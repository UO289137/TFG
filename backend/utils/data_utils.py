import re
import random
import datetime
import pycountry
from faker import Faker
from nltk.corpus import names

fake = Faker()

# Load name corpus for name checks
NAME_LIST = set(name.lower() for name in names.words())

def is_name(string_value: str) -> bool:
    """
    Check if a given string_value likely represents a name 
    based on the NLTK corpus of names.
    """
    return string_value.lower() in NAME_LIST

def is_id(column_name: str) -> bool:
    """
    Determine whether a column_name indicates an ID field.
    """
    lower_name = column_name.lower()
    if lower_name == 'id':
        return True
    if lower_name.endswith("_id") or lower_name.startswith("id_"):
        return True
    # Check for patterns like "IdX" or "XId"
    if (column_name.endswith("Id") and len(column_name) > 2 and column_name[-3].islower()):
        return True
    if ((column_name.startswith("Id") or column_name.startswith("id"))
        and len(column_name) > 2 and column_name[2].isupper()):
        return True
    return False

def is_country(possible_country: str, translate_func) -> bool:
    """
    Check if a string is a valid country name by translating it to English
    and then looking it up via pycountry.
    """
    english_name = translate_func(possible_country)
    try:
        pycountry.countries.lookup(english_name)
        return True
    except LookupError:
        return False

def generate_country() -> str:
    """
    Return a random country name, according to pycountry.
    """
    countries = list(pycountry.countries)
    random_country = random.choice(countries)
    return random_country.name.replace('"', '')

def generate_ids(template_str: str, max_val: int) -> list:
    """
    Generate a list of IDs based on a template string that may contain digits.
    For example, 'USR0001' will generate ['USR0001', 'USR0002', ..., 'USR0100'] for max_val=100.
    """
    # If the entire string is just digits
    if template_str.isdigit():
        return [str(i).zfill(len(template_str)) for i in range(1, max_val + 1)]

    match = re.search(r'(\D*)(\d+)(\D*)', template_str)
    if not match:
        # If there are no digits in template_str, return it repeated max_val times
        return [template_str] * max_val

    part_start = match.group(1)
    number_str = match.group(2)
    part_end = match.group(3)
    number_len = len(number_str)

    # Generate new strings incrementing the numeric part
    result = [
        f"{part_start}{str(i).zfill(number_len)}{part_end}"
        for i in range(1, max_val + 1)
    ]
    return result

def generate_random_date(start_str: str, end_str: str) -> datetime.date:
    """
    Generate a random date between two given date strings (YYYY-MM-DD).
    """
    start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d')
    return fake.date_between(start_date=start_date, end_date=end_date)
