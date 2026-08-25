# HELIOS ContextForge
ContextForge is the evidence compiler between HELIOS deterministic engines and Gemma 4.

Principles:
- never dump the database into the model
- rank evidence by decision utility
- preserve truth categories
- keep fixture/modelled/derived distinctions explicit
- version prompt components
- hash the exact context packet
- enforce context budgets
- numeric/spatial truth remains owned by HELIOS engines

Context Utility Score uses relevance, confidence, spatial match, freshness, and decision impact.

Prompt bundle v1:
- identity
- truth policy
- tool policy
- uncertainty policy
- output contract

Every packet stores task, mode, user intent, context hash, prompt bundle version, token budget, estimated tokens, and ranked evidence references.
