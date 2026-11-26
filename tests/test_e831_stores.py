from pathlib import Path
from modules.knowledge_hub import index_document, search_documents, list_documents, get_document, delete_document
from modules.formula_registry import list_formulas, get_formula
from modules.calculation_registry import calculation_summary, inspect_calculation_registry


def test_knowledge_hub_persists_metadata_and_retrieves_content(tmp_path):
    db = str(tmp_path / "data" / "knowledge.sqlite")
    raw = b"RSI Wilder 14 average gain average loss formula reference"
    added = index_document("rsi.txt", raw, ticker="AAA", doc_type="Phuong phap",
                           period="v1", source_name="Reference", source_date="2026-01-01", db_path=db)
    assert added["characters"] > 10
    assert not added["duplicate"]
    duplicate = index_document("rsi.txt", raw, ticker="AAA", db_path=db)
    assert duplicate["duplicate"]
    hits = search_documents("Wilder average gain", ticker="AAA", db_path=db)
    assert hits and hits[0]["ticker"] == "AAA"
    doc = get_document(added["id"], db_path=db)
    assert doc["content"] == raw.decode()
    assert doc["source_name"] == "Reference"
    assert list_documents(db_path=db)[0]["id"] == added["id"]
    assert delete_document(added["id"], db_path=db)
    assert get_document(added["id"], db_path=db) is None


def test_formula_catalog_has_unique_ids_and_implementation_paths():
    rows = list_formulas()
    ids = [x["id"] for x in rows]
    assert len(ids) == len(set(ids))
    assert len(rows) >= 15
    assert all(x["expression"] and x["inputs"] and x["output"] and x["status"] for x in rows)
    assert get_formula("IND-RSI14")["status"] == "PENDING_INDEPENDENT_VALIDATION"
    assert get_formula("NOT-FOUND") is None


def test_calculation_registry_matches_real_source_functions():
    rows = inspect_calculation_registry()
    assert len(rows) >= 8
    assert all(x["parse_ok"] for x in rows)
    assert all(not x["missing_functions"] for x in rows)
    assert all(not x["missing_test_files"] for x in rows)
    assert calculation_summary()["review_required"] == 0
