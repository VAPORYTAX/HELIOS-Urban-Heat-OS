import asyncio
import hashlib
import json
import time
from typing import Any

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings, get_settings
from app.fortyguard.cache import ResponseCache
from app.fortyguard.exceptions import (
    FortyGuardAccessError,
    FortyGuardConfigurationError,
    FortyGuardRequestError,
    FortyGuardTimeoutError,
)
from app.fortyguard.schemas import (
    ActivityResult,
    ActivitySubmission,
    EnvironmentalParametersRequest,
    HeatmapRequest,
    SatelliteRequest,
    StreetViewRequest,
)

_RETRYABLE = (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError)

class FortyGuardClient:
    def __init__(self, settings: Settings | None = None, transport=None):
        self.settings = settings or get_settings()
        self.cache = ResponseCache(ttl=self.settings.fortyguard_cache_ttl_seconds)
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        if not self.settings.fortyguard_api_key:
            raise FortyGuardConfigurationError(
                "FORTYGUARD_API_KEY is not configured. Add it to .env."
            )
        return {
            "api-key": self.settings.fortyguard_api_key,
            "accept": "application/json",
            "content-type": "application/json",
            "user-agent": "HELIOS/0.1",
        }

    def _url(self, path: str) -> str:
        return f"{self.settings.fortyguard_base_url.rstrip('/')}{path}"

    @staticmethod
    def _cache_key(method: str, path: str, payload: dict | None) -> str:
        body = json.dumps(payload or {}, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(body.encode()).hexdigest()
        return f"{method}:{path}:{digest}"

    async def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        key = self._cache_key(method, path, payload)
        if method == "GET":
            cached = self.cache.get(key)
            if cached is not None:
                return cached

        timeout = httpx.Timeout(self.settings.fortyguard_timeout_seconds)
        async with httpx.AsyncClient(
            timeout=timeout,
            transport=self._transport,
            follow_redirects=True,
        ) as client:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self.settings.fortyguard_max_retries),
                wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
                retry=retry_if_exception_type(_RETRYABLE),
                reraise=True,
            ):
                with attempt:
                    response = await client.request(
                        method,
                        self._url(path),
                        headers=self._headers(),
                        json=payload if method != "GET" else None,
                    )

        try:
            data = response.json()
        except ValueError:
            data = {"raw_text": response.text}

        if response.status_code in (401, 403):
            raise FortyGuardAccessError(
                f"FortyGuard denied access ({response.status_code}). "
                "Check API key and plan entitlement."
            )
        if response.status_code >= 400:
            raise FortyGuardRequestError(
                f"FortyGuard request failed ({response.status_code})",
                status_code=response.status_code,
                payload=data,
            )

        if isinstance(data, dict) and data.get("error") is True:
            raise FortyGuardRequestError(
                data.get("message", "FortyGuard returned an error response"),
                status_code=data.get("status_code"),
                payload=data,
            )

        if method == "GET":
            self.cache.set(key, data)
        return data

    @staticmethod
    def _activity_id(data: dict) -> str:
        activity_id = ((data.get("data") or {}).get("activity_id"))
        if not activity_id:
            raise FortyGuardRequestError("FortyGuard response did not contain activity_id", payload=data)
        return str(activity_id)

    async def submit_heatmap(self, request: HeatmapRequest) -> ActivitySubmission:
        data = await self._request("POST", "/v1/heatmap", request.model_dump(mode="json", exclude_none=True))
        return ActivitySubmission(activity_id=self._activity_id(data), operation="heatmap")

    async def submit_streetview(self, request: StreetViewRequest) -> ActivitySubmission:
        data = await self._request("POST", "/v1/streetview", request.model_dump(mode="json", exclude_none=True))
        return ActivitySubmission(activity_id=self._activity_id(data), operation="streetview")

    async def submit_satellite(self, request: SatelliteRequest) -> ActivitySubmission:
        data = await self._request("POST", "/v1/satellite", request.model_dump(mode="json", exclude_none=True))
        return ActivitySubmission(activity_id=self._activity_id(data), operation="satellite")

    async def submit_environmental_parameters(
        self, request: EnvironmentalParametersRequest
    ) -> ActivitySubmission:
        data = await self._request("POST", "/v1/env_params", request.model_dump(mode="json", exclude_none=True))
        return ActivitySubmission(activity_id=self._activity_id(data), operation="env_params")

    async def get_activity(self, activity_id: str, *, bypass_cache: bool = False) -> ActivityResult:
        path = f"/v1/status/{activity_id}"
        if bypass_cache:
            # POST-like cache key is intentionally not used; status polling must be fresh.
            timeout = httpx.Timeout(self.settings.fortyguard_timeout_seconds)
            async with httpx.AsyncClient(
                timeout=timeout, transport=self._transport, follow_redirects=True
            ) as client:
                response = await client.get(self._url(path), headers=self._headers())
            try:
                data = response.json()
            except ValueError:
                data = {"raw_text": response.text}
            if response.status_code in (401, 403):
                raise FortyGuardAccessError("FortyGuard denied status access.")
            if response.status_code >= 400 or data.get("error") is True:
                raise FortyGuardRequestError(
                    data.get("message", f"Status request failed ({response.status_code})"),
                    response.status_code,
                    data,
                )
        else:
            data = await self._request("GET", path)

        payload = data.get("data") or {}
        return ActivityResult(
            activity_id=str(payload.get("activity_id") or activity_id),
            status=str(payload.get("status") or data.get("message") or "Unknown"),
            result=payload.get("result"),
            raw=data,
        )

    async def wait_for_activity(self, activity_id: str) -> ActivityResult:
        deadline = time.monotonic() + self.settings.fortyguard_max_poll_seconds
        terminal = {"completed", "failed", "cancelled", "canceled"}

        while time.monotonic() < deadline:
            activity = await self.get_activity(activity_id, bypass_cache=True)
            if activity.status.lower() in terminal:
                return activity
            await asyncio.sleep(self.settings.fortyguard_poll_interval_seconds)

        raise FortyGuardTimeoutError(
            f"Activity {activity_id} did not finish within "
            f"{self.settings.fortyguard_max_poll_seconds:.0f}s."
        )
