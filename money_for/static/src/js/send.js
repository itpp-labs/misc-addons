$(document).ready(function(){
    /*
    var validated;
    $('#send_money_form').submit(function(event){
        event.preventDefault();
        validated = true;
        console.log('validated');
    });
*/

    $('.m-multilist__item-header').on('click', function(event){
        var index = 1 + $(this).parent().index();
        if (index==1)
            return true;

        var p = $('#send_money_form').parsley();
        if (index==2 && p.isValid('g1'))
            return true;

        if (index==3 && p.isValid('g2'))
            return true;

        p.validate();
        event.stopImmediatePropagation()
    })
})