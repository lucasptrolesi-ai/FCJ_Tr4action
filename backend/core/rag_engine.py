from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from core.config import (
    KNOWLEDGE_PATH,
    EMBEDDINGS_PATH,
    METADATA_PATH,
    RAG_EMBEDDING_MODEL,
)


@dataclass
class KnowledgeDoc:
    id: str
    step: str
    title: str
    text: str


class RAGEngine:
    """
    Engine simples de RAG em memória.
    Carrega documentos + embeddings e permite buscar contexto por pergunta.
    """

    def __init__(self) -> None:
        self.model = SentenceTransformer(RAG_EMBEDDING_MODEL)
        self.docs: List[KnowledgeDoc] = []
        self.embeddings: Optional[np.ndarray] = None

        self._load_from_disk()

    # ---------- Persistência ----------
    def _load_from_disk(self) -> None:
        if KNOWLEDGE_PATH.exists():
            with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.docs = [KnowledgeDoc(**d) for d in raw]

        if EMBEDDINGS_PATH.exists():
            self.embeddings = np.load(EMBEDDINGS_PATH)

    def _save_to_disk(self) -> None:
        with open(KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
            json.dump([d.__dict__ for d in self.docs], f, ensure_ascii=False, indent=2)

        if self.embeddings is not None:
            np.save(EMBEDDINGS_PATH, self.embeddings)

        # metadados simples
        meta = {
            "docs": len(self.docs),
            "steps": sorted(list({d.step for d in self.docs})),
        }
        with open(METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    # ---------- Atualização ----------
    def add_documents(self, docs: List[KnowledgeDoc]) -> None:
        if not docs:
            return

        new_texts = [d.text for d in docs]
        new_embs = self.model.encode(new_texts, convert_to_numpy=True)

        if self.embeddings is None or len(self.docs) == 0:
            self.embeddings = new_embs
            self.docs = docs
        else:
            self.embeddings = np.vstack([self.embeddings, new_embs])
            self.docs.extend(docs)

        self._save_to_disk()

    def reload(self) -> None:
        """Recarrega do disco (caso outra rotina tenha atualizado os arquivos)."""
        self._load_from_disk()

    # ---------- Busca ----------
    def search(
        self,
        query: str,
        top_k: int = 5,
        step_filter: Optional[str] = None,
    ) -> List[KnowledgeDoc]:
        if self.embeddings is None or not self.docs:
            return []

        q_emb = self.model.encode([query], convert_to_numpy=True)
        sims = cosine_similarity(q_emb, self.embeddings)[0]

        # aplica filtro por step se houver
        scored: List[tuple[float, int]] = []
        for idx, doc in enumerate(self.docs):
            if step_filter and step_filter != "todas" and doc.step != step_filter:
                continue
            scored.append((sims[idx], idx))

        scored.sort(reverse=True, key=lambda x: x[0])
        top = scored[:top_k]
        return [self.docs[i] for _, i in top]

    # ---------- Info ----------
    def get_stats(self) -> Dict[str, Any]:
        if not self.docs:
            return {"docs": 0, "steps": []}
        return {
            "docs": len(self.docs),
            "steps": sorted(list({d.step for d in self.docs})),
        }


# Instância global (padrão indústria simples para projeto pequeno)
rag_engine = RAGEngine()
