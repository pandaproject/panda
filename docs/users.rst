===============
User management
===============

Creating a new admin user
=========================

Visit the admin users page::

    http://localhost:8000/admin/auth/user/

Replace ``localhost:8000`` with your PANDA's domain name.

In the upper-right corner click "Add user". Type in the email address and name and click "Save". If you've already setup :doc:`Email <email>` then you will receive a registration email with an activation link. Ignore it. On the details page for your new user click the "change password form" link underneath the **Password** field. Enter your password and click "Change Password". Check the **Active**, **Staff status** and **Superuser status** checkboxes and click "Save".

Creating new PANDA users
========================

.. note::

    Setup :doc:`Email <email>` before you do this.

Visit the admin users page::

    http://localhost:8000/admin/auth/user/

Replace ``localhost:8000`` with your PANDA's domain name.

In the upper-right corner click "Add user". Type in the email address. You may choose to also enter the user's name or leave it blank. They will have an opportunity to add/update it. Click "Save". Your new user will receive a registration email with an activation link.

Creating new users in bulk
==========================

If you need to create a lot of users you can also use your administrative API key to create new users via the :doc:`API <api>`.

