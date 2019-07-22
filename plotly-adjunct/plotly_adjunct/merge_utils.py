from functools import partial
from collections import namedtuple
from itertools import chain


def fmap(f, data):
    if isinstance(data, list):
        return [f(x) for x in data]
    if isinstance(data, dict):
        return {k: f(v) for (k, v) in data.items()}
    return data


def pair_fmap(f, data):
    if isinstance(data[0], (tuple, list)):
        return [f(x) for x in zip(*data)]
    if isinstance(data[0], dict):
        return {k: f((v, data[1][k])) for (k, v) in data[0].items()}
    return data


def pair_fmap_dict(f, data):
    if isinstance(data[0], dict):
        return {k: f((v, data[1][k])) for (k, v) in data[0].items()}
    return data


def cata_with(ffmap, f, data):
    # First, we recurse inside all the values in data
    def cata_on_f(x): return cata_with(ffmap, f, x)
    recursed = ffmap(cata_on_f, data)
    return f(recursed)


cata = partial(cata_with, fmap)
cata_pair = partial(cata_with, pair_fmap)
cata_pair_dict = partial(cata_with, pair_fmap_dict)
