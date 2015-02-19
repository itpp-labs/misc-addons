$(document).ready(function(){
    if (!$('#calculator'))
        return;
    var currency_list = [];
    var recalc = function(name){
        var cur;
        $.each(currency_list, function(){
            if (this.name==name){
                cur = this;
                return false;
            }
        })
        if (!cur)
            return;
        var cur_value = $('#calculator input[data-name="'+cur.name+'"]').val()
        cur_value = parseInt(cur_value || '0');

        $.each(currency_list, function(){
            if (this.name==name)
                return;
            var val = cur_value / cur.rate * this.rate;
            var valStr = val.toFixed(Math.ceil(Math.log(1.0 / this.rounding) / Math.log(10)));
            $('#calculator input[data-name="'+this.name+'"]').val(valStr)
        })
    }
    $('#calculator input[type="text"]').on('change', function(e){
        recalc($(this).attr('data-name'));
    });
    var names = [];
    $('#calculator input[type="text"]').each(function(){
        var c = $(this).attr('data-name');
        if (c)
            names.push(c)
    })

    openerp.jsonRpc("/calculator/currencies", 'call', {names:names}).then(function(data){
        if (!data)
            return;
        console.log('currencies', data);
        currency_list = data;
        $('#calculator input[data-name="EGP"]').val(1)
        recalc('EGP')
    });

});
