 (function(){

     "use strict";

     var _t = openerp._t;
     var _lt = openerp._lt;
     var QWeb = openerp.qweb;

     openerp.im_chat.Conversation.include({
        escape_keep_url: function(str){
            //var url_regex = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/gi;
            var url_regex  = /((ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?|ODOO_REF#[\w#!:.?+=&%@!\-\/]+)/gi;
            var last = 0;
            var txt = "";
            while (true) {
                var result = url_regex.exec(str);
                if (! result)
                    break;
                txt += _.escape(str.slice(last, result.index));
                last = url_regex.lastIndex;
                var is_odoo_ref = result[0].match(/^ODOO_REF/)
                var url = _.escape(result[0].replace(/^ODOO_REF/, ''));
                if (is_odoo_ref)
                    url += '&rnd='+parseInt(Math.random()*1000);
                txt += '<a href="' + url + '"' + (is_odoo_ref?'':' target="_blank"')+'>' + url + '</a>';
            }
            txt += _.escape(str.slice(last, str.length));
            return txt;
        },
     })
 })()