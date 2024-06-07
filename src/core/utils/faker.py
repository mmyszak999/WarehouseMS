import random
from decimal import Decimal

from faker import Faker
from faker.providers import address, date_time, internet, lorem, misc, person
from faker_commerce import Provider as commerce_provider


def initialize_faker():
    faker = Faker("en_US")
    faker.seed_instance(random.randint(1, 1000))
    faker.add_provider(person)
    faker.add_provider(internet)
    faker.add_provider(date_time)
    faker.add_provider(misc)
    faker.add_provider(commerce_provider)
    faker.add_provider(address)
    faker.add_provider(lorem)

    return faker


def set_product_weight() -> int:
    return random.randint(1, 50)


def set_product_count() -> int:
    return random.randint(5, 30)


def set_waiting_room_weight() -> int:
    return random.randint(3000, 10000)


def set_waiting_room_stocks() -> int:
    return random.randint(5, 10)
