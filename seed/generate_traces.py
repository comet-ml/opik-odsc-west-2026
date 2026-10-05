"""Generate a realistic volume of traces for the Module 3 analytics exercise.

    python seed/generate_traces.py --traces 500

Traces are spread over the last 23 hours by default.

Why recent: Opik's trace ids are UUIDv7s, whose leading bits are a timestamp — that is what
makes them sortable by time. Opik Cloud is built for live telemetry and expects ids to be
recent, so the generator doesn't backdate further than a day there. A self-hosted Opik doesn't
apply that expectation by default, so `--days N` gives you weeks of history locally.

If generated traces don't show up, check the SDK's log output: a problem with a batch is
reported there rather than raised in your code.

Keep volumes modest on a free Opik Cloud account: every span counts towards its usage
allowance, and each generated trace carries 5-7 spans.

Timestamps are fixed when traces are written, so data generated weeks before you need it will
look weeks old, and a "last 24h" filter will come back empty. Generate close to when you need it.
"""

import argparse
import datetime as dt
import random

import opik
from opik import id_helpers
from opik.config import OpikConfig

MODELS = [
    # name, provider, weight, latency_ms (median, sigma), prompt_tokens, completion_tokens
    ("gpt-4o-mini", "openai", 0.60, (900, 0.45), (400, 900), (80, 260)),
    ("gpt-4o", "openai", 0.25, (1900, 0.40), (500, 1200), (120, 400)),
    ("claude-sonnet-5", "anthropic", 0.15, (1600, 0.38), (450, 1100), (100, 350)),
]

TENANTS = ["acme", "globex", "initech", "umbrella"]
# A planted signal for the Module 3 exercise: one tenant fails noticeably more often, so
# "which tenant has the highest error rate?" has a real answer rather than noise.
TENANT_ERROR_MULTIPLIER = {"umbrella": 3.0}
QUESTIONS = [
    "How does the SDK batch spans before sending them?",
    "What engine stores traces in ClickHouse?",
    "Why would I lower an online rule's sampling rate?",
    "What does wait_for_async_insert guarantee?",
    "How do I attach metadata to a trace?",
    "What is Agent as a Judge?",
]

ERRORS = [
    ("RateLimitError", "429 Too Many Requests"),
    ("APITimeoutError", "Request timed out after 30s"),
    ("ContextWindowExceeded", "Prompt exceeds model context window"),
]


def lognormal_ms(median, sigma):
    return max(1.0, random.lognormvariate(0, sigma) * median)


def pick_model():
    r = random.random()
    cumulative = 0.0
    for entry in MODELS:
        cumulative += entry[2]
        if r <= cumulative:
            return entry
    return MODELS[-1]


