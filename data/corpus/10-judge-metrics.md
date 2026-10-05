# LLM-as-a-judge metrics in the SDK

The evaluation SDK provides judge metrics you can call directly, including Hallucination,
AnswerRelevance, ContextPrecision, ContextRecall, Moderation, Usefulness and G-Eval.

The Hallucination metric takes an input, an output and a context, and uses another LLM to
decide whether the output is supported by the context. It returns 1.0 when hallucination is
detected and 0.0 when it is not — so for this metric a higher score is worse. It also
returns a reason explaining the verdict.
