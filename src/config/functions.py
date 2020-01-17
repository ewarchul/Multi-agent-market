import random


def const(time, dt, value):
    return value


def const_per_second(time, dt, value):
    return value * dt.total_seconds()


def random_uniform(time, dt, min, max):
    return random.uniform(min, max)


def random_uniform_per_second(time, dt, min, max):
    return random.uniform(min, max) * dt.total_seconds()


def random_integer(time, dt, min, max):
    return random.randint(min, max)


def random_integer_per_second(time, dt, min, max):
    return sum(random.randint(min, max) for _ in range(round(dt.total_seconds())))
