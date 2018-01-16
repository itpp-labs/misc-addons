# -*- coding: utf-8 -*-
from . import models
from . import controllers


def post_load():
    from .models import binary_fields
    from .models import image
