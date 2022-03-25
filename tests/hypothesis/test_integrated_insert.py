from random import choice
from string import printable

from inflection import underscore

from faker import Faker
from hypothesis import strategies as st
from hypothesis.strategies import builds
from hypothesis.strategies import composite

from bodhi_server.utils import InsertParameters


fake_generator = Faker()


def random_title():
    available_generator_list = [
        "color_name",
        "first_name",
        "language_name",
        "last_name",
        "city",
        "country",
        "street_name",
        "street_suffix",
        "credit_card_provider",
    ]
    selected_attr: str = choice(available_generator_list)

    return underscore(getattr(fake_generator, selected_attr)())
