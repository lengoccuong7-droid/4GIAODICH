"""Safe local backup/restore helpers for user-generated application data."""
from __future__ import annotations

import io
import json
import sqlite3
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ALLOWED_FILES = {
    "market_history.sqlite3",
    "trading_knowledge.sqlite",
    "decision_journal.sqlite3",
    "decision_journal.jsonl",
    "portfolio_positions.json",
    "sector_index.csv",
}
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024


def create_data_backup(data_dir: str | Path) -> bytes:
    """Return a ZIP backup containing only recognized files directly in data_dir."""
    root = Path(data_dir)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(ALLOWED_FILES):
            path = root / name
            if not path.is_file():
                continue
            if name.endswith((".sqlite", ".sqlite3")):
                # SQLite online backup includes committed pages even when WAL is active.
                with tempfile.NamedTemporaryFile(suffix=".sqlite") as snapshot:
                    source = sqlite3.connect(path)
                    destination = sqlite3.connect(snapshot.name)
                    try:
                        source.backup(destination)
                    finally:
                        destination.close()
                        source.close()
                    archive.write(snapshot.name, arcname=f"data/{name}")
            else:
                archive.write(path, arcname=f"data/{name}")
    return output.getvalue()


def _validate_member(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or len(path.parts) != 2 or path.parts[0] != "data":
        raise ValueError(f"Đường dẫn không được phép trong bản sao lưu: {name}")
    filename = path.parts[1]
    if filename not in ALLOWED_FILES:
        raise ValueError(f"Tệp không thuộc danh sách dữ liệu được phép: {filename}")
    return filename


def _validate_payload(filename: str, payload: bytes) -> None:
    if filename.endswith((".sqlite", ".sqlite3")):
        temp = io.BytesIO(payload)
        # sqlite3 requires a filesystem path for a reliable integrity check.
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as handle:
            handle.write(temp.getvalue())
            handle.flush()
            conn = sqlite3.connect(handle.name)
            try:
                result = conn.execute("PRAGMA integrity_check").fetchone()
                if not result or result[0] != "ok":
                    raise ValueError(f"Cơ sở dữ liệu {filename} không vượt qua integrity_check.")
            finally:
                conn.close()
    elif filename == "portfolio_positions.json":
        try:
            parsed = json.loads(payload.decode("utf-8"))
        except Exception as exc:
            raise ValueError("portfolio_positions.json không hợp lệ.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("portfolio_positions.json phải có cấu trúc object.")
    elif filename == "decision_journal.jsonl":
        for line_no, line in enumerate(payload.decode("utf-8").splitlines(), 1):
            if line.strip():
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Nhật ký JSONL lỗi tại dòng {line_no}.") from exc
    elif filename == "sector_index.csv":
        header = payload.decode("utf-8-sig").splitlines()[0:1]
        if not header or not {"date", "sector", "close"}.issubset({x.strip().lower() for x in header[0].split(",")}):
            raise ValueError("sector_index.csv thiếu cột date, sector hoặc close.")


def restore_data_backup(archive_bytes: bytes, data_dir: str | Path) -> list[str]:
    """Validate all archive members before atomically replacing allowed data files."""
    if len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("Bản sao lưu vượt quá giới hạn 100 MB.")
    root = Path(data_dir)
    staged: dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes), "r") as archive:
            total_uncompressed = 0
            for info in archive.infolist():
                if info.is_dir():
                    continue
                total_uncompressed += info.file_size
                if info.file_size > MAX_ARCHIVE_BYTES or total_uncompressed > MAX_ARCHIVE_BYTES:
                    raise ValueError("Nội dung giải nén vượt quá giới hạn 100 MB.")
                filename = _validate_member(info.filename)
                if filename in staged:
                    raise ValueError(f"Tệp bị lặp trong bản sao lưu: {filename}")
                payload = archive.read(info)
                _validate_payload(filename, payload)
                staged[filename] = payload
    except zipfile.BadZipFile as exc:
        raise ValueError("Tệp tải lên không phải bản sao lưu ZIP hợp lệ.") from exc
    if not staged:
        raise ValueError("Bản sao lưu không chứa tệp dữ liệu hợp lệ.")

    root.mkdir(parents=True, exist_ok=True)
    written = []
    for filename, payload in staged.items():
        target = root / filename
        temp = target.with_name(target.name + ".restore-tmp")
        temp.write_bytes(payload)
        temp.replace(target)
        written.append(filename)
    return sorted(written)
