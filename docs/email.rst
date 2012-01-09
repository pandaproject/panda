=====
Email
=====

Before you configure PANDA you're going to need access to an SMTP server for sending email. There are several ways you can get access to one of these.

Using a Private SMTP
====================

If you're organization already has an SMTP server then you may be able to use it for PANDA. Note, however, that if you host PANDA on EC2 and your SMTP server is internal to your organization you may not be able to reach it. It's best to discuss this possibility with the IT staff in charge of your email servers.

If you can use your own SMTP server then make sure you have its address, port number, username and password ready so you can fill them in later.

Using SendGrid
==============

TODO

Using Gmail's SMTP servers
==========================

Another possiblity is to use Gmail's SMTP servers for sending email. Note that this solution is somewhat hacky and probably shouldn't be relied on as a permanant solution.

You'll need to `register for a new Gmail <http://www.gmail.com>`_. Do **not** use your primary email account for this, but do register with a real name and contact information.

That's it. To use the Gmail SMTP servers, you'll use the following configuration for PANDA::

    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'YOUR_NEW_EMAIL_ADDRESS'
    EMAIL_HOST_PASSWORD = 'YOUR_NEW_PASSWORD'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'YOUR_NEW_EMAIL_ADDRESS'

