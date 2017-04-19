# -*- coding: utf-8 -*-
from odoo import tools
import re


def image_resize_images(vals, big_name='image', medium_name='image_medium', small_name='image_small'):
    """ Update ``vals`` with image fields resized as expected. """
    url = None
    if big_name in vals:
        if not is_url(vals[big_name]):
            vals.update(tools.image_get_resized_images(vals[big_name],
                                                       return_big=True, return_medium=True, return_small=True,
                                                       big_name=big_name, medium_name=medium_name,
                                                       small_name=small_name,
                                                       avoid_resize_big=True, avoid_resize_medium=False,
                                                       avoid_resize_small=False))
        else:
            url = vals[big_name]
    elif medium_name in vals:
        if not is_url(vals[medium_name]):
            vals.update(tools.image_get_resized_images(vals[medium_name],
                                                       return_big=True, return_medium=True, return_small=True,
                                                       big_name=big_name, medium_name=medium_name, small_name=small_name,
                                                       avoid_resize_big=True, avoid_resize_medium=True,
                                                       avoid_resize_small=False))
        else:
            url = vals[medium_name]

    elif small_name in vals:
        if not is_url(vals[small_name]):
            vals.update(tools.image_get_resized_images(vals[small_name],
                                                       return_big=True, return_medium=True, return_small=True,
                                                       big_name=big_name, medium_name=medium_name, small_name=small_name,
                                                       avoid_resize_big=True, avoid_resize_medium=True,
                                                       avoid_resize_small=True))
        else:
            url = vals[small_name]
    if url:
        vals.update({big_name: url})
        vals.update({medium_name: url})
        vals.update({small_name: url})


def is_url(value):
    if value:
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', value)


tools.image_resize_images = image_resize_images
