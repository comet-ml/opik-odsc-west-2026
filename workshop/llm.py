import os
import textwrap

MODEL = os.environ.get("WORKSHOP_MODEL", "gpt-4o-mini")


def _canned(messages: list[dict]) -> str:
    """Offline stand-in so the tracing modules work without a provider key.

    It answers from the prompt's context block, which means it never hallucinates —
    so Module 4's evaluation story needs a real key to be meaningful.
    """
    prompt = messages[-1]["content"]
    context = prompt.split("Context:", 1)[-1].split("Question:", 1)[0].strip()
    first = textwrap.shorten(context.replace("\n", " "), width=280, placeholder=" ...")
    return f"[canned] {first}" if first else "[canned] No context was retrieved."


def get_client():
    """Returns (client, is_canned). The client is wrapped so token counts and cost land
    on every LLM span — a bare @track would not capture those."""
    if os.environ.get("USE_CANNED_RESPONSES") == "1" or not os.environ.get("OPENAI_API_KEY"):
        return None, True

    from openai import OpenAI
    from opik.integrations.openai import track_openai

    return track_openai(OpenAI()), False


def complete(client, messages: list[dict], temperature: float = 0.0) -> str:
    if client is None:
        return _canned(messages)
    reply = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
    )
    return reply.choices[0].message.content
