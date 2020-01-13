import random


def const(time, dt, value):
    return value


def random_uniform(time, dt, min, max):
    return random.uniform(min, max)


def random_integer(time, dt, min, max):
    return random.randint(min, max)
