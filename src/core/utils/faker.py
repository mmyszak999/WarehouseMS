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
    return random.randint(1, 10)


def set_product_count() -> int:
    return random.randint(2, 10)


def set_waiting_room_weight() -> int:
    return random.randint(400, 5000)


def set_waiting_room_stocks() -> int:
    return random.randint(5, 10)


def set_max_waiting_rooms() -> int:
    return random.randint(6, 9)


def set_max_sections() -> int:
    return random.randint(4, 6)


def set_max_section_weight() -> int:
    return random.randint(5000, 15000)


def set_max_racks() -> int:
    return random.randint(4, 7)


def set_rack_weight() -> int:
    return random.randint(400, 1000)


def set_rack_levels() -> int:
    return random.randint(2, 4)


def set_rack_level_slots() -> int:
    return random.randint(2, 4)


def set_rack_level_weight() -> int:
    return random.randint(70, 150)
