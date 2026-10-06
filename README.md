# Production-Grade Agent & LLM Observability with Opik

Companion repository for the ODSC AI West 2026 workshop.

**Session:** Production-Grade Agent & LLM Observability: Real-Time Analytics and Evaluation at Scale with Opik
**Presenter:** Andrés Cruz, Principal Software Engineer, Comet

---

## Start here

The fastest path is Google Colab — no local Python, no Docker, nothing to install.

| Module | Notebook | |
|---|---|---|
| 1 — Why LLM observability is different | `01_first_trace.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/comet-ml/opik-odsc-west-2026/blob/main/notebooks/01_first_trace.ipynb) |
| 2 — Instrumenting a multi-step agent | `02_agent_tracing.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/comet-ml/opik-odsc-west-2026/blob/main/notebooks/02_agent_tracing.ipynb) |
| 3 — Ingestion & real-time analytics | `03_scale_and_analytics.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/comet-ml/opik-odsc-west-2026/blob/main/notebooks/03_scale_and_analytics.ipynb) |
| 4 — Evaluation & online scoring | `04_evaluation_and_online_scoring.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/comet-ml/opik-odsc-west-2026/blob/main/notebooks/04_evaluation_and_online_scoring.ipynb) |

You need a free [Opik Cloud](https://www.comet.com/site/products/opik/) account and an OpenAI
API key. The examples use an inexpensive model and keep usage light, so the cost is small —
but API usage is billed to your own OpenAI account.

See [SETUP.md](SETUP.md) for the full pre-workshop checklist, and
[TROUBLESHOOTING.md](TROUBLESHOOTING.md) if something misbehaves.

## Running locally instead

Needs Python 3.10 or newer and git.

```bash
git clone https://github.com/comet-ml/opik-odsc-west-2026.git
cd opik-odsc-west-2026
pip install -r requirements.txt
opik configure
export OPENAI_API_KEY="<your-openai-api-key>"
python scripts/check_setup.py
jupyter lab
```

`check_setup.py` prints a PASS/FAIL line per requirement. Run it before the session.

## What's in here

```
workshop/      the instrumented RAG agent used throughout
data/corpus/   13 short documents the agent answers questions over
data/          eval_dataset.jsonl — 28 questions with reference answers
notebooks/     one notebook per module, each ending with a Your turn exercise
seed/          generates trace volume for the Module 3 analytics exercise
sql/           the ClickHouse queries from Module 3
scripts/       setup verification
```

## No API key?

Press **Enter** when a notebook asks for your OpenAI key — on Colab, that's all it takes. Running
locally, you can switch canned mode on for every notebook instead:

```bash
export USE_CANNED_RESPONSES=1
```

You can still follow the tracing mechanics: decorators, nesting and span trees in Modules 1
and 2, and all of Module 3 on generated data. The agent answers from its retrieved context
instead of calling a model, so your own traces carry no token cost or model latency. The
model cells in Module 1 (the call itself, and reading its trace back) and all of Module 4
need a real key.

## Links

- Opik — https://github.com/comet-ml/opik (Apache-2.0)
- Opik docs — https://www.comet.com/docs/opik/

## Questions, bugs, contributions

- **Ask** — Comet community Slack, channel `#support-issues`: https://chat.comet.com
- **Report a bug or request a feature** — https://github.com/comet-ml/opik/issues
- **Contribute** — pull requests welcome: https://github.com/comet-ml/opik/pulls
  (start with the Opik repo's `CONTRIBUTING.md`)

## License

Apache-2.0 — see [LICENSE](LICENSE). Copyright Comet ML, Inc.
