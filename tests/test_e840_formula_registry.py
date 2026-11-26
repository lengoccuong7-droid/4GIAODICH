from modules.formula_registry import FORMULAS, get_formula, list_formulas
from modules.calculation_registry import calculation_summary
from modules.risk_manager import calculate_position_size


def test_formula_registry_has_unique_ids_and_keeps_unverified_status_explicit():
    ids = [row["id"] for row in FORMULAS]
    assert len(ids) == len(set(ids))
    assert len(FORMULAS) >= 28
    assert all(row["status"] == "PENDING_INDEPENDENT_VALIDATION" for row in FORMULAS)
    assert get_formula("IND-RVOL20")["implementation"].endswith("_prior20_volume_mean")
    assert get_formula("PERF-SHARPE") is not None


def test_formula_registry_filter_returns_copies():
    rows = list_formulas(category="Động lượng")
    assert rows
    rows[0]["name"] = "mutated"
    assert all(row["name"] != "mutated" for row in FORMULAS)


def test_calculation_inventory_is_static_inventory_not_math_validation():
    summary = calculation_summary()
    assert summary["total_modules"] >= 10
    assert "không chứng minh" in summary["note"].lower()


def test_position_size_rejects_non_integer_or_boolean_lot_size():
    for lot in (100.5, True, "100.5"):
        result = calculate_position_size(100_000_000, 100, 95, lot_size=lot)
        assert result["status"] == "INPUT_INVALID"
        assert result["quantity"] == 0


def test_position_size_rejects_percentages_over_100():
    assert calculate_position_size(100_000_000, 100, 95, risk_pct=101)["status"] == "INPUT_INVALID"
    assert calculate_position_size(100_000_000, 100, 95, max_allocation_pct=101)["status"] == "INPUT_INVALID"
