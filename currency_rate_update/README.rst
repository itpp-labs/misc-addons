*Supported version of this module is available here:* https://github.com/OCA/account-financial-tools/tree/8.0/currency_rate_update

The module is able to use 4 different sources:

1. Admin.ch
   Updated daily, source in CHF.

2. European Central Bank (ported by Grzegorz Grzelak)
   The reference rates are based on the regular daily concertation procedure between
   central banks within and outside the European System of Central Banks,
   which normally takes place at 2.15 p.m. (14:15) ECB time. Source in EUR.
   http://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html

3. Yahoo Finance
   Updated daily

4. Polish National Bank (Narodowy Bank Polski) (contribution by Grzegorz Grzelak)
   Takes official rates from www.nbp.pl. Adds rate table symbol in log.
   You should check when rates should apply to bookkeeping. If next day you should
   change the update hour in schedule settings because in OpenERP they apply from
   date of update (date - no hours).
   
5. Banxico for USD & MXN (created by Agustín Cruz)
   Updated daily

In the roadmap : Google Finance.
   Updated daily from Citibank N.A., source in EUR. Information may be delayed.
   This is parsed from an HTML page, so it may be broken at anytime.

The update can be set under the company form.
You can set for each services which currency you want to update.
The logs of the update are visible under the service note.
You can active or deactivate the update.
The module uses internal ir_cron feature from OpenERP, so the job is launched once
the server starts if the 'first execute date' is before the current day.
The module supports multi-company currency in two ways:

*    the currencies are shared, you can set currency update only on one 
    company
*    the currency are separated, you can set currency on every company
    separately

A function field lets you know your currency configuration.

If in multi-company mode, the base currency will be the first company's currency
found in database.

Thanks to main contributors: Grzegorz Grzelak, Alexis de Lattre

Tested by Ivan Yelizariev on Odoo 8.0 d023c079ed86468436f25da613bf486a4a17d625

Maintainers
------------
This module is not maintainable since Odoo 9.0, because lack of interests from customers.
