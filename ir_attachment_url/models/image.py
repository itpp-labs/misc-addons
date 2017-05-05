# -*- coding: utf-8 -*-
from odoo import tools
import re


super_image_resize_images = tools.image_resize_images


def updated_image_resize_images(vals, big_name='image', medium_name='image_medium', small_name='image_small'):
    """ Update ``vals`` with image fields resized as expected. """
    url = None
    if big_name in vals and is_url(vals[big_name]):
        url = vals[big_name]
    elif medium_name in vals and is_url(vals[medium_name]):
        url = vals[medium_name]
    elif small_name in vals and is_url(vals[small_name]):
        url = vals[small_name]

    if url:
        vals.update({big_name: url})
        vals.update({medium_name: url})
        vals.update({small_name: url})
    else:
        super_image_resize_images(vals, big_name, medium_name, small_name)


def is_url(value):
    if value:
        return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', value)


tools.image_resize_images = updated_image_resize_images
