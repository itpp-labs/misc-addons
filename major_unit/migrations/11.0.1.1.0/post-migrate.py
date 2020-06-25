
def migrate(cr, version):

    # update new name column
    cr.execute("""UPDATE product_product pp
            SET     name = pt.name
            FROM    product_template pt
            WHERE   pp.product_tmpl_id = pt.id
        """)
