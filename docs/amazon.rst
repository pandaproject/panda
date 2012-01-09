========================
Installing on Amazon EC2
========================

Getting ready
=============

Email
-----

Before you installing PANDA you're going to need access to an SMTP server for sending email. If you don't know what that is or you don't have easy access to one, please read our `guide to Email <email.html>`_.

Security groups
---------------

If you're going to be using EC2, you will need to configure your security group so that web requests will reach your PANDA server. To do this you'll need to visit the "Security Groups" tab of the EC2 Management Console. Select "Inbound" and then adds rules for ``HTTP``, ``HTTPS`` and ``SSH``. If you don't mind your PANDA being accessible to anyone then you can enter ``0.0.0.0/0`` for the source for each. More discerning users may wish to enter a private IP or subnet assigned to their organization.

Installation
============

Method #1 - EC2, using an AMI
-----------------------------

This is the absolute simplest possible way to make a PANDA...

TODO

Method #2 - EC2, using a user_data script
-----------------------------------------

This method is also very easy and has the advantage that you don't have to wait for an "official" PANDA release. If you want to run the latest code, this is the easiest way to do it!

Start a new EC2 server based Ubuntu 11.10 AMI ``ami-a7f539ce``. In the "Advanced Instance Options" section of the launch wizard, paste the following script into the "User Data" box:

.. code-block:: bash

    #!/bin/bash

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    bash setup_panda.sh

The disadvantage of this method is that you will need to wait while the setup script is run. This will probably take 15-20 minutes. You can periodically check to see if your instance is ready by visiting it's public DNS name in your web browser.

.. note::

    If you're familiar with EC2 user_data scripts, than you've probably realized that you could accomplish this same thing by SSHing into your new server and running the above commands with sudo. You're right! In fact this is exactly what we do in our guide to `Installing on your own hardware <self-install.html>`_. 

Configuration
=============

DNS
---

TODO

Email
-----

TODO

