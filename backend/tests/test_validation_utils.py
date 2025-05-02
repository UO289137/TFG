import pytest
from backend.utils.validation_utils import ValidationUtils

@pytest.mark.parametrize("config, expected", [
    ({}, False),                         # Sin clave 'columns'
    ({"columns": {}}, False),            # 'columns' vacío
])
def test_empty_columns(config, expected):
    assert ValidationUtils.validate_config_dict(config) is expected

def test_string_missing_values():
    config = {"columns": {"col1": {"type": "string"}}}
    assert not ValidationUtils.validate_config_dict(config)

def test_string_valid():
    config = {"columns": {"col1": {"type": "string", "values": ["a","b"]}}}
    assert ValidationUtils.validate_config_dict(config)

@pytest.mark.parametrize("props", [
    {"type": "int", "min": 1},            # Falta 'max'
    {"type": "int", "max": 10},           # Falta 'min'
])
def test_int_missing_bounds(props):
    assert not ValidationUtils.validate_config_dict({"columns": {"col1": props}})

def test_int_valid():
    config = {"columns": {"col1": {"type": "int", "min": 0, "max": 5}}}
    assert ValidationUtils.validate_config_dict(config)

@pytest.mark.parametrize("props", [
    {"type": "float", "min": 0.0},        # Falta 'max'
    {"type": "float", "max": 1.0},        # Falta 'min'
])
def test_float_missing_bounds(props):
    assert not ValidationUtils.validate_config_dict({"columns": {"col1": props}})

def test_float_valid():
    config = {"columns": {"col1": {"type": "float", "min": 0.5, "max": 2.5}}}
    assert ValidationUtils.validate_config_dict(config)

@pytest.mark.parametrize("props", [
    {"type": "date", "start": "2020-01-01"},  # Falta 'end'
    {"type": "date", "end": "2020-12-31"},    # Falta 'start'
])
def test_date_missing_bounds(props):
    assert not ValidationUtils.validate_config_dict({"columns": {"col1": props}})

def test_date_valid():
    config = {"columns": {"col1": {"type": "date", "start": "2020-01-01", "end": "2020-12-31"}}}
    assert ValidationUtils.validate_config_dict(config)

def test_boolean_type():
    # Boolean no requiere campos adicionales
    config = {"columns": {"col1": {"type": "boolean"}}}
    assert ValidationUtils.validate_config_dict(config)

def test_unknown_type():
    # Cualquier tipo no reconocido debe devolver False
    config = {"columns": {"col1": {"type": "mystery"}}}
    assert not ValidationUtils.validate_config_dict(config)
