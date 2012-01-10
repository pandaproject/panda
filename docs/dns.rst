===============
Configuring DNS
===============

Getting a domain name
---------------------

To use a custom domain with your PANDA you will first need to purchase one from a registrar such as `Namecheap <http://www.namecheap.com/>`_ or `dnsimple <https://dnsimple.com/>`_. Once you've purchased a domain you'll want to point it at your PANDA.

.. note::

    If your using Amazon EC2 you will now want to setup an "Elastic IP" for your instance. This will give you a permanant address for your server. To do this, visit the EC2 Dashboard and click "Elastic IPs" in the left-hand rail. Click "Allocate New Address" in the toolbar and then "Yes, Allocate". Select the new IP address in the list and click "Associate Address" in the toolbar. Select your PANDA instance from the drop-down and click "Yes, Associate." You'll use this new IP address in the next step.

Create an ANAME record for your new domain, pointed to your server's IP address. The details of how to do this will depend on your registrar, but typically it's as simple as pasting the IP address into the correct box and clicking save. It may take some time for your domain to become available, but frequently it is instantaneous. Trying visiting your new domain in your web browser and PANDA should load. If it does not, wait a while and try again.

Configuring PANDA
-----------------

Once you have your new domain name directed to your PANDA you'll want to configure outbound email to use the new domain. You can do this on the settings page::

    http://localhost:8000/admin/settings

Replace ``localhost:8000`` with your PANDA's domain name.

You'll be prompted to login. If this is you're first time you can use the default username, ``panda@pandaproject.net`` and the default password ``panda``.

Once you've logged you'll see a list of configuration options. In the section titled "Site domain settings", fill in your new domain name and click "Update Settings".

To test the new domain name click the "Home" link at the top of the screen and then the link to "Add" a new User. Fill in your own email address and click Save. You should get an activation email in your inbox. Click the activation link and verify that you return to your PANDA.

