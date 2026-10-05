GLOSSARY = {
    "span": "A single unit of work inside a trace, with its own inputs, outputs and timing.",
    "trace": "The full record of one end-to-end execution, containing a tree of spans.",
    "feedback score": "A named numeric score attached to a trace or span, from a human, the SDK or a judge.",
    "experiment": "The result of running a task over a dataset and scoring it.",
    "dataset": "A fixed collection of items used to evaluate a task reproducibly.",
    "sampling rate": "The share of production traces an online rule scores.",
}


def lookup(term: str) -> str | None:
    return GLOSSARY.get(term.strip().lower())


def find_terms(text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in GLOSSARY if term in lowered]
