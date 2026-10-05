import json

import numpy as np

from src.neo4j_ingestion.cypher_generator import CypherGenerator
from src.retrieval.anchor_search import AnchorSearch, attach_embeddings_to_graph


def write_cache(directory, vectors, node_ids, model="test/model"):
    directory.mkdir(parents=True, exist_ok=True)
    np.save(directory / "embeddings.npy", np.asarray(vectors, dtype=np.float32))
    (directory / "node_ids.json").write_text(json.dumps(node_ids), encoding="utf-8")
    (directory / "embeddings.meta.json").write_text(
        json.dumps({
            "model": model,
            "dimension": int(np.asarray(vectors).shape[1]),
            "node_count": len(node_ids),
        }),
        encoding="utf-8",
    )


class FakeResult:
    def __iter__(self):
        return iter([{"node_id": "physical-1", "score": 0.9}])


class FakeSession:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def run(self, query, **parameters):
        self.driver.calls.append((query, parameters))
        return FakeResult()


class FakeDriver:
    def __init__(self):
        self.calls = []
        self.database = None

    def session(self, database=None):
        self.database = database
        return FakeSession(self)


class FakeEncoder:
    def encode(self, texts, **kwargs):
        assert texts == ["legal question"]
        assert kwargs["normalize_embeddings"] is False
        return np.array([[0.1, 0.2, 0.3]], dtype=np.float32)


def test_attach_embeddings_to_physical_nodes(tmp_path):
    write_cache(tmp_path, [[0.1, 0.2], [0.3, 0.4]], ["p1", "p2"])
    graph = {
        "nodes": [
            {"id": "p1", "labels": ["LegalNode", "CLAUSE"], "properties": {}},
            {"id": "p2", "labels": ["LegalNode", "POINT"], "properties": {}},
            {"id": "s1", "labels": ["SemanticEntity"], "properties": {}},
        ]
    }

    dimensions = attach_embeddings_to_graph(graph, tmp_path)

    assert dimensions == 2
    assert np.allclose(graph["nodes"][0]["properties"]["embedding"], [0.1, 0.2])
    assert graph["nodes"][2]["properties"] == {}


def test_anchor_search_embeds_query_and_calls_vector_index(tmp_path):
    write_cache(tmp_path, [[0.1, 0.2, 0.3]], ["physical-1"])
    driver = FakeDriver()
    search = AnchorSearch(
        driver,
        database="neo4j",
        embedding_dir=tmp_path,
        encoder=FakeEncoder(),
    )

    result = search.search("legal question", top_k=4)

    assert result == [{"node_id": "physical-1", "score": 0.9}]
    assert driver.database == "neo4j"
    query, parameters = driver.calls[0]
    assert "db.index.vector.queryNodes" in query
    assert parameters["index_name"] == "legal_node_vector_idx"
    assert parameters["top_k"] == 4
    assert len(parameters["embedding"]) == 3


def test_vector_index_uses_metadata_dimension():
    statement = CypherGenerator.vector_index_statement(896)

    assert "legal_node_vector_idx" in statement
    assert "vector.dimensions`: 896" in statement
    assert ":LegalNode" in statement
