"""Chronological train/validation/test walk-forward orchestration.

The strategy evaluator is the existing backtest_plan (same decision/risk path).
Validation chooses among explicitly supplied parameter candidates; test is then
run once with the selected candidate. All slices are positional and ordered.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

import pandas as pd

from .plan_backtest import backtest_plan


def build_walk_forward_folds(
    n_rows: int,
    *,
    warmup: int = 60,
    train_size: int = 120,
    validation_size: int = 40,
    test_size: int = 40,
    step_size: int | None = None,
) -> list[dict[str, int]]:
    """Build expanding-history folds with disjoint train/validation/test blocks."""
    vals = (n_rows, warmup, train_size, validation_size, test_size)
    if any(isinstance(v, bool) or int(v) != v for v in vals):
        raise ValueError("Các kích thước phải là số nguyên.")
    if warmup < 1 or train_size < 1 or validation_size < 1 or test_size < 1:
        raise ValueError("Warmup và kích thước các tập phải lớn hơn 0.")
    step = test_size if step_size is None else step_size
    if isinstance(step, bool) or int(step) != step or step < 1:
        raise ValueError("step_size phải là số nguyên dương.")

    folds: list[dict[str, int]] = []
    train_end = warmup + train_size - 1
    fold_id = 1
    while True:
        val_start = train_end + 1
        val_end = val_start + validation_size - 1
        test_start = val_end + 1
        test_end = test_start + test_size - 1
        if test_end >= n_rows:
            break
        folds.append({
            "fold": fold_id,
            "train_start": warmup,
            "train_end": train_end,
            "validation_start": val_start,
            "validation_end": val_end,
            "test_start": test_start,
            "test_end": test_end,
        })
        fold_id += 1
        train_end += int(step)
    return folds


def _metric(result: dict[str, Any], name: str) -> float | None:
    value = result.get(name)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if pd.notna(value) else None


def walk_forward_validate(
    frame: pd.DataFrame,
    benchmark: pd.DataFrame,
    *,
    warmup: int = 60,
    train_size: int = 120,
    validation_size: int = 40,
    test_size: int = 40,
    step_size: int | None = None,
    parameter_candidates: list[dict[str, Any]] | None = None,
    selection_metric: str = "expectancy_pct",
    min_validation_trades: int = 3,
    backtest_fn=None,
    base_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run train/validation selection and one untouched OOS test per fold.

    Candidate selection uses validation only. Train results are reported for
    diagnostics and never used to select a candidate. No parameter optimization
    is performed unless candidates are explicitly supplied by the caller.
    """
    if not isinstance(frame, pd.DataFrame) or not isinstance(benchmark, pd.DataFrame):
        raise TypeError("frame và benchmark phải là pandas DataFrame.")
    if "date" not in frame or "date" not in benchmark:
        raise ValueError("frame và benchmark phải có cột date.")
    stock = frame.copy()
    stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
    stock = stock.dropna(subset=["date"]).sort_values("date", kind="mergesort").reset_index(drop=True)
    bmk = benchmark.copy()
    bmk["date"] = pd.to_datetime(bmk["date"], errors="coerce")
    bmk = bmk.dropna(subset=["date"]).sort_values("date", kind="mergesort").reset_index(drop=True)
    if stock["date"].duplicated().any():
        raise ValueError("Dữ liệu cổ phiếu có ngày trùng; cần xử lý trước walk-forward.")
    if bmk["date"].duplicated().any():
        raise ValueError("Dữ liệu benchmark có ngày trùng; cần xử lý trước walk-forward.")

    folds = build_walk_forward_folds(
        len(stock), warmup=warmup, train_size=train_size,
        validation_size=validation_size, test_size=test_size, step_size=step_size,
    )
    if not folds:
        return {"status": "INSUFFICIENT_DATA", "folds": [], "fold_count": 0,
                "reason": "Không đủ dữ liệu cho ít nhất một fold train/validation/test."}

    candidates = deepcopy(parameter_candidates) if parameter_candidates else [{}]
    if not isinstance(candidates, list) or not candidates or any(not isinstance(x, dict) for x in candidates):
        raise ValueError("parameter_candidates phải là danh sách dict không rỗng.")
    if min_validation_trades < 0:
        raise ValueError("min_validation_trades không được âm.")
    run = backtest_fn or backtest_plan
    base = dict(base_params or {})
    base.setdefault("warmup", warmup)
    output = []

    for fold in folds:
        train_results = []
        validation_results = []
        for candidate_id, candidate in enumerate(candidates, start=1):
            params = {**base, **candidate}
            train = run(stock, benchmark=bmk, **params,
                        test_start_index=fold["train_start"], test_end_index=fold["train_end"])
            validation = run(stock, benchmark=bmk, **params,
                             test_start_index=fold["validation_start"], test_end_index=fold["validation_end"])
            train_results.append({"candidate_id": candidate_id, "result": train})
            closed = int(validation.get("closed_trades", 0)) if isinstance(validation, dict) else 0
            score = _metric(validation, selection_metric) if isinstance(validation, dict) else None
            validation_results.append({"candidate_id": candidate_id, "params": candidate,
                                       "result": validation, "score": score,
                                       "eligible": closed >= min_validation_trades and score is not None})
        eligible = [r for r in validation_results if r["eligible"]]
        if eligible:
            # Deterministic tie-break: earlier candidate wins.
            selected = max(eligible, key=lambda r: r["score"])
            selected_status = "SELECTED_ON_VALIDATION"
            selected_params = selected["params"]
            test = run(stock, benchmark=bmk, **{**base, **selected_params},
                       test_start_index=fold["test_start"], test_end_index=fold["test_end"])
        else:
            selected_status = "NO_CANDIDATE_PASSED_VALIDATION"
            selected_params = None
            test = {"status": "SKIPPED", "reason": "Không có ứng viên đủ số lệnh và metric validation hợp lệ."}
        output.append({**fold, "train_candidates": train_results,
                       "validation_candidates": validation_results,
                       "selection_status": selected_status,
                       "selected_params": selected_params, "test_result": test})

    tested = [f["test_result"] for f in output if isinstance(f["test_result"], dict)
              and f["test_result"].get("status") != "SKIPPED" and "error" not in f["test_result"]]
    return {
        "status": "OK" if tested else "NO_VALID_OOS_TESTS",
        "method": "EXPANDING_WINDOW_TRAIN_VALIDATION_TEST",
        "selection_metric": selection_metric,
        "fold_count": len(output),
        "tested_fold_count": len(tested),
        "folds": output,
        "limitations": [
            "Chỉ chọn tham số từ validation; test không tham gia chọn tham số.",
            "Kết quả phụ thuộc giả định khớp lệnh, phí, thuế, trượt giá và dữ liệu OHLCV.",
            "Các fold hiện báo cáo độc lập; chưa mô phỏng vốn/vị thế liên tục xuyên fold.",
            "Không tự tối ưu tham số nếu không truyền parameter_candidates.",
        ],
    }
