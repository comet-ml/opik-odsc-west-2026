# Provider integrations

Wrapping an LLM client adds automatic tracing of model calls. For OpenAI use
`track_openai(client)` from `opik.integrations.openai`; for Anthropic use
`track_anthropic(client)` from `opik.integrations.anthropic`. The wrapper is what records
token counts, estimated cost and the model name on each LLM span — a plain `@track`
decorator alone does not produce those. Opik ships integrations for many frameworks,
including LangChain, LlamaIndex, Haystack, CrewAI, DSPy and Bedrock.
