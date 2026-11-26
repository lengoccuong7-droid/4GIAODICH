"""Stable, versioned contracts shared by analysis modules and orchestration."""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any

VALID_STATUSES = {"OK", "WARNING", "INSUFFICIENT_DATA", "ERROR", "NOT_RUN"}


@dataclass
class ModuleResult:
    module: str
    status: str
    evidence: list[Any] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    confidence: str | None = None
    data_requirements: list[str] = field(default_factory=list)
    data_as_of: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    module_id: str | None = None
    signal: Any = None
    limitations: list[str] = field(default_factory=list)
    source_refs: list[Any] = field(default_factory=list)
    snapshot_id: str | None = None
    calculation_version: str = "8.4.0"

    def to_dict(self) -> dict:
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid module status: {self.status}")
        return asdict(self)


def normalize_module_result(module: str, result: dict | None, data_as_of=None,
                            snapshot_id=None, calculation_version="8.4.0") -> dict:
    """Adapt legacy result dictionaries while retaining payload and traceability."""
    if not isinstance(result, dict):
        return ModuleResult(
            module=module, module_id=module, status="ERROR",
            warnings=["Module không trả về dict hợp lệ."],
            data_as_of=str(data_as_of) if data_as_of is not None else None,
            snapshot_id=snapshot_id, calculation_version=calculation_version,
        ).to_dict()
    raw_status = str(result.get("status", "WARNING")).upper()
    status = raw_status if raw_status in VALID_STATUSES else "WARNING"
    evidence = result.get("evidence", [])
    if not isinstance(evidence, list):
        evidence = [evidence]
    warnings = result.get("warnings", result.get("cautions", result.get("issues", [])))
    if isinstance(warnings, str):
        warnings = [warnings]
    elif not isinstance(warnings, list):
        warnings = []
    limitations = result.get("limitations", result.get("cautions", []))
    if isinstance(limitations, str):
        limitations = [limitations]
    elif not isinstance(limitations, list):
        limitations = []
    source_refs = result.get("source_refs", result.get("sources", []))
    if not isinstance(source_refs, list):
        source_refs = [source_refs] if source_refs else []
    return ModuleResult(
        module=module, module_id=str(result.get("module_id", module)), status=status,
        evidence=evidence, warnings=[str(x) for x in warnings],
        confidence=result.get("confidence"),
        data_requirements=list(result.get("data_requirements", [])) if isinstance(result.get("data_requirements", []), list) else [],
        data_as_of=str(data_as_of) if data_as_of is not None else result.get("data_as_of"),
        payload=result, signal=result.get("signal", result.get("decision", result.get("label"))),
        limitations=[str(x) for x in limitations], source_refs=source_refs,
        snapshot_id=snapshot_id or result.get("snapshot_id"),
        calculation_version=str(calculation_version),
    ).to_dict()
