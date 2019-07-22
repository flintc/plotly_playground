from functools import partial
from collections import namedtuple
import ipywidgets as widgets
from itertools import chain


def fmap(f, data):
    if isinstance(data, list):
        return [f(x) for x in data]
    if isinstance(data, dict):
        return {k: f(v) for (k, v) in data.items()}
    return data


def pair_fmap(f, data):
    if isinstance(data[0], list):
        return [f(x) for x in zip(*data)]
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

DynamicValue = namedtuple('DynamicValue', 'data controller register')


def resolve_value(item):
    if isinstance(item, DynamicValue):
        return item.data
    return item


def clip_x_max(change, fig, trace, data):
    with fig.batch_animate(duration=50):
        trace.x = data['x'][data['x'] < change['new']]
        trace.y = data['y'][data['x'] < change['new']]
        fig.data[0].line.color = 'red'


def make_interactor(widget_factory, on_change):
    def interactor(data, kwargs=None):
        widget = widget_factory(data)
        value = dict(**data, **kwargs) if kwargs is not None else data

        def register(trace, fig):
            widget.observe(partial(on_change, data=data,
                                   trace=trace, fig=fig), names='value')
        # return {'x': DynamicValue(data.x, widget, register), 'y': DynamicValue(data.y, widget, register)}
        return DynamicValue(value, widget, register)
    return interactor


use_clip_x_max = make_interactor(
    lambda data: widgets.FloatSlider(min=min(data['x']), max=max(data['x']),
                                     value=max(data['x']), description='x max'),
    clip_x_max
)


def splatargs(fn):
    def wrapper(args):
        return fn(*args)
    return wrapper


class InteractMixin:
    @classmethod
    def interactive(cls, fig_def):
        foo = cata(resolve_value, fig_def)
        fig = cls(cata(resolve_value, foo))
        fig._interact_widgets = ()
        bar = cata_pair(splatargs(fig.register_interactor), (fig_def, fig))
        print('bar2', bar)
        cata_pair(splatargs(fig.register_interactor), (bar, fig))
        return fig

    def register_interactor(self, value, trace=None, *args):
        if trace is not None:
            if isinstance(value, DynamicValue):
                value.register(trace, self)
                self._interact_widgets = self._interact_widgets + \
                    (value.controller,)
                #print('value?', value.data)
                return value.data
            return value, trace
        return value, trace

    def is_interactive(self):
        return hasattr(self, '_interact_widgets')

    def _make_widgetbox(self):
        return widgets.VBox([*self._interact_widgets, self])

    def interact(self):
        return self._make_widgetbox() if self.is_interactive else ()
