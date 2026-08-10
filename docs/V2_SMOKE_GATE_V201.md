# POLIS v2.0.1 compatibility gate

Confirmatory collection is blocked until one live strict structured-action request succeeds for every endpoint in the v2.0.1 seven-model panel.

The gate uses the production OpenRouter adapter and is not part of the research dataset. A successful gate verifies interface compatibility only. It does not test or tune any research hypothesis.

If any endpoint fails, paid confirmatory collection remains blocked and any further endpoint replacement requires another protocol version increment and a new study fingerprint before the gate is repeated.
