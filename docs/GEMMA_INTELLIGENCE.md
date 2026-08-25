# HELIOS Gemma 4 Intelligence Gateway

Gemma is a reasoning/orchestration layer, not the owner of numerical truth.

## Default model routing
- deep/default: `gemma-4-26B-A4B-it`
- fast/fallback: `gemma-4-12B-it`

Environment:
- `GEMMA_BASE_URL=http://127.0.0.1:1235/v1`
- `GEMMA_MODEL=gemma-4-26B-A4B-it`
- `GEMMA_FALLBACK_MODEL=gemma-4-12B-it`
- `GEMMA_ENABLED=true`

Any OpenAI-compatible local runtime may be used.

## Safety architecture
1. ContextForge builds evidence.
2. Gemma receives only a bounded context packet.
3. Gemma returns structured JSON.
4. Pydantic validates the schema.
5. Hallucination Firewall checks evidence refs and numeric claims.
6. Quality gates cannot be overridden by the model.
7. Invalid or unavailable model output falls back to deterministic HELIOS output.

## Thinking
Thinking is enabled for deep planning/review tasks and disabled for operational mode by default.
Hidden reasoning is not stored or returned to the user.

## Numeric firewall
Gemma may only emit numeric claims using explicit authoritative keys already present in the context packet.
Mismatched or invented numbers invalidate the model response.
