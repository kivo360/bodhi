import pytest
from faker import Faker
from faker_schema.faker_schema import FakerSchema

flat_schema = {
    'employee_id': 'uuid4',
    'employee_name': 'name',
    'employee address': 'address',
    'email_address': 'email'
}

nested_schema = {
    'employee_id': 'uuid4',
    'employee_name': 'name',
    'employee address': 'address',
    'email_address': 'email',
    'contact': {
        'email': 'email', 'phone_number': 'phone_number'
    },
    'location': {
        'country_code': 'country_code',
        'city': 'city',
        'country': 'country',
        'postal_code': 'postalcode',
        'address': 'street_address'
    },
}


@pytest.fixture(scope = "session")
def core_faker() -> Faker:
    return Faker()


@pytest.fixture(scope = "session")
def core_faker_schema() -> FakerSchema:
    return FakerSchema()


@pytest.fixture
def fake_single_employee_record(core_faker_schema: FakerSchema):
    return core_faker_schema.generate_fake(flat_schema)


@pytest.fixture
def fake_single_nested_employee_record(core_faker_schema: FakerSchema):
    return core_faker_schema.generate_fake(nested_schema)


def generate_multiple_employees(insert_amout: int):
    faker_schema = FakerSchema()
    for _ in range(insert_amout):
        yield faker_schema.generate_fake(flat_schema)
