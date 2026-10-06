# Pre-workshop setup

Ideally before the session. We start with a short guided setup, but arriving ready means you
spend that time practising instead.

If something doesn't work, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md), or ask in the Comet
community Slack, channel `#support-issues`: https://chat.comet.com

---

## Minimum — everyone

### 1. An Opik account (free, no card)

Sign up at https://www.comet.com/site/products/opik/ and keep your API key handy.
`opik.configure()` in the first notebook will prompt for it.

### 2. An OpenAI API key

https://platform.openai.com/. The examples use an inexpensive model (`gpt-4o-mini`) and keep
usage light, so a small amount of credit is enough — but API usage is billed to your own
account.

### 3. Open Module 1 in Colab and run the first cell

Use the Colab badge in the [README](README.md). If it prints a trace URL, you are ready.

That's it. Everything below is optional.

---

## Also worth doing: the AI provider key **inside Opik**

Module 4 creates an online scoring rule — an LLM-as-a-judge that grades production traces.

**The judge runs on the Opik server, not in your notebook.** The `OPENAI_API_KEY` you set for
the notebook is not visible to it, so Opik needs its own copy.

In the Opik UI: **Configuration → AI Providers → add OpenAI**.

Skip this and the rule will be created successfully, fire on every trace, and score nothing.
Your code raises no error; the traces simply never get a score. Module 4's notebook sets it up
for you if it's missing, but doing it beforehand saves a minute.

---

## Keep your keys out of the notebooks

The notebooks never ask you to paste a key into a cell. `opik.configure()` and the OpenAI prompt
both read keys without echoing them and keep them out of the saved notebook. Keep it that way:
no `os.environ["OPENAI_API_KEY"] = "..."` in a cell, and clear outputs before sharing a
notebook.

## Optional: run locally instead of Colab

Needs Python 3.10 or newer and git.

```bash
git clone https://github.com/comet-ml/opik-odsc-west-2026.git
cd opik-odsc-west-2026
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
opik configure
export OPENAI_API_KEY="<your-openai-api-key>"
python scripts/check_setup.py
jupyter lab
```

`check_setup.py` prints PASS/FAIL per requirement. Run it before the session. Then open the
notebooks from the `notebooks/` folder.

---

## Optional: self-host Opik (for Module 3's SQL)

Module 3 looks at how traces are stored and queried. Following along *at the SQL level* needs a
local Opik instance — a Docker Compose stack of ClickHouse, MySQL, Redis, ZooKeeper, MinIO,
plus backend and frontend.

You do not need this to follow Module 3. The notebook answers the same questions through the
SDK, which works on Colab.

```bash
git clone https://github.com/comet-ml/opik.git
cd opik
./opik.sh --port-mapping
```

**`--port-mapping` is required.** Without it ClickHouse is not published to your host and the
Module 3 queries cannot connect — port publishing lives in an override compose file that only
that flag applies.

Then point the SDK and the notebooks at it, in the terminal you start Jupyter from:

```bash
export OPIK_URL_OVERRIDE=http://localhost:5173/api/
```

No Opik API key and no `opik configure` needed: the notebooks see this variable and connect to
your local Opik instead of Opik Cloud.

| Service | Where |
|---|---|
| Opik UI | http://localhost:5173 |
| ClickHouse HTTP | localhost:8123 |
| ClickHouse credentials | database `opik`, user `opik`, password `opik` |

`opik` / `opik` are the default credentials of the local Docker install — nothing secret, and
not used by Opik Cloud.

**Pull the images the day before.** A first-time pull takes minutes and there is no room for
that during the session.

---

## Optional: your own trace volume for Module 3

```bash
python seed/generate_traces.py --traces 500
```

Module 3 runs exactly this in-session, so you don't need to do it beforehand.

Traces are spread over the last 23 hours. Opik's trace ids are UUIDv7s — their leading bits are
a timestamp, which keeps them sortable by time — and Opik Cloud, being built for live telemetry,
expects them to be recent. A self-hosted Opik doesn't apply that expectation by default, so
`--days 90` works there.

Keep volumes modest on a free account: every span counts towards your usage allowance, and each
generated trace carries 5-7 spans. Bulk writes are also paced, so the SDK may back off and retry;
everything lands, just not all at once.

---

## No provider key?

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
