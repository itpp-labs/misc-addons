$(document).ready(function () {
if (! $('#cart_products') )
    return;
$('.oe_website_sale').each(function () {
    var oe_website_sale = this;

    $(oe_website_sale).on("change", ".oe_cart input.js_quantity", function () {
        setTimeout(function(){
            openerp.jsonRpc("/website_sale_special_offer/get_cart_lines", 'call', {
            }).then(function (data){
                $.each(data, function(key, line){
                    var $tr = $('.js_quantity[data-line-id='+line.id+']').parent().parent().parent()
                    $tr.find("[name='price_total']").html(line.price_subtotal)
                })
            })
        }, 1000)
    })
})
})
