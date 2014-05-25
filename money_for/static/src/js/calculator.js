$(document).ready(function(){
	if (!$('#calculator'))
		return;
	var recalc = function(){
		var x_currency_in_id = $('#x_currency_in_id').val();
		var x_currency_out_id = $('#x_currency_out_id').val();
		var x_in_amount = $('#x_in_amount').val();
		if (!(x_currency_out_id && x_currency_in_id && x_in_amount))
			return false;
		openerp.jsonRpc("/calculator/calc", 'call', {
			'x_currency_in_id':x_currency_in_id,
			'x_currency_out_id':x_currency_out_id,
			'x_in_amount':x_in_amount
		}).then(function(data){
			if (!data)
				return;
			$('#x_out_amount').val(data.x_out_amount);
		});
	}
	$('#calculator input, #calculator select').on('change', function(e){
		recalc();
	});

	openerp.jsonRpc("/calculator/currencies", 'call', {}).then(function(data){
		if (!data)
			return;
        var val_in = $('#x_currency_in_id').attr('init-value');
        var val_out = $('#x_currency_out_id').attr('init-value');

		$('#x_currency_out_id, #x_currency_in_id').html(data);
        $('#x_currency_in_id').val(val_in)
        $('#x_currency_out_id').val(val_out)
	});

});
