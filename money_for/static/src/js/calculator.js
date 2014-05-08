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
			$('#x_out_amount').text(data.x_out_amount);
		});
	}
	$('#calculator input, #calculator select').on('change', function(e){
		recalc();
	});

	openerp.jsonRpc("/calculator/currencies", 'call', {}).then(function(data){
		if (!data)
			return;
		$('#x_currency_out_id, #x_currency_in_id').html(data);
	});

});
