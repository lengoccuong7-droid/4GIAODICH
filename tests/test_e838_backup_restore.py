import json
import sqlite3
import zipfile
from io import BytesIO

import pytest

from modules.backup_restore import create_data_backup, restore_data_backup


def _make_db(path):
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT)')
    con.execute('INSERT INTO sample(value) VALUES (?)', ('persisted',))
    con.commit()
    con.close()


def test_backup_contains_only_allowlisted_data_files(tmp_path):
    data = tmp_path / 'data'
    data.mkdir()
    (data / 'portfolio_positions.json').write_text(json.dumps({'positions': []}), encoding='utf-8')
    (data / 'unrelated.txt').write_text('do not include', encoding='utf-8')
    archive = create_data_backup(data)
    with zipfile.ZipFile(BytesIO(archive)) as zf:
        assert zf.namelist() == ['data/portfolio_positions.json']


def test_restore_validates_and_restores_json_and_sqlite(tmp_path):
    source = tmp_path / 'source'
    target = tmp_path / 'target'
    source.mkdir()
    target.mkdir()
    (source / 'portfolio_positions.json').write_text(json.dumps({'positions': [{'symbol': 'ABC'}]}), encoding='utf-8')
    _make_db(source / 'market_history.sqlite3')
    archive = create_data_backup(source)
    restored = restore_data_backup(archive, target)
    assert restored == ['market_history.sqlite3', 'portfolio_positions.json']
    assert json.loads((target / 'portfolio_positions.json').read_text())['positions'][0]['symbol'] == 'ABC'
    con = sqlite3.connect(target / 'market_history.sqlite3')
    assert con.execute('SELECT value FROM sample').fetchone()[0] == 'persisted'
    con.close()


def test_restore_rejects_path_traversal_without_writing(tmp_path):
    out = BytesIO()
    with zipfile.ZipFile(out, 'w') as zf:
        zf.writestr('../portfolio_positions.json', '{}')
    target = tmp_path / 'data'
    with pytest.raises(ValueError, match='Đường dẫn'):
        restore_data_backup(out.getvalue(), target)
    assert not target.exists()


def test_restore_rejects_invalid_json(tmp_path):
    out = BytesIO()
    with zipfile.ZipFile(out, 'w') as zf:
        zf.writestr('data/portfolio_positions.json', '{bad json')
    with pytest.raises(ValueError, match='không hợp lệ'):
        restore_data_backup(out.getvalue(), tmp_path / 'data')


def test_restore_rejects_unrecognized_files(tmp_path):
    out = BytesIO()
    with zipfile.ZipFile(out, 'w') as zf:
        zf.writestr('data/app.py', 'print(1)')
    with pytest.raises(ValueError, match='không thuộc danh sách'):
        restore_data_backup(out.getvalue(), tmp_path / 'data')
