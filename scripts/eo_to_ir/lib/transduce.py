from functools import reduce


def xd_map(map_func):
    def _map_xd(reducer):
        def _apply(init, x):
            return reducer(init, map_func(x))

        return _apply
    return _map_xd


def xd_filter(predicate):
    def _filter_xd(reducer):
        def _apply(init, x):
            if predicate(x):
                return reducer(init, x)
            else:
                return init

        return _apply
    return _filter_xd


def appender(init, x):
    init.append(x)
    return init


def compose(f, g):
    def _h(arg):
        return f(g(arg))
    return _h


def xd(*components):
    return reduce(compose, components)
