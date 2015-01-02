$(document).ready(function () {
    var page_product_id = $('input.product_id').val();//for page of a product
    if (!page_product_id && !$('#products_grid_before'))
        return;
    if (page_product_id && ! $('#add_to_cart').attr('quick-add-to-cart') || $('#cart_products') )
        return;
    var update_json = $.Deferred();
    update_json.resolve();
    $(".oe_website_sale input.js_quantity").change(function () {
        var $input = $(this);
        update_json = update_json.then(function(){
            var value = parseInt($input.val(), 10);
            if (isNaN(value)) value = 0;
            return openerp.jsonRpc("/shop/cart/update_json", 'call', {
                'line_id': parseInt($input.data('line-id'),10),
                'product_id': parseInt($input.data('product-id') || $('input.product_id').val(),10),
                'set_qty': value})
            .then(function (data) {
                if (!data.quantity) {
                    location.reload();
                    return;
                }
                var $q = $(".my_cart_quantity");
                $q.parent().parent().removeClass("hidden", !data.quantity);
                $q.html(data.cart_quantity).hide().fadeIn(600);
                //$input.val(data.quantity);
                $("#cart_total").replaceWith(data['website_sale.total']);
            })
        })
    });
    /*
    $('.oe_website_sale .oe_product_cart .oe_product_image a').on('click', function (ev) {
        //ev.preventDefault();
        var $input = $(ev.currentTarget).parent().parent().find("input");
        $input.val(1 + parseFloat($input.val(),10));
        $input.change();
        $input.css('background-color', '#428bca').stop().animate({backgroundColor:'white'}, 500)
        return false;
    });
    */

    if (page_product_id)
        $('input.js_quantity').val(0);
    openerp.jsonRpc("/shop/get_order_numbers", 'call').then(function(data){
        if (!data)
            return;
        $.each(data, function(product_id, num){
            if (page_product_id){
                if (page_product_id == product_id){
                    $('input.js_quantity').val(num);
                }
            } else
                $('input[data-product-id="'+product_id+'"]').val(num)
        })
    })

})