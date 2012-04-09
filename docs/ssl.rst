===============
Configuring SSL
===============

Getting your certificate
========================

If you've decided to host your PANDA on Amazon's EC2 service or anywhere else that is accessible over the public internet then you should secure your site with an SSL certificate. Broadly, there are two ways you might go about this.

Buying a certificate
--------------------

The best option is purchase a certificate from an official signing authority such as `VeriSign <http://www.verisign.com/ssl/buy-ssl-certificates/index.html>`_ or `Digicert <http://www.digicert.com/>`_. However, a fully validated SSL certificate can cost hundreds of dollars per year.

Fortunantely, for the purposes of PANDA you should be fine with a much less expensive "Domain Validation" only certificate. This are available from many DNS registrars, such as `Namecheap <http://www.namecheap.com/ssl-certificates/comodo.aspx>`_ as well as dedicated providers like `RapidSSL <http://www.rapidssl.com/>`_. Domain Validation certificates typically verify the email address in the WHOIS records of your domain registration and then issue instantly. Ideally, you wouldn't want to use one of these to secure a public website, but because PANDA is only used by members of your organization it is sufficient.

Once you've acquired a certificate you can copy it your server by running the following commands in the directory with the files:

.. code-block:: bash

    scp -i <MY_EC2_KEY.pem> <MY_CERT.crt> ubuntu@<MY_PANDA_SERVER.com>:~/panda.crt
    scp -i <MY_EC2_KEY.pem> <MY_KEY.key> ubuntu@<MY_PANDA_SERVER.com>:~/panda.key

Creating your own certificate
-----------------------------

If you are operating your PANDA in a no-budget environment, then you may choose to generate your own "self-signed" certificate instead. This will provide all the benefits of encryption to your users, however, **each user will need to click through a browser warning that the site is not verified**. You will need to explicitly communicate to your users that this error message is normal. (In most browers they will only see it once.)

SSH into your server and run these commands:

.. code-block:: bash

    # You'll be prompted for a passphrase.
    # Use anything, but remember what it is.
    openssl genrsa -des3 -out panda.key 1024

    # After entering your passphrase you'll be prompted for a
    # variety of information which you can either fill in or leave blank.
    openssl req -new -key panda.key -out panda.csr

    cp panda.key panda.key.org

    # You'll need your passphrase again here.
    openssl rsa -in panda.key.org -out panda.key
    openssl x509 -req -days 365 -in panda.csr -signkey panda.key -out panda.crt

    rm panda.csr
    rm panda.key.org

Installing your certificate
===========================

Once you've purchased or created a certificate you'll need to install both it and your signing key in the correct location:

.. code-block:: bash

    sudo mv panda.crt /etc/nginx/panda.crt
    sudo chown root:root /etc/nginx/panda.crt
    sudo chmod 644 /etc/nginx/panda.crt

    sudo mv panda.key /etc/nginx/panda.key
    sudo chown root:root /etc/nginx/panda.key
    sudo chmod 644 /etc/nginx/panda.key

Turning it on
=============

The last thing you'll need to do is reconfigure PANDA's webserver (Nginx) to use the new SSL certificate. Fortunantely, there is a one-size-fits-all solution for this. All you need to is SSH into your PANDA server and run the following commands:

.. code-block:: bash

    sudo wget https://raw.github.com/pandaproject/panda/0.1.3/setup_panda/nginx_ssl -O /etc/nginx/sites-available/panda
    sudo service nginx restart

Your PANDA should now redirect all unsecured requests to a secure ``https://`` url.
    
