Backend debranding + Support branding
=====================================

Fixes compatibility between two modules:

* web_debranding
* support_branding

By default, the module puts "Supported by ..." at backend footer. The label can be changed via translation tool:

* open Settings/Translations/Application Terms/Translated Terms (be sure that you have "Technical Features" tick in user access right settings.
* type "Supported by" (without quotes) and click "Search old source for: ..."
* set "Translation Value" e.g. to "Hosted by"
* click [Save]
* refresh page

Tested on Odoo 8.0 75f0c7df4dc016b5e0ace4db5b6487fc5a21632a
