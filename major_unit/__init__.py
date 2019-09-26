
from . import models
from . import report
from . import wizard
from . import models


def post_init_hook(cr, registry):

    # update new name column
    cr.execute("""UPDATE product_product pp
            SET     name = pt.name
            FROM    product_template pt
            WHERE   pp.product_tmpl_id = pt.id
        """)
