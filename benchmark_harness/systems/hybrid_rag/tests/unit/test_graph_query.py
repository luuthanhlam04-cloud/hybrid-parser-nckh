from src.retrieval.graph_query import GraphQuery


class FakeResult:
    def __init__(self, records):
        self.records = records

    def __iter__(self):
        return iter(self.records)


class FakeSession:
    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def run(self, query, **parameters):
        self.driver.calls.append((query, parameters))
        return FakeResult(self.driver.records)


class FakeDriver:
    def __init__(self, records=None):
        self.records = records or []
        self.calls = []
        self.database = None

    def session(self, database=None):
        self.database = database
        return FakeSession(self)


def test_mode_a_returns_norm_records_and_deduplicates_anchor_ids():
    expected = [{"norm_id": "norm-1", "modality": "PROHIBIT"}]
    driver = FakeDriver(expected)
    graph_query = GraphQuery(driver, database="neo4j")

    result = graph_query.retrieve_mode_a(["anchor-1", "anchor-1"], limit=5)

    assert result == expected
    assert driver.database == "neo4j"
    query, parameters = driver.calls[0]
    assert "GLOBAL_NORM" in query
    assert "HAS_SUBJECT" in query
    assert "HAS_ACTION" in query
    assert "HAS_CONDITION" in query
    assert "HAS_EXCEPTION" in query
    assert "collect(DISTINCT" in query
    assert parameters == {"anchor_ids": ["anchor-1"], "limit": 5}


def test_mode_b_bounds_hops_and_paths():
    driver = FakeDriver([{"anchor_id": "anchor-1", "nodes": [], "relationships": []}])
    graph_query = GraphQuery(driver)

    result = graph_query.retrieve_mode_b(["anchor-1"], max_hops=3, max_paths=7)

    assert result == driver.records
    query, parameters = driver.calls[0]
    assert "[*1..3]" in query
    assert parameters == {"anchor_ids": ["anchor-1"], "max_paths": 7}


def test_empty_anchors_skip_database_query():
    driver = FakeDriver()
    graph_query = GraphQuery(driver)

    assert graph_query.retrieve_mode_a([]) == []
    assert graph_query.retrieve_mode_b([]) == []
    assert driver.calls == []


def test_retrieval_rejects_invalid_limits_and_anchor_ids():
    graph_query = GraphQuery(FakeDriver())

    for call in (
        lambda: graph_query.retrieve_mode_a(["anchor-1"], limit=0),
        lambda: graph_query.retrieve_mode_b(["anchor-1"], max_hops=4),
        lambda: graph_query.retrieve_mode_a("anchor-1"),
        lambda: graph_query.retrieve_mode_b([""]),
    ):
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError("Expected invalid retrieval arguments to be rejected.")
