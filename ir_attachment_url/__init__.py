from . import models


def post_load():
    from .models import binary_fields
    from .models import image

    # in /controllers/main there is an import from the `mail` module
    # it leads to loading the mail and all its dependencies earlier than the patch in `binary_fields` is applied.
    # That is why the `from . import controller` line is here
    from . import controllers
