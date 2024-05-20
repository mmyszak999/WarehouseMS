import random

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
