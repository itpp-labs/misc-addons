// Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
odoo.define('web_website.SwitchWebsiteMenu', function(require) {
"use strict";

var config = require('web.config');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var core = require('web.core');

var _t = core._t;

var SwitchWebsiteMenu = Widget.extend({
    template: 'SwitchWebsiteMenu',
    events: {
        'click .dropdown-item[data-menu]': '_onClick',
    },
    init: function () {
        this._super.apply(this, arguments);
        this.isMobile = config.device.isMobile;
        this._onClick = _.debounce(this._onClick, 1500, true);
    },
    willStart: function() {
        if (!session.user_websites) {
            return $.Deferred().reject();
        }
        return this._super();
    },
    start: function() {
        var self = this;
        var all_websites_text = _t('All Websites');
        var topbar = self.$('.oe_topbar_name');
        var current_website = session.user_websites.current_website;

        var websites_list = '';

        if (this.isMobile) {
            websites_list = '<li class="bg-info">' +
                _t('Tap on the list to change website') + '</li>';
        } else if (current_website){
            self.$('.oe_topbar_name').text(current_website[1]);
        } else {
            self.$('.oe_topbar_name').html('<em>' + all_websites_text + '</em>');
        }

        var websites = session.user_websites.allowed_websites;
        websites.unshift(false);
        _.each(websites, function(website) {
            var a = '';
            if ((!website && !current_website) || website[0] === session.user_websites.current_website[0]) {
                a = '<i class="fa fa-check mr8"></i>';
            } else {
                a = '<span class="o_company"/>';
            }
            if (website){
                websites_list += '<a href="#" class="dropdown-item" data-menu="website" data-website-id="' + website[0] + '">' + a + website[1] + '</a>';
            } else {
                websites_list += '<a href="#" class="dropdown-item all_websites" data-menu="website">' + a + '<em>' + all_websites_text + '</em></a>';
            }
        });
        self.$('.dropdown-menu').html(websites_list);
        return this._super();
    },
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    _onClick: function (ev) {
        ev.preventDefault();
        // write method ignores undefinded
        var website_id = $(ev.currentTarget).data('website-id') || false;
        this._rpc({
            model: 'res.users',
            method: 'write',
            args: [[session.uid], {'backend_website_id': website_id}],
        }).then(function() {
            location.reload();
        });
    },
});

SystrayMenu.Items.push(SwitchWebsiteMenu);

return SwitchWebsiteMenu;

});
