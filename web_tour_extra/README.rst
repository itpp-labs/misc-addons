Extended tours
==============

Extra features for tours:

* Fixes issue with running Tour in specific backend page. For example, without this module it's impossible to start Tour from ``/web#id=3&view_type=form&model=res.partner``, the hash will be cleaned and Tour begins from ``/web#`` page.

  * to use it in ir.action.todo add something to url instead of using simple ``/web#`` url, because page has to be reloded, e.g.::

      <record id="res_partner_mails_count_tutorial" model="ir.actions.act_url">
          <field name="name">res_partner_mails_count Tutorial</field>
          <field name="url" eval="'/web?res_partner_mails_count=tutorial#id='+str(ref('base.partner_root'))+'&amp;view_type=form&amp;model=res.partner&amp;/#tutorial_extra.mails_count_tour=true'"/>
      </record>

    if you are developer, don't forget to change url ``/web?res_partner_mails_count=tutorial#...`` back to ``/web#...`` whenever you want to relaunch the Tour (usually by uninstalling and installing your module).

* fix ignoring step's title if there is title in step's element
