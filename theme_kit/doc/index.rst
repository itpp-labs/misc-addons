===========
 Brand kit
===========

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Install `Website login background <https://apps.odoo.com/apps/modules/9.0/website_login_background/>`__ module too, if you use *website*.

Configuration
=============

* `Enable technical features <https://odoo-development.readthedocs.io/en/latest/odoo/usage/technical-features.html>`__
* Open menu ``Settings / Brand Kit / Brand``
* Choose **Color Scheme** or create new one. To return default color scheme set empty value
* **Favicon**: type some name (e.g. *favicon*) and click *Create and Edit*

  * Choose **Type** (File or URL), then upload icon or specify url
* Click ``[Apply]``

To temporarly undo Color Scheme (e. g. if you have applied non-contrast background and text colors)

* Open browser console (F12 in Chrome)
* Type and click Enter:

    $('#custom_css').remove()

Examples of the use of custom JS and Less

* JS::

    $(document).ready(function(){
        var ribbon = $('<div class="test-ribbon"/>');
        $('body').append(ribbon);
        ribbon.html("Demo");
    })

* css::

    .test-ribbon{
        width: 200px;
        top: 25px;
        left: -50px;
        text-align: center;
        line-height: 50px;
        letter-spacing: 1px;
        color: darken(#f0f0f0, 5%);
        -webkit-transform: rotate(-45deg);
        -ms-transform: rotate(-45deg);
        -moz-transform: rotate(-45deg);
        -o-transform: rotate(-45deg);
        transform: rotate(-45deg);
        z-index: 9999;
        position: fixed;
        box-shadow: 0 0 3px rgba(0,0,0,.3);
        background: rgba(255,0,0,.6);
        pointer-events: none;
    }

    .test-ribbon b {
        font-size: 20px;
    }
