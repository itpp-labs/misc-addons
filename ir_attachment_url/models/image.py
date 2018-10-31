from odoo import tools
import re


super_image_resize_images = tools.image_resize_images


def updated_image_resize_images(vals, big_name='image', medium_name='image_medium', small_name='image_small', sizes=None):
    """ Update ``vals`` with image fields resized as expected. """
    if not sizes:
        sizes = {}

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
        super_image_resize_images(vals, big_name, medium_name, small_name, sizes=sizes)


def is_url(value):
    if value:
        return isinstance(value, str) and re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', value)


super_image_resize_image = tools.image_resize_image


def updated_image_resize_image(base64_source, size=(1024, 1024), encoding='base64', filetype=None, avoid_if_small=False):
    source_for_check = base64_source.decode("utf-8") if isinstance(base64_source, bytes) else base64_source
    if is_url(source_for_check):
        return source_for_check
    return super_image_resize_image(base64_source, size=size, encoding=encoding, filetype=filetype, avoid_if_small=avoid_if_small)


def updated_image_resize_image_big(base64_source, size=(1024, 1024), encoding='base64', filetype=None, avoid_if_small=True):
    """ copy-pasted from odoo/tools/image.py::image_resize_image_big
        because we rewrite image_resize_image function.
    """
    return updated_image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)


def updated_image_resize_image_medium(base64_source, size=(128, 128), encoding='base64', filetype=None, avoid_if_small=False):
    """ copy-pasted from odoo/tools/image.py::image_resize_image_medium
        because we rewrite image_resize_image function.
    """
    return updated_image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)


def updated_image_resize_image_small(base64_source, size=(64, 64), encoding='base64', filetype=None, avoid_if_small=False):
    """ copy-pasted from odoo/tools/image.py::image_resize_image_small
        because we rewrite image_resize_image function.
    """
    return updated_image_resize_image(base64_source, size, encoding, filetype, avoid_if_small)


def updated_image_get_resized_images(base64_source, return_big=False, return_medium=True, return_small=True,
                                     big_name='image', medium_name='image_medium', small_name='image_small',
                                     avoid_resize_big=True, avoid_resize_medium=False, avoid_resize_small=False):
    """ copy-pasted from odoo/tools/image.py::image_get_resized_images
        because we rewrite image_resize_image function.
    """
    return_dict = dict()
    if isinstance(base64_source, tools.pycompat.text_type):
        base64_source = base64_source.encode('ascii')
    if return_big:
        return_dict[big_name] = updated_image_resize_image_big(base64_source, avoid_if_small=avoid_resize_big)
    if return_medium:
        return_dict[medium_name] = updated_image_resize_image_medium(base64_source, avoid_if_small=avoid_resize_medium)
    if return_small:
        return_dict[small_name] = updated_image_resize_image_small(base64_source, avoid_if_small=avoid_resize_small)
    return return_dict


tools.image_resize_images = updated_image_resize_images
tools.image_resize_image = updated_image_resize_image
tools.image_resize_image_big = updated_image_resize_image_big
tools.image_resize_image_medium = updated_image_resize_image_medium
tools.image_resize_image_small = updated_image_resize_image_small
tools.image_get_resized_images = updated_image_get_resized_images
