import re
import random
import datetime
import pycountry
from faker import Faker
from nltk.corpus import names

class DataUtils:
    """
    Colección de utilidades para detección y generación de datos:
    nombres, IDs, países y fechas aleatorias.
    """
    fake = Faker()
    NAME_LIST = set(name.lower() for name in names.words())

    @staticmethod
    def is_name(string_value: str) -> bool:
        """
        Comprueba si una cadena es un nombre según el corpus NLTK.
        """
        return string_value.lower() in DataUtils.NAME_LIST

    @staticmethod
    def is_id(column_name: str) -> bool:
        """
        Determina si un nombre de columna indica un campo de ID.
        """
        lower_name = column_name.lower()
        if lower_name == 'id':
            return True
        if lower_name.endswith("_id") or lower_name.startswith("id_"):
            return True
        if (column_name.endswith("Id") and len(column_name) > 2 and column_name[-3].islower()):
            return True
        if ((column_name.startswith("Id") or column_name.startswith("id"))
            and len(column_name) > 2 and column_name[2].isupper()):
            return True
        return False

    @staticmethod
    def is_country(possible_country: str, translate_func) -> bool:
        """
        Traduce el texto y comprueba si es un país válido con pycountry.
        """
        english_name = translate_func(possible_country)
        try:
            pycountry.countries.lookup(english_name)
            return True
        except LookupError:
            return False

    @staticmethod
    def generate_country() -> str:
        """
        Devuelve aleatoriamente el nombre de un país.
        """
        countries = list(pycountry.countries)
        random_country = random.choice(countries)
        return random_country.name.replace('"', '')

    @staticmethod
    def generate_ids(template_str: str, max_val: int) -> list:
        """
        Genera una lista de IDs secuenciales basados en una plantilla.
        """
        # Si es todo dígitos
        if template_str.isdigit():
            return [str(i).zfill(len(template_str)) for i in range(1, max_val + 1)]

        match = re.search(r'(\D*)(\d+)(\D*)', template_str)
        if not match:
            return [template_str] * max_val

        part_start, number_str, part_end = match.group(1), match.group(2), match.group(3)
        number_len = len(number_str)

        return [
            f"{part_start}{str(i).zfill(number_len)}{part_end}"
            for i in range(1, max_val + 1)
        ]

    @staticmethod
    def generate_random_date(start_str: str, end_str: str) -> datetime.date:
        """
        Genera una fecha aleatoria entre dos fechas dadas (YYYY-MM-DD).
        """
        start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d')
        return DataUtils.fake.date_between(start_date=start_date, end_date=end_date)
