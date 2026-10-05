from opik import track

from . import glossary, llm
from .corpus import Document

_CLIENT, _IS_CANNED = llm.get_client()

# The v1 prompt: what a first-draft RAG app actually ships with. No refusal instruction,
# so the model fills gaps from pretraining. Module 4 measures that, then swaps in GROUNDED.
SYSTEM = (
    "You are a helpful assistant answering questions about the Opik observability "
    "platform. Use the context below to answer the user's question."
)

GROUNDED = (
    "You are a helpful assistant answering questions about the Opik observability "
    "platform. Answer using only the context provided. If the context does not contain "
    "the answer, say so plainly instead of guessing."
)


@track(type="general")
def retrieve(question: str, k: int = 3) -> list[dict]:
    from .corpus import search

    return [{"doc_id": d.doc_id, "title": d.title, "text": d.text} for d in search(question, k=k)]


@track(type="llm")
def rerank(question: str, candidates: list[dict]) -> list[dict]:
    """A second model call purely to reorder candidates. Off by default — Module 2 turns it
    on to watch where latency and cost actually concentrate."""
    listing = "\n".join(f"{i}. {c['title']}" for i, c in enumerate(candidates))
    answer = llm.complete(
        _CLIENT,
        [
            {"role": "system", "content": "Reply with the indices, most relevant first, comma separated."},
            {"role": "user", "content": f"Question: {question}\n\n{listing}"},
        ],
    )
    order = []
    for token in answer.replace(".", ",").split(","):
        token = token.strip()
        if token.isdigit() and int(token) < len(candidates) and int(token) not in order:
            order.append(int(token))
    order += [i for i in range(len(candidates)) if i not in order]
    return [candidates[i] for i in order]


@track(type="tool")
def lookup_glossary(question: str) -> dict[str, str]:
    return {term: glossary.lookup(term) for term in glossary.find_terms(question)}


@track(type="llm")
def generate_answer(
    question: str,
    context: list[dict],
    definitions: dict[str, str],
    system: str = SYSTEM,
) -> str:
    context_block = "\n\n".join(f"[{c['doc_id']}] {c['text']}" for c in context)
    if definitions:
        context_block += "\n\nGlossary:\n" + "\n".join(f"- {k}: {v}" for k, v in definitions.items())
    return llm.complete(
        _CLIENT,
        [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Context:\n{context_block}\n\nQuestion: {question}"},
        ],
    )


@track(name="rag_agent")
def answer_question(question: str, use_reranker: bool = False, grounded: bool = False) -> dict:
    context = retrieve(question)
    if use_reranker:
        context = rerank(question, context)
    definitions = lookup_glossary(question)
    answer = generate_answer(question, context, definitions, GROUNDED if grounded else SYSTEM)
    return {
        "answer": answer,
        "context": [c["text"] for c in context],
        "doc_ids": [c["doc_id"] for c in context],
    }
