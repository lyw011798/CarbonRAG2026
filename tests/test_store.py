import pytest
from src.store import VectorStore


def test_vector_store_init(tmp_path):
    db_path = str(tmp_path / "chroma_init")
    store = VectorStore(db_path=db_path)
    assert store.collection.name == "taiwan_carbon_market"


def test_add_and_query(tmp_path):
    db_path = str(tmp_path / "chroma_add")
    store = VectorStore(db_path=db_path)

    chunks = [
        {
            "text": "氣候變遷因應法第一條：為因應全球氣候變遷，落實世代正義、環境永續及國家發展，特制定本法。",
            "metadata": {"source": "law.txt", "article": "第一條", "jurisdiction": "Taiwan"}
        },
        {
            "text": "溫室氣體減量及管理法：行政院應定期檢討國家應變策略。",
            "metadata": {"source": "ghg.txt", "article": "General", "jurisdiction": "Taiwan"}
        }
    ]

    store.add_documents(chunks)

    # Semantic search for "climate change law purpose" in Chinese
    results = store.query("氣候變遷法律的目的", n_results=1)

    assert len(results) == 1
    assert "氣候變遷因應法" in results[0]["text"]
    assert results[0]["metadata"]["article"] == "第一條"


def test_query_no_results(tmp_path):
    db_path = str(tmp_path / "chroma_empty")
    store = VectorStore(db_path=db_path)
    results = store.query("Random query", n_results=5)
    assert len(results) == 0
