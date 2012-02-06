========================
Installing on Amazon EC2
========================

Registering for EC2
===================

If you don't already have an Amazon Web Services account you will need to register for one and setup your credentials. Visit the `EC2 homepage <http://aws.amazon.com/ec2/>`_ and follow the "Sign Up Now" link.

.. note::

    Although every effort has been made to make this process as streamlined as possible, if you've never used a setup a server before, you may find it rather daunting. In this case we suggest pairing up with a engineer until your through the setup process.

Configuring your Security Group
===============================

Before setting up your PANDA server, you will need to configure your security group so that web requests will reach be able to reach it.

To do this visit the `Security Groups tab <https://console.aws.amazon.com/ec2/home?#s=SecurityGroups>`_ of the EC2 Management Console. Select the "default" security group from the list and then click the "Inbound" tab in the bottom pane of the window. Add rules for ``HTTP``, ``HTTPS`` and ``SSH``. If you don't mind your PANDA being accessible to anyone on the internet then you can enter ``0.0.0.0/0`` in the **Source** field for each. More discerning users may wish to enter a private IP or subnet assigned to their organization.

.. note::

    If you're not sure what to enter for the **Source** field it would be wise to consult with your IT department to find out if your organization has a private subnet.

Installation
============

Method #1 - EC2, using an AMI
-----------------------------

This is the absolute simplest possible way to make a PANDA. Visit the `Instances tab <https://console.aws.amazon.com/ec2/home?#s=Instances>`_ and click "Launch Instance". Select "Launch Class Wizard" and click "Continue". Click the "Community AMIs" tab and search for ``ami-77ab7c1e``. It may take a moment to return a result. When it does, click "Select".

.. _notes above regarding instance types:

On the next page you'll need to select an **Instance Type**. You are welcome to use (and pay for) a more powerful server, but PANDA has been optimized with the expectation that most organizations will run it on an ``m1.small`` instance. (At a cost of roughly $70 per month.) This should provide adequate capacity for small to medium size groups. We don't recommend trying to run it on a ``t1.micro`` unless you'll only be using it for testing.

Once you've select your instance type click "Continue". Keep clicking "Continue" and accepting all the default options until the "Continue" button becomes a "Launch button". Click "Launch".

Method #2 - EC2, using a user_data script
-----------------------------------------

This method is also very easy and has the advantage that you don't have to wait for an "official" PANDA release. If you want to run the latest code, this is the easiest way to do it!

Visit the `Instances tab <https://console.aws.amazon.com/ec2/home?#s=Instances>`_ and click "Launch Instance". Select "Launch Class Wizard" and click "Continue". Click the "Community AMIs" tab and search for ``ami-a7f539ce``. This is the official Ubuntu 11.10 AMI. It may take a moment to return a result. When it does, click "Select".

On the next page you'll need to select an **Instance Type**. See the `notes above regarding instance types`_. We recommend you select ``m1.small``.

On the next page, under the "Advanced Instance Options" section, paste the following script into the **User Data** field:

.. code-block:: bash

    #!/bin/bash

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    bash setup_panda.sh

Click "Continue". Keep clicking "Continue" and accepting all the default options until the "Continue" button becomes a "Launch button". Click "Launch".

The disadvantage of this method is that you will need to wait while the setup script is run. This normally takes 15-20 minutes. You can periodically check to see if your instance is ready by visiting it's Public DNS name in your web browser. You'll find this name in the bottom pane of the window after selecting your instance on the `Instances tab <https://console.aws.amazon.com/ec2/home?#s=Instances>`_. It will look like this: ``ec2-50-16-157-39.compute-1.amazonaws.com``.

.. note::

    If you're familiar with EC2 user_data scripts, than you've probably realized that you could accomplish this same thing by SSHing into your new server and running the above commands with sudo. You're right! In fact this is exactly what we do in our guide to `Installing on your own hardware <self-install.html>`_. 

