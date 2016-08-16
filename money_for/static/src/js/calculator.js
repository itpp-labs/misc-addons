$(document).ready(function(){
    if (!$('#calculator'))
        return;
    var type='x_in_amount';
    var recalc = function(){
        var x_currency_in_id = $('#x_currency_in_id').val();
        var x_currency_out_id = $('#x_currency_out_id').val();
        var x_in_amount = $('#x_in_amount').val();
        var x_out_amount = $('#x_out_amount').val();
        if (!(x_currency_out_id && x_currency_in_id && x_in_amount))
            return false;
        var values = {
            'x_currency_in_id':x_currency_in_id,
            'x_currency_out_id':x_currency_out_id,
        };
        if (type=='x_in_amount')
            values.x_in_amount = x_in_amount;
        else
            values.x_out_amount = x_out_amount;
        openerp.jsonRpc("/calculator/calc", 'call', values).then(function(data){
            if (!data)
                return;
            if (type=='x_in_amount')
                $('#x_out_amount').val(data.x_out_amount);
            else
                $('#x_in_amount').val(data.x_in_amount);
        });
    };
    $('#calculator #x_in_amount').focus(function(){
        type='x_in_amount';
    });
    $('#calculator #x_out_amount').focus(function(){
        type='x_out_amount';
    });
    $('#calculator input, #calculator select').on('change', function(e){
        recalc();
    });

    return;
    openerp.jsonRpc("/calculator/currencies", 'call', {}).then(function(data){
        if (!data)
            return;
        var val_in = $('#x_currency_in_id').attr('init-value');
        var val_out = $('#x_currency_out_id').attr('init-value');

        $('#x_currency_out_id, #x_currency_in_id').html(data);
        $('#x_currency_in_id').val(val_in);
        $('#x_currency_out_id').val(val_out);
    });

});
