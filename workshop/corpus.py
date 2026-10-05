import pathlib
import re
from dataclasses import dataclass

CORPUS_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "corpus"

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "how", "i", "in", "is", "it", "its", "of", "on", "or", "that", "the", "to", "what",
    "when", "which", "with", "you", "your",
}


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str


def _tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9_]+", text.lower()) if t not in _STOPWORDS]


def load_corpus() -> list[Document]:
    docs = []
    for path in sorted(CORPUS_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8").strip()
        title = raw.splitlines()[0].lstrip("# ").strip()
        docs.append(Document(doc_id=path.stem, title=title, text=raw))
    return docs


_CORPUS = load_corpus()
_INDEX = {doc.doc_id: set(_tokenize(doc.text)) for doc in _CORPUS}


def search(question: str, k: int = 3) -> list[Document]:
    """Keyword overlap retrieval. Deliberately naive — a real vector store would go here,
    and the workshop's point is that the observability story is identical either way."""
    query_terms = set(_tokenize(question))
    scored = []
    for doc in _CORPUS:
        overlap = len(query_terms & _INDEX[doc.doc_id])
        if overlap:
            scored.append((overlap / len(query_terms or {""}), doc))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [doc for _, doc in scored[:k]]
