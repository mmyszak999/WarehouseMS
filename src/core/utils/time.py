import datetime
import random

def get_current_time():
    return datetime.datetime.now()


def set_employment_date_for_factory():
    return get_current_time() - datetime.timedelta(months=random.randint(1, 12))