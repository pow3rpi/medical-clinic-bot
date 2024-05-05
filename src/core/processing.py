from typing import List
import re


def process_input(string: str, delimiter: str) -> List[str]:
    clean_data: str
    elements: List[str]

    clean_data = re.sub(r'\s+', ' ', string).strip().strip(delimiter)
    elements = clean_data.lower().split(delimiter)
    elements = [el.strip() for el in elements]
    elements = [el[0].upper() + el[1:] for el in elements]

    return elements


def transform_name(full_name: str) -> str:
    names_list: List[str]
    short_form: str

    names_list = full_name.split(' ')
    short_form = names_list[0] + ' '
    for name in names_list[1:]:
        short_form += name[0] + '.'

    return short_form


def standardize_phone(phone: str) -> str:
    if len(phone) == 10:
        return '7' + phone
    else:
        return '7' + phone[1:]
