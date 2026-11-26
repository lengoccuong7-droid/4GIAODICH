"""Inventory and static verification of calculation code in this application."""
from __future__ import annotations
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALCULATION_MODULES = [
    {"module":"modules/indicators.py", "purpose":"Tính chỉ báo kỹ thuật và đặc trưng OHLCV", "functions":["add_indicators", "add_ohlcv_features", "_calculate_clv", "_calculate_obv"], "tests":["tests/test_unified_analytics.py"], "owner":"Unified Analytics"},
    {"module":"modules/risk_manager.py", "purpose":"Tính quy mô vị thế và ngân sách rủi ro", "functions":["calculate_position_size"], "tests":["tests/test_e82_architecture.py"], "owner":"Risk Manager"},
    {"module":"modules/portfolio_manager.py", "purpose":"Đánh giá phơi nhiễm và rủi ro danh mục", "functions":["assess_portfolio_risk", "summarize_portfolio"], "tests":["tests/test_e82_architecture.py"], "owner":"Portfolio Manager"},
    {"module":"modules/relative_strength.py", "purpose":"Tính sức mạnh tương đối so với benchmark/ngành", "functions":["relative_strength"], "tests":["tests/test_unified_analytics.py"], "owner":"Analysis Modules"},
    {"module":"modules/market_regime.py", "purpose":"Đánh giá chế độ thị trường", "functions":["assess_market_regime"], "tests":["tests/test_unified_analytics.py"], "owner":"Analysis Modules"},
    {"module":"modules/market_flow_trap.py", "purpose":"Phân tích dấu hiệu dòng tiền proxy và bẫy giá", "functions":["analyze_flow_and_traps"], "tests":["tests/test_market_flow_trap.py"], "owner":"Analysis Modules"},
    {"module":"modules/performance_metrics.py", "purpose":"Tính chỉ số hiệu suất/backtest", "functions":["calculate_performance"], "tests":["tests/test_unified_analytics.py"], "owner":"Backtest"},
    {"module":"modules/unified_analytics.py", "purpose":"Enrich Once và tạo Unified Snapshot", "functions":["enrich_once", "build_unified_snapshot"], "tests":["tests/test_unified_analytics.py", "tests/test_e83_snapshot_integration.py"], "owner":"Unified Analytics"},
    {"module":"modules/position_state.py", "purpose":"Tổng hợp vị thế theo lô và ngày thanh toán được cung cấp", "functions":["build_position_state"], "tests":["tests/test_e847_integration.py"], "owner":"Position State"},
    {"module":"modules/risk_gate.py", "purpose":"Áp dụng hard/soft constraints cho hành động chuẩn", "functions":["apply_risk_gate"], "tests":["tests/test_e847_integration.py"], "owner":"Risk Gate"},
    {"module":"modules/price_limit_engine.py", "purpose":"Tính và kiểm tra biên độ giá theo cấu hình", "functions":["calculate_price_limits", "validate_ohlc_within_limits"], "tests":["tests/test_e847_integration.py"], "owner":"Execution"},
    {"module":"modules/execution_simulator.py", "purpose":"Mô phỏng khớp lệnh giới hạn theo OHLCV và participation cap", "functions":["simulate_limit_order"], "tests":["tests/test_e847_integration.py"], "owner":"Execution"},
]


def inspect_calculation_registry(root: str | Path | None = None) -> list[dict]:
    base = Path(root) if root else ROOT
    results = []
    for item in CALCULATION_MODULES:
        path = base / item["module"]
        actual_functions = set()
        parse_error = None
        if path.exists():
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                actual_functions = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            except (SyntaxError, UnicodeDecodeError) as exc:
                parse_error = str(exc)
        missing = sorted(set(item["functions"]) - actual_functions)
        tests_missing = [t for t in item["tests"] if not (base / t).exists()]
        results.append({**item, "exists":path.exists(), "parse_ok":path.exists() and parse_error is None,
                        "declared_functions_found":sorted(set(item["functions"]) & actual_functions),
                        "missing_functions":missing, "missing_test_files":tests_missing,
                        "status":"INVENTORY_OK" if path.exists() and parse_error is None and not missing and not tests_missing else "REVIEW_REQUIRED",
                        "parse_error":parse_error})
    return results


def calculation_summary(root: str | Path | None = None) -> dict:
    rows = inspect_calculation_registry(root)
    return {"total_modules":len(rows), "inventory_ok":sum(x["status"] == "INVENTORY_OK" for x in rows),
            "review_required":sum(x["status"] != "INVENTORY_OK" for x in rows), "modules":rows,
            "note":"Kiểm tra AST xác nhận sự tồn tại hàm và tệp kiểm thử; không chứng minh công thức đúng về mặt toán học."}
