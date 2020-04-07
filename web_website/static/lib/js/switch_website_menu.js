// Copyright 2018,2020 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
/* eslint-disable */
odoo.define('web.SwitchWebsiteMenu', function(require) {
"use strict";

/**
 * When Odoo is configured in multi-website mode, users should obviously be able
 * to switch their interface from one website to the other.  This is the purpose
 * of this widget, by displaying a dropdown menu in the systray.
 */

var config = require('web.config');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');
var utils = require('web.utils');
require('web_website.session');
require('web_website.web_client');

var SwitchWebsiteMenu = Widget.extend({
    // This code must be in AbstractWebClient, but Odoo doesn't really allow to extend it
    update_user_websites_context: function () {
        var state = $.bbq.getState();
        // If not set on the url, retrieve wids from the local storage
        // of from the default website on the user
        var current_website_id = session.user_websites.current_website[0];
        if (!state.wids) {
            state.wids = utils.get_cookie('wids') !== null ? utils.get_cookie('wids') : String(current_website_id);
        }
        var stateWebsiteIDS = _.map(state.wids.split(','), function (wid) { return parseInt(wid); });
        var userWebsiteIDS = _.map(session.user_websites.allowed_websites, function(website) {return website[0];});
        // Check that the user has access to all the websites
        if (!_.isEmpty(_.difference(stateWebsiteIDS, userWebsiteIDS))) {
            state.wids = String(current_website_id);
            stateWebsiteIDS = [current_website_id];
        }
        // Update the user context with this configuration
        session.user_context.allowed_website_ids = stateWebsiteIDS;
        $.bbq.pushState(state);
    },


    template: 'SwitchWebsiteMenu',
    events: {
        'click .dropdown-item[data-menu] div.log_into': '_onSwitchWebsiteClick',
        'keydown .dropdown-item[data-menu] div.log_into': '_onSwitchWebsiteClick',
        'click .dropdown-item[data-menu] div.toggle_website': '_onToggleWebsiteClick',
        'keydown .dropdown-item[data-menu] div.toggle_website': '_onToggleWebsiteClick',
    },
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.isMobile = config.device.isMobile;
        this._onSwitchWebsiteClick = _.debounce(this._onSwitchWebsiteClick, 1500, true);
    },

    /**
     * @override
     */
    willStart: function () {
        this.update_user_websites_context();
        var self = this;
        this.allowed_website_ids = String(session.user_context.allowed_website_ids)
                                    .split(',')
                                    .map(function (id) {return parseInt(id);});
        this.user_websites = session.user_websites.allowed_websites;
        this.current_website = this.allowed_website_ids[0];
        this.current_website_name = _.find(session.user_websites.allowed_websites, function (website) {
            return website[0] === self.current_website;
        })[1];
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     */
    _onSwitchWebsiteClick: function (ev) {
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var dropdownMenu = dropdownItem.parent();
        var websiteID = dropdownItem.data('website-id');
        var allowed_website_ids = this.allowed_website_ids;
        if (dropdownItem.find('.fa-square-o').length) {
            // 1 enabled website: Stay in single website mode
            if (this.allowed_website_ids.length === 1) {
                if (this.isMobile) {
                    dropdownMenu = dropdownMenu.parent();
                }
                dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                allowed_website_ids = [websiteID];
            } else { // Multi website mode
                allowed_website_ids.push(websiteID);
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            }
        }
        $(ev.currentTarget).attr('aria-pressed', 'true');
        session.setWebsites(websiteID, allowed_website_ids);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     */
    _onToggleWebsiteClick: function (ev) {
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var websiteID = dropdownItem.data('website-id');
        var allowed_website_ids = this.allowed_website_ids;
        var current_website_id = allowed_website_ids[0];
        if (dropdownItem.find('.fa-square-o').length) {
            allowed_website_ids.push(websiteID);
            dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked', 'true');
        } else {
            allowed_website_ids.splice(allowed_website_ids.indexOf(websiteID), 1);
            dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked', 'false');
        }
        session.setWebsites(current_website_id, allowed_website_ids);
    },

});

if (session.display_switch_website_menu) {
    SystrayMenu.Items.push(SwitchWebsiteMenu);
}

return SwitchWebsiteMenu;

});
