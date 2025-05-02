# tests/test_json_utils.py

import pytest
import logging
import csv
from backend.utils.json_utils import JSONUtils

def test_format_result_for_jsonl_basic():
    raw = "prefix {\"a\":1}\n\n{\"b\":2}\n suffix"
    result = JSONUtils.format_result_for_jsonl(raw)
    lines = result.splitlines()
    assert lines == ['{"a":1}', '{"b":2}']

def test_format_result_for_jsonl_quotes_na():
    raw = '{"x":"N/A","y":N/A}'
    result = JSONUtils.format_result_for_jsonl(raw)
    assert '"N/A"' in result
    assert result.count('"N/A"') == 2

def test_format_result_for_jsonl_no_matches():
    with pytest.raises(ValueError, match="No valid JSON block"):
        JSONUtils.format_result_for_jsonl("no json here")

def test_extract_low_result_json_basic():
    raw = "some text '''json {\"key\": 123} ''' more"
    extracted = JSONUtils.extract_low_result_json(raw)
    assert extracted.strip() == '{"key": 123}'

def test_extract_low_result_json_no_match():
    with pytest.raises(ValueError, match="No valid JSON structure"):
        JSONUtils.extract_low_result_json("invalid {")

def test_jsonlist_to_csv_creates_file(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    logger = logging.getLogger("test")
    jsonl = ['{"a":1,"b":"x"}', '{"a":2,"b":"y"}']
    out_file = tmp_path / "out.csv"
    JSONUtils.jsonlist_to_csv(jsonl, str(out_file), logger)
    
    assert out_file.exists()
    with open(out_file, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert rows == [{'a':'1','b':'x'}, {'a':'2','b':'y'}]
    assert f"CSV created successfully: {out_file}" in caplog.text

def test_jsonlist_to_csv_empty_list(tmp_path, caplog):
    caplog.set_level(logging.WARNING)
    logger = logging.getLogger("test")
    out_file = tmp_path / "empty.csv"
    JSONUtils.jsonlist_to_csv([], str(out_file), logger)
    assert not out_file.exists()
    assert "No valid JSON objects to write" in caplog.text

def test_jsonlist_to_csv_partial_invalid(tmp_path, caplog):
    caplog.set_level(logging.ERROR)
    logger = logging.getLogger("test")
    jsonl = ['{"k":1}', '{"k":invalid}']
    out_file = tmp_path / "partial.csv"
    JSONUtils.jsonlist_to_csv(jsonl, str(out_file), logger)
    assert out_file.exists()
    with open(out_file, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert rows == [{'k':'1'}]
    assert "JSON decode error" in caplog.text
