=====================
Production deployment
=====================

Getting ready: email
====================

Before you configure PANDA you're going to need access to an SMTP server for sending email.

If you're organization already has one of these that you can use then you just need to make sure you have the address, username and password handy so you can fill them in later. 

If you don't have access to an email server you'll need to set one up. The easiest way to do this is to use a service. We recommend `Sendgrid <http://sendgrid.com>`_, because they offer a free plan for less than 200 emails a day and the stay affordable if and when you exceed that limit.

If you decide to use Sendgrid you can follow our :doc:`instructions_ for setting it up getting the information you need </sendgrid>`.

Setting up the server
=====================

Get hold of an Ubuntu 11.10 server--an EC2 small based off of ami-a7f539ce works well. SSH into your server and run::

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    sudo bash setup_panda.sh

Your new PANDA server should now be serving on port 80. (Ensure port 80 is open in your security group.)

TODO: configure email.

