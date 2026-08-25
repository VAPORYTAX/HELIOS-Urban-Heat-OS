# FortyGuard Provider Contract Used by HELIOS

Verified against current FortyGuard v1 documentation in August 2026.

## Authentication
Header: `api-key`

## Base URL
`https://api.fortyguard.com`

## Async lifecycle
1. Submit operation.
2. Read `data.activity_id`.
3. Poll `GET /v1/status/{activity_id}`.
4. Accept terminal states explicitly.
5. Do not fabricate a result when an operation fails or access is unavailable.

## Encoded endpoints
- POST `/v1/heatmap`
- POST `/v1/streetview`
- POST `/v1/satellite`
- POST `/v1/env_params`
- GET `/v1/status/{activity_id}`

## Heatmap
- GeoJSON FeatureCollection Polygon AOI
- 60 / 80 / 100m granularity
- analytics: tcm, time_of_measure, exceedance, persistence
- documented history begins 2019-01-01
- documented forecast reach: up to 12 hours ahead
- current regional coverage: United States

## Satellite
- nested `sat: {latitude, longitude}`
- matching `date_time`
- 60 / 80 / 100m granularity
- Premium-only in the current provider documentation

## Environmental Parameters
- latitude / longitude
- input `temperature`
- matching `date_time`
- Basic/Startup currently allow up to 3 selected parameters; Premium allows full access

## Plan-aware operation
Satellite and street-view segmentation are currently Premium-only according to provider docs.
HELIOS reports access failure transparently rather than silently substituting synthetic content.
