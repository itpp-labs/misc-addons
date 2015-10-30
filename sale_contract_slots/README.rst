Service selling in bulk
=======================

Description: This module provides an opportunity for your company to sell a service (e.g swimming pool attendance) in bulk.
You may sell for 6 or 12 or any other number (slots)  of the services at one go. One usage of your service by client is equal to one slot in the contract.
To sell in bulk you should create a bulk product in odoo (e.g. 'Six swimming pool attendance') and create a contract, using account analytical module.

In the sale order for bulk product you choose the contract. Available slots will be counted per contract then.

Also you should create a product with zero price and type "-1" in the slots field of the product. You sell this product each time
the client wants to use the slots in his contract.



Tested on Odoo 8.0 e84c01ebc1ef4fdf99865c45f10d7b6b4c4de229