def make_trace(client, project, started_at, error_rate):
    name, provider, _, (median, sigma), prompt_range, completion_range = pick_model()
    tenant = random.choice(TENANTS)
    failed = random.random() < error_rate * TENANT_ERROR_MULTIPLIER.get(tenant, 1.0)

    retrieve_ms = random.uniform(0.05, 3.0)
    use_reranker = random.random() < 0.35
    rerank_ms = lognormal_ms(600, 0.3) if use_reranker else 0.0
    generate_ms = lognormal_ms(median, sigma)
    tool_ms = random.uniform(0.05, 0.4)
    total_ms = retrieve_ms + rerank_ms + tool_ms + generate_ms

    trace_id = id_helpers.generate_id(timestamp=started_at)
    question = random.choice(QUESTIONS)
    error_info = None
    if failed:
        exc, msg = random.choice(ERRORS)
        error_info = {"exception_type": exc, "message": msg, "traceback": f"{exc}: {msg}"}

    # Two writes per trace: one when execution starts, one when it ends. Both carry the same
    # id, which is why the table is a ReplacingMergeTree. The second write must be a FULL
    # payload — it replaces the first rather than merging into it, so anything it omits
    # (tags, metadata) is lost once the rows merge.
    tags = [f"tenant:{tenant}", "seeded"]
    metadata = {"corpus_version": "v1", "reranker": use_reranker}
    client.trace(
        id=trace_id,
        name="rag_agent",
        project_name=project,
        start_time=started_at,
        input={"question": question},
        tags=tags,
        metadata=metadata,
    )
    client.trace(
        id=trace_id,
        name="rag_agent",
        project_name=project,
        start_time=started_at,
        end_time=started_at + dt.timedelta(milliseconds=total_ms),
        input={"question": question},
        output=None if failed else {"answer": "(seeded)"},
        error_info=error_info,
        tags=tags,
        metadata=metadata,
    )

    def span(span_name, span_type, begin, duration_ms, parent, **kwargs):
        span_id = id_helpers.generate_id(timestamp=begin)
        client.span(
            trace_id=trace_id,
            id=span_id,
            parent_span_id=parent,
            project_name=project,
            name=span_name,
            type=span_type,
            start_time=begin,
            end_time=begin + dt.timedelta(milliseconds=duration_ms),
            **kwargs,
        )
        return span_id

    def at(offset_ms):
        return started_at + dt.timedelta(milliseconds=offset_ms)

    # A root span sharing the trace's name, mirroring what @track emits.
    root = span("rag_agent", "general", at(0), total_ms, None, input={"question": question})

    offset = 0.0
    span("retrieve", "general", at(offset), retrieve_ms, root, output={"k": 3})
    offset += retrieve_ms

    if use_reranker:
        # An LLM step wraps the provider call; the integration adds the inner span that
        # actually carries usage and cost. Same shape the live OpenAI wrapper produces.
        rerank_parent = span("rerank", "llm", at(offset), rerank_ms, root)
        span(
            "chat_completion_create", "llm", at(offset + 0.2), rerank_ms - 0.4, rerank_parent,
            model=name, provider=provider,
            usage={"prompt_tokens": 60, "completion_tokens": 8, "total_tokens": 68},
        )
        offset += rerank_ms

    span("lookup_glossary", "tool", at(offset), tool_ms, root, output={"hits": random.randint(0, 2)})
    offset += tool_ms

    prompt_tokens = random.randint(*prompt_range)
    completion_tokens = 0 if failed else random.randint(*completion_range)
    generate_parent = span("generate_answer", "llm", at(offset), generate_ms, root)
    span(
        "chat_completion_create", "llm", at(offset + 0.2), generate_ms - 0.4, generate_parent,
        model=name, provider=provider,
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
        error_info=error_info,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--traces", type=int, default=500)
    parser.add_argument("--project", default="odsc-analytics")
    parser.add_argument("--hours", type=float, default=23.0, help="spread traces over the last N hours")
    parser.add_argument("--days", type=float, default=None, help="overrides --hours; for self-hosted Opik")
    parser.add_argument("--workspace", default=None, help="target workspace (default: your configured one)")
    parser.add_argument("--error-rate", type=float, default=0.04)
    args = parser.parse_args()

    span_hours = args.days * 24 if args.days else args.hours
    if span_hours > 23.5 and "comet.com" in OpikConfig().url_override:
        print(
            f"Note: {span_hours:.0f}h of history is more than Opik Cloud accepts for new traces.\n"
            "      Use a self-hosted Opik for longer histories (see SETUP.md).\n"
        )

    client = (
        opik.Opik(workspace=args.workspace, project_name=args.project)
        if args.workspace
        else opik.Opik(project_name=args.project)
    )
    now = dt.datetime.now(dt.timezone.utc)
    earliest = now - dt.timedelta(hours=span_hours)

    print(f"seeding {args.traces} traces into '{args.project}' over the last {span_hours:.1f}h")
    for i in range(args.traces):
        offset = random.random() ** 0.7  # weight recent
        started = earliest + (now - earliest) * offset
        make_trace(client, args.project, started, args.error_rate)
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{args.traces}")

    print("flushing...")
    opik.flush_tracker()
    print("done. Verify with:  python seed/verify_seed.py --project " + args.project)


if __name__ == "__main__":
    main()
