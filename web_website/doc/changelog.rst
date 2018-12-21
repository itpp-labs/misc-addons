`3.0.2`
-------
- **Fix:** Error related to incorrect SQL request

`3.0.1`
-------
- **Fix:** Incorrect website priority after odoo updates https://github.com/odoo/odoo/commit/b6d32de31e0e18a506ae06dc27561d1d078f3ab1

`3.0.0`
-------
- **New:** set website value automatically in case 1 company = 1 website

`2.1.4`
-------
- **New:** Computing default company in multi-website environment is moved to
  this module from website_multi_company
- **Fix:** Default value was updated for random field in _force_default method
- **Fix:** updating many2one field to empty value raised error
- **Fix:** Rare error on reading non-text fields

`2.1.3`
-------
- **Improvement:** better names in *Company Properties* menu

`2.1.2`
-------
- **Fix:** Error on creating record with non-empty value in website-depedent many2one field

`2.1.1`
-------
- **Fix:** Error on searching by website_dependent or company_dependent fields

`2.1.0`
-------
- **Fix:** fix API, which affects new modules
- **Improvement:** allow convert html fields to website-dependent ones

`2.0.0`
-------
- **Improvement:** Code is refactored to convert existing field to website-dependent one in a more easy way

`1.0.1`
-------
- **Fix:** Website Switcher didn't work for non-admin users

`1.0.0`
-------

- **Init version**
