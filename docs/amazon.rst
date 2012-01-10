========================
Installing on Amazon EC2
========================

Registering for EC2
===================

TODO

Configuring your Security Group
===============================

Before setting up your PANDA server, you will need to configure your security group so that web requests will reach be able to reach it.

To do this visit the "Security Groups" tab of the EC2 Management Console. Select "Inbound" and then adds rules for ``HTTP``, ``HTTPS`` and ``SSH``. If you don't mind your PANDA being accessible to anyone on the internet then you can enter ``0.0.0.0/0`` in the "Source" field for each. More discerning users may wish to enter a private IP or subnet assigned to their organization.

Installation
============

Method #1 - EC2, using an AMI
-----------------------------

This is the absolute simplest possible way to make a PANDA. Log into your EC2 Dashboard and click "Launch Instance". On the "Community AMIs" tab search for ``ami-77ab7c1e``. When the image comes up (it may take a moment), click "Select".

.. _notes above regarding instance types:

You'll need to select an **Instance Type**. You are welcome to use (and pay for) a more powerful server, but PANDA has been optimized with the expectation that most organizations will run it on an ``m1.small`` instance. (At a cost of roughly $70 per month.) This should provide adequate capacity for small to medium size groups. We don't recommend trying to run it on a ``t1.micro`` unless you'll only be using it for testing.

Leave all the other settings as their defaults and launch your instance.

Method #2 - EC2, using a user_data script
-----------------------------------------

This method is also very easy and has the advantage that you don't have to wait for an "official" PANDA release. If you want to run the latest code, this is the easiest way to do it!

Log into your EC2 Dashboard and click "Launch Instance". On the "Community AMIs" tab search for ``ami-a7f539ce``. This is the official Ubuntu 11.10 AMI. When the AMI appears in the list (it may take a moment), click "Select".

See the `notes above regarding instance types`_. We recommend you select ``m1.small``.

On the next page, under the "Advanced Instance Options" section, paste the following script into the **User Data** field:

.. code-block:: bash

    #!/bin/bash

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    bash setup_panda.sh

Leave all other settings as their defaults and launch your instance.

The disadvantage of this method is that you will need to wait while the setup script is run. This normally takes 15-20 minutes. You can periodically check to see if your instance is ready by visiting it's Public DNS name in your web browser. You'll find this name in the details pane when you select your instance from the list. It will look like this: ``ec2-50-16-157-39.compute-1.amazonaws.com``.

.. note::

    If you're familiar with EC2 user_data scripts, than you've probably realized that you could accomplish this same thing by SSHing into your new server and running the above commands with sudo. You're right! In fact this is exactly what we do in our guide to `Installing on your own hardware <self-install.html>`_. 

