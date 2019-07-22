import yaml
import plotly.io as pio
import os
import plotly.graph_objs as go
from PIL import Image
import shapely.geometry as geom
from .utils import merge_deep
from .interact import InteractMixin
from jinja2 import Template
import plotly.io as pio
from .images import img_to_b64
from .merge_utils import cata_pair_dict
from itertools import chain


def register_templates():
    with open(os.path.join(os.path.dirname(__file__), 'templates.yml'), 'r') as f:
        templates = yaml.load(f)
        for key, t in templates.items():
            print(key)
            pio.templates[key] = t


def axis_equal(fig):
    fig.layout.update(
        yaxis=dict(
            scaleanchor='x',
            scaleratio=1,
        )
    )


def background_image(img):
    return {
        'templateitemname': 'background',
        'source': img,
        'sizex': img.size[0]-1,
        'sizey': img.size[1]-1,
    }


def _imshow(img):
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    return {
        'data': [{
            'x': [0, img.size[0], img.size[0], 0, 0],
            'y': [0, 0, img.size[1], img.size[1], 0],
            'hoveron': 'fills',
            'marker': {
                'color': 'rgba(0,0,0,0)'
            },
            'line': {
                'color': 'rgba(0,0,0,0)'
            },
            'showlegend': False,
        }],
        'layout': {
            'template': 'images',
            'images': [
                background_image(img)
            ],
            'xaxis': {
                'range': [0, img.size[0]],
            },
            'yaxis': {
                'range': [img.size[1], 0],
            },
        }
    }


def imshow(img):
    if not isinstance(img, Image.Image):
        img = Image.fromarray(img)
    return go.FigureWidget(
        layout={
            'template': 'images',
            'images': [
                background_image(img)
            ],
            'xaxis': {
                'range': [0, img.size[0]],
            },
            'yaxis': {
                'range': [img.size[1], 0],
            },
        }
    )


def max_extent(x, y):
    if x[0] < x[1]:
        return [min(x[0], y[0]), max(x[1], y[1])]
    return [max(x[0], y[0]), min(x[1], y[1])]


_MERGE_IMAGES = {
    'layout': {
        'xaxis': {
            'range': max_extent,
        },
        'yaxis': {
            'range': max_extent,
        }
    }
}


def _concat_images(x):
    try:
        if isinstance(x[1][0], go.layout.Image):
            out = tuple(map(go.layout.Image, chain.from_iterable(x)))
            return out
    except:
        try:
            if isinstance(x[1], tuple):
                return (go.layout.Image(x[0][0]),)
        except:
            try:
                return x[0]
            except:
                return x
    try:
        return x[0]
    except:
        return x


class ImshowMixin:
    def add_background_image(self, img, **kwargs):
        images = yaml.load(render_template('background_image',
                                           img=img_to_b64(img), sz=img.size))
        merged = cata_pair_dict(_concat_images, (images, self))
        self.update(merged)
        self.layout.images = merged['layout']['images']
        self.update(kwargs)

    def axis_equal(self):
        self.layout.xaxis.constrain = 'domain'
        axis_equal(self)


def xy_from_polygon(box):
    return dict(zip(('x', 'y'), zip(*(box.exterior.coords))))


def box_cxcywh_toxxyy(cx, cy, w, h):
    return (cx-w/2, cy-h/2, cx+w/2, cy+h/2)


def box_xywh_toxxyy(x, y, w, h):
    return (x, y, x+w, y+h)


class PolygonMixin:
    def add_bbox_xxyy(self, minx, miny, maxx, maxy, **kwargs):
        print(minx, miny, maxx, maxy)
        return self.add_scatter(
            **xy_from_polygon(geom.box(minx, miny, maxx, maxy)),
            **kwargs,
            hoveron='fills',
        )

    def add_bbox_cxcywh(self, cx, cy, w, h, **kwargs):
        return self.add_bbox_xxyy(
            box_cxcywh_toxxyy(cx, cy, w, h),
            **kwargs
        )

    def add_bbox_xywh(self, x, y, w, h, **kwargs):
        return self.add_bbox_xxyy(
            box_xywh_toxxyy(x, y, w, h),
            **kwargs
        )

    def add_bbox(self, *args, bbox_mode='xywh', **kwargs):
        if bbox_mode == 'xxyy':
            return self.add_bbox_xxyy(*args, **kwargs)
        if bbox_mode == 'cxcywh':
            return self.add_bbox_cxcywh(*args, **kwargs)
        if bbox_mode == 'xywh':
            return self.add_bbox_xywh(*args, **kwargs)
        raise NotImplementedError(
            'BBox Mode: {} not implemented'.format(bbox_mode))


class FigureWidget(go.FigureWidget, ImshowMixin, PolygonMixin, InteractMixin):
    pass


def render_template(name, **kwargs):
    with open(os.path.join(os.path.dirname(__file__), 'templates', '{}.yml'.format(name)), 'r') as f:
        t = f.read()
    #pio.templates[name] = yaml.load(Template(t).render(**kwargs))
    return Template(t).render(**kwargs)
    # return Template(t).render(**kwargs)


def register_template(name, template):
    pio.templates[name] = yaml.load(template)
