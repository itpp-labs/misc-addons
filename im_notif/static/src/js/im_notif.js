 (function(){

     "use strict";

     var _t = openerp._t;
     var _lt = openerp._lt;
     var QWeb = openerp.qweb;

     openerp.im_chat.Conversation.include({
        escape_keep_url: function(str){
            //var url_regex = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/gi;
            var url_regex  = /((ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?|(<a)[^>]*href="([^"]*)"[^>]*>([^<]*)<\/a>)/gi;
            var last = 0;
            var txt = "";
            while (true) {
                var result = url_regex.exec(str);
                if (! result)
                    break;
                txt += _.escape(str.slice(last, result.index));
                last = url_regex.lastIndex;
                var href = '';
                var content = '';
                var is_odoo_ref = false;
                if (result[8]=='<a'){
                    href = result[9];
                    if (href[0]=='#'){
                        href += '&rnd='+parseInt(Math.random()*1000);
                        content = result[10];
                        is_odoo_ref = true;
                    } else {
                        //only internal urls are allowed
                        href = '';
                    }
                }else{
                    href = _.escape(result[0]);
                    content = href;
                }
                txt += '<a href="' + href + '"' + (is_odoo_ref?'':' target="_blank"')+'>' + content + '</a>';
            }
            txt += _.escape(str.slice(last, str.length));
            return txt;
        },
     });
 })();
