odoo.define('web_debranding.UserMenu', function (require) {
    "use strict";

    require('web_debranding.base');
    var session = require('web.session');
    var core = require('web.core');
    var _t = core._t;


    var UserMenu = require('web.UserMenu');
    UserMenu.include({
        _onMenuDebug: function(){
            if (session.debug && session.debug !== 'assets'){
                return console.log(_t('Developer mode is already activated'));
            }
            window.location = $.param.querystring(window.location.href, 'debug');
        },
        _onMenuDebugassets: function(){
            if (session.debug === 'assets'){
                return console.log(_t('Developer mode is already activated'));
            }
            window.location = $.param.querystring(window.location.href, 'debug=assets');
        }
    });
});
