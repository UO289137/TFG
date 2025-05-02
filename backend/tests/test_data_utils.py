import pytest
import datetime
import random

from backend.utils.data_utils import DataUtils

# Tests for is_name

def test_is_name_true(monkeypatch):
    # Monkey-patch NAME_LIST to a controlled set
    monkeypatch.setattr(DataUtils, "NAME_LIST", {"alice", "bob"})
    assert DataUtils.is_name("Alice")
    assert DataUtils.is_name("bob")


def test_is_name_false(monkeypatch):
    monkeypatch.setattr(DataUtils, "NAME_LIST", {"alice", "bob"})
    assert not DataUtils.is_name("Charlie")
    assert not DataUtils.is_name("")

# Tests for is_id
@pytest.mark.parametrize("column, expected", [
    ("id", True),
    ("user_id", True),
    ("id_user", True),
    ("orderId", True),
    ("IdNumber", True),
    ("identifier", False),
    ("idx", False),
])
def test_is_id(column, expected):
    assert DataUtils.is_id(column) is expected

# Tests for is_country

def test_is_country_true():
    translate = lambda x: "Spain"
    assert DataUtils.is_country("España", translate)


def test_is_country_false():
    translate = lambda x: "Atlantis"
    assert not DataUtils.is_country("Atlantis", translate)

# Tests for generate_country

def test_generate_country():
    country = DataUtils.generate_country()
    assert isinstance(country, str)
    assert country != ""
    # Check country in pycountry list
    import pycountry
    all_names = {c.name for c in pycountry.countries}
    assert country in all_names

# Tests for generate_ids

def test_generate_ids_digits():
    result = DataUtils.generate_ids("001", 3)
    assert result == ["001", "002", "003"]


def test_generate_ids_pattern():
    result = DataUtils.generate_ids("item01A", 4)
    assert result == ["item01A", "item02A", "item03A", "item04A"]


def test_generate_ids_no_digits():
    result = DataUtils.generate_ids("abc", 3)
    assert result == ["abc", "abc", "abc"]

# Tests for generate_random_date

def test_generate_random_date():
    start_str = "2020-01-01"
    end_str = "2020-01-10"
    dates = {DataUtils.generate_random_date(start_str, end_str) for _ in range(10)}
    for d in dates:
        assert isinstance(d, datetime.date)
        assert datetime.date(2020,1,1) <= d <= datetime.date(2020,1,10)

# Test reproducibility for generate_country

def test_generate_country_reproducible(monkeypatch):
    class DummyCountry:
        def __init__(self, name):
            self.name = name
    dummy_list = [DummyCountry("TestLand")]
    monkeypatch.setattr(random, "choice", lambda x: dummy_list[0])
    assert DataUtils.generate_country() == "TestLand"
