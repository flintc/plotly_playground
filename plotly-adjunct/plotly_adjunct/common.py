from webcolors import name_to_rgb


def line_color_theme(color):
    pink = name_to_rgb(color)
    pink_rgb_str = 'rgb({r}, {g}, {b})'.format(
        r=pink.red, g=pink.green, b=pink.blue)
    pink_rgba_str = 'rgba({r}, {g}, {b}, {a})'.format(
        r=pink.red, g=pink.green, b=pink.blue, a=0.25)
    pink_fill_rgba_str = 'rgba({r}, {g}, {b}, {a})'.format(
        r=pink.red, g=pink.green, b=pink.blue, a=0.2)
    pink_lines = dict(
        data=dict(
            scatter=[
                dict(
                    line=dict(
                        color=pink_rgb_str,
                    ),
                ),
                dict(
                    line=dict(
                        color=pink_rgba_str,
                    ),
                ),
                dict(
                    line=dict(color=pink_rgba_str),
                    fillcolor=pink_fill_rgba_str,
                )
            ]
        ),
    )
    #pio.templates['{}_lines'.format(color)] = pink_lines
    # return '{}_lines'.format(color)
    return pink_lines


def add_trace(src=(), figure=None, **kwargs):
    method = getattr(figure, 'add_{}'.format(kwargs['type']))
    trace = method()
    with figure.batch_update():
        for name, value in kwargs.items():
            config = flat_to_nested(name, src[value] if (
                isinstance(value, str) and value in src) else value)
            trace.update(config)
    return trace


def flat_to_nested(key, value):
    names = key.split('_')
    key = names.pop()
    d = {key: value}
    while len(names) > 0:
        key = names.pop()
        d = {key: d}
    return d


images_template = dict(layout=dict(
    images=[
        dict(
            name='background',
            xref="x",
            yref="y",
            x=0,
            y=0,
            layer="below",
            sizing="stretch",
        ),
        dict(
            name='watermark',
            xref='paper',
            yref='paper',
            x=.75,
            y=0.3,
            sizex=0.25,
            sizey=0.25,
            sizing="stretch",
            opacity=1,
            layer="below"
        )
    ]
))
