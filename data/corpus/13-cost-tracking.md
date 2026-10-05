# Token usage and cost

Each LLM span carries a usage map of token counts and an estimated cost. Cost is derived
from the recorded model and provider, so the provider has to be known. When you wrap an
OpenAI-compatible client that is actually pointed at another service — Together, OpenRouter,
vLLM, DeepSeek and so on — pass `provider=` to `track_openai` so cost is attributed to the
real provider instead of the base URL host. Providers Opik recognises for cost tracking
include openai, anthropic, google_vertexai, google_ai, groq, bedrock and anthropic_vertexai.
