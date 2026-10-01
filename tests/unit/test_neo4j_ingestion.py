from src.neo4j_ingestion import CypherGenerator, GraphChecker, Neo4jIngestor


def sample_graph():
    return {
        "nodes": [
            {
                "id": "a",
                "node_kind": "PHYSICAL",
                "labels": ["LegalNode", "ARTICLE"],
                "properties": {"text": "Điều 1"},
                "provenance": [],
            },
            {
                "id": "b",
                "node_kind": "PHYSICAL",
                "labels": ["LegalNode", "CLAUSE"],
                "properties": {"text": "Nội dung"},
                "provenance": [],
            },
        ],
        "edges": [
            {
                "source": "b",
                "target": "a",
                "type": "BELONG_TO",
                "properties": {},
                "provenance": [],
            }
        ],
    }


class QueryResult:
    def __init__(self, record=None, records=None):
        self.record = record
        self.records = records or []

    def consume(self):
        return None

    def single(self):
        return self.record

    def __iter__(self):
        return iter(self.records)


class FakeTransaction:
    def __init__(self, queries):
        self.queries = queries

    def run(self, query, **parameters):
        self.queries.append((query, parameters))
        return QueryResult()


class FakeSession:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def run(self, query, **parameters):
        self.driver.queries.append((query, parameters))
        return QueryResult()

    def execute_write(self, callback, *args):
        self.driver.write_batch_sizes.append(
            len(args[0]) if args and isinstance(args[0], list) else 0
        )
        return callback(FakeTransaction(self.driver.queries), *args)


class FakeDriver:
    def __init__(self):
        self.queries = []
        self.write_batch_sizes = []

    def session(self, database=None):
        return FakeSession(self)


def test_generator_serializes_nested_properties_and_stable_edge_identity():
    graph = sample_graph()
    node = CypherGenerator.node_parameters(graph["nodes"][0])
    edge = CypherGenerator.edge_parameters(graph["edges"][0])

    assert '"text": "Điều 1"' in node["properties_json"]
    assert "ARTICLE" in node["search_text"]
    assert edge["edge_key"] == CypherGenerator.edge_key(graph["edges"][0])
    assert edge["source_id"] == "b"


def test_ingestor_batches_nodes_and_edges_and_initializes_schema():
    graph = sample_graph()
    driver = FakeDriver()
    report = Neo4jIngestor(driver, batch_size=1).ingest(graph)

    assert report == {
        "nodes": 2,
        "edges": 1,
        "node_batches": 2,
        "edge_batches": 1,
    }
    assert driver.write_batch_sizes == [1, 1, 1]
    assert any("CREATE CONSTRAINT ukg_node_id" in query for query, _ in driver.queries)
    assert any("CREATE FULLTEXT INDEX ukg_node_text" in query for query, _ in driver.queries)
    assert any("UNWIND $rows AS row" in query for query, _ in driver.queries)


def test_ingestor_rejects_invalid_edges_before_database_access():
    graph = sample_graph()
    graph["edges"][0]["target"] = "missing"
    driver = FakeDriver()

    try:
        Neo4jIngestor(driver).ingest(graph)
    except ValueError as exc:
        assert "unknown node" in str(exc)
    else:
        raise AssertionError("Expected validation to reject an unknown endpoint.")
    assert driver.queries == []


def test_graph_checker_detects_cycles_and_accepts_acyclic_structures():
    assert not GraphChecker._has_cycle([("child", "parent"), ("leaf", "child")])
    assert GraphChecker._has_cycle([("a", "b"), ("b", "a")])


def test_replace_is_explicit_and_deletes_only_managed_graph():
    driver = FakeDriver()
    Neo4jIngestor(driver).ingest(sample_graph(), replace=True)

    assert any(
        "MATCH (n:UKG_NODE) DETACH DELETE n" in query
        for query, _ in driver.queries
    )
