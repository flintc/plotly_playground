from itertools import starmap, chain
from functools import singledispatch


def is_leaf_strict(x):
    if not isinstance(x, (dict, list)):
        return True
    return False


def is_leaf(x):
    if is_leaf_strict(x):
        return True
    if isinstance(x, (dict, list)):
        if all(map(is_leaf_strict, x.values())):
            return True
    return False


def common_keys(d1, d2):
    return set(d1).intersection(set(d2))


def zip_with(strategy):
    def wrapper(l1, l2):
        return starmap(strategy, zip(l1, l2))
    return wrapper


def first(x, y):
    return y


def last(x, y):
    return y


OVERRIDE_STRATEGIES = {
    'layout': {
        'template': last,
        'xaxis': {
            'range': last
        },
        'yaxis': {
            'range': last
        }
    }
}


@singledispatch
def default_strategy(x, y):
    return y


@default_strategy.register(list)
def list_concat(l1, l2):
    print('here!!')
    # return list(chain.from_iterable(lists))
    return [*l1, *l2]


@default_strategy.register(dict)
def dict_merge(d1, d2):
    print(d1)
    print(d2)
    # return dict(list_concat(*[d.items() for d in dikts]))
    return dict(**d1, **d2)


def merge_deep(d1, d2, strategy=None, default=OVERRIDE_STRATEGIES):
    d = d1.copy()
    for key, item in d2.items():
        if key in d1:
            if isinstance(item, dict):
                if all(is_leaf(x) for x in [d1, d2]):
                    #d[key] = dict(**d1[key], **item)
                    if strategy is not None and key in strategy:
                        d[key] = dict(strategy[key](d1[key], item))
                    elif key in default:
                        d[key] = dict(default[key](d1[key], item))
                    else:
                        d[key] = default_strategy(d1[key], item)
                else:
                    out = merge_deep(
                        d1[key], item,
                        strategy=strategy[key] if strategy is not None and key in strategy else None,
                        default=default[key] if key in default else {})
                    d[key] = out
            elif isinstance(item, list):
                if strategy is not None and key in strategy:
                    d[key] = list(strategy[key](d1[key], item))
                elif key in default:
                    d[key] = list(default[key](d1[key], item))
                else:
                    d[key] = default_strategy(d1[key], item)
            else:
                if strategy is not None and key in strategy:
                    d[key] = strategy[key](d1[key], item)
                elif key in default:
                    d[key] = default[key](d1[key], item)
                else:
                    d[key] = default_strategy(d1[key], item)
        else:
            d[key] = item
    return d
