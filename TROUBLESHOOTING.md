# Troubleshooting

Ordered by how often it bites.

---

## "I logged a trace and it isn't there"

Expected, briefly. The SDK batches: span and trace messages flush when the batch fills (1000
messages) **or** when a 2.0 second timer expires — whichever comes first. Then the server
buffers again before writing.

So *logged* and *queryable* are not the same instant.

```python
opik.flush_tracker()   # push what's buffered
```

…then poll rather than sleeping a fixed amount:

```python
import time

from opik.rest_api.core.api_error import ApiError

deadline = time.time() + 60
found = []
while time.time() < deadline:
    try:
        found = client.search_traces(project_name=PROJECT, max_results=50)
    except ApiError as exc:
        if exc.status_code != 404:  # 404: the project doesn't exist until its first trace lands
            raise
    if found:
        break
    time.sleep(3)
```

A short script that exits without flushing loses whatever was still buffered.

---

## My trace has no token counts or cost

`@track` alone does not record them. The **client wrapper** does:

```python
from opik.integrations.openai import track_openai
client = track_openai(OpenAI())
```

Cost lands on the innermost LLM span — the one the integration creates — not on the function you
decorated. A trace's cost is the sum of its spans, and the trace-level rollup is computed after
the spans land, so reading it immediately can return 0.

---

## My online scoring rule isn't producing scores

Almost always the provider key. **The judge runs on the Opik server**, so your notebook's
`OPENAI_API_KEY` is invisible to it.

Check the rule's logs (UI, or `get_evaluator_logs_by_id`). This is what a missing key looks like:

```
[INFO]  Evaluating traceId '...' sampled by rule 'grounding-check'
[INFO]  Sending traceId '...' to LLM: model='gpt-4o-mini'
[ERROR] API key not configured for LLM. provider='openai', model='gpt-4o-mini'
```

Fix: **Configuration → AI Providers → add OpenAI** in the UI.

Note that new workspaces already list Opik's own free provider there. That doesn't cover this
workshop: its judge calls an OpenAI model, so OpenAI has to be added specifically.

If the key is set and scores still look wrong, check the **variable mapping** next. Each
`{{placeholder}}` names a path into the trace, and a wrong path grades an empty string —
silently, with confident-sounding reasons. Our agent returns context in its *output*, so:

```python
variables={"context": "output.context",     # not input.context
           "question": "input.question",
           "answer": "output.answer"}
```

If mapping is fiddly, put `{{trace}}` in the prompt instead. **Agent as a Judge** reads the
trace itself with tools and needs no mapping at all.

---

## Generated traces don't show up

Check the SDK's log output first: a problem with a batch is reported there rather than raised in
your code, so a script can finish "successfully" with nothing ingested. Two usual causes:

- **The history is too old for Opik Cloud.** Trace ids are UUIDv7s — their leading bits are a
  timestamp, which keeps them sortable by time — and Opik Cloud, built for live telemetry,
  expects them to be recent. Keep generated data within the last 23 hours (the default). A
  self-hosted Opik doesn't apply that expectation by default, so `--days 90` works there.
- **The account's usage allowance is used up** — see the next section.

---

## Nothing arrives at all, and the log mentions the account's limit

Free Opik Cloud accounts include a usage allowance, and every span counts towards it. Once it is
used up, new traces are not accepted — the SDK logs the reason, and notebooks that wait for
traces simply keep waiting.

The workshop itself uses a small part of it. The one thing that adds up quickly is generating
data: each generated trace carries 5-7 spans, so avoid re-running the generator more than you
need to.

---

## `Connection refused` on localhost:8123

ClickHouse isn't published to your host. Start Opik with the flag:

```bash
./opik.sh --port-mapping
```

Without it the port only exists inside the Docker network. If Opik is already running, stop it
with `./opik.sh --stop` and start it again with the flag.

Still refused? Check which host port ClickHouse is published on, and set `CLICKHOUSE_PORT` if
it isn't 8123:

```bash
docker ps --format '{{.Names}}\t{{.Ports}}' | grep clickhouse
```

---

## `Ingestion rate limited, retrying in N seconds`

Like any SaaS, Opik Cloud paces how fast a workspace can write. This is not an error — the SDK
backs off and retries, and everything lands; it just takes a little longer. You are most likely
to see it when generating data, since each generated trace is written twice (start and end) plus
its spans.

---

## `Project name: … not found` right after logging

A project is created when its first trace is ingested. Query it before that happens — the first
thing a fresh notebook does after logging — and you get a 404 rather than an empty list.
Treat the 404 as "nothing has landed yet" and keep polling. The notebooks' `wait_for` helpers
do exactly that.

---

## Searches are slow, or pause for a minute

Opik Cloud also paces searches. A loop that calls `search_spans` once per trace reaches that
quickly, and the SDK then waits before carrying on.

Ask once instead: filter the spans you want across the whole project, for example

```python
client.search_spans(project_name=PROJECT, filter_string="total_estimated_cost > 0")
client.search_spans(project_name=PROJECT, filter_string='name = "rerank"')
```

When polling, keep the interval at 3-5 seconds rather than 1.

---

## Queries are slow, or read the whole table

Check the `WHERE` clause. `traces` is ordered by `(workspace_id, project_id, id)` and `spans` by
`(workspace_id, project_id, trace_id, parent_span_id, id)`. Those leading columns are the
primary key — filtering on them prunes to a small range of granules; omitting them reads
everything.

Also add `source = 'sdk'` when you mean production traffic. Traces from experiments, the
playground and optimization runs share the table, and will otherwise be folded into your
production latency numbers.

---

## Summing span durations gives a number that's too big

A span tree double-counts if you sum it naively: `generate_answer` wraps
`chat_completion_create` and both carry roughly the same duration.

Attribute time over **leaf spans only** — spans that are not any other span's parent. The tree is
stored flat (parentage is just a column), so that's an anti-join rather than a recursive walk.
See `sql/04_where_time_goes.sql`.

---

## The agent refuses to answer things it should know

You're on the grounded prompt. `answer_question(question, grounded=True)` uses the hardened
system prompt; the default is deliberately the weaker v1 so Module 4 has something to catch.

---

## No OpenAI key at all

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

---

## Still stuck?

- Ask in the Comet community Slack, channel `#support-issues`: https://chat.comet.com
- If it looks like a bug in Opik itself, open an issue: https://github.com/comet-ml/opik/issues
