==========================
Frequently Asked Questions
==========================

About the project
=================

What is the PANDA Project?
--------------------------

The PANDA Project is a data warehousing solution for newsrooms. It provides a place for journalists to securely archive data, search it and share it within their organization.

Who is developing it?
---------------------

The PANDA board is made up of `Brian Boyer <http://twitter.com/brianboyer>`_ and `Joe Germuska <http://twitter.com/joegermuska>`_ of the Chicago Tribune, joined by `Ryan Pitts <http://twitter.com/ryanpitts>`_ of The Spokesman-Review. The lead developer is `Christopher Groskopf <http://twitter.com/onyxfish>`_. Additional source code, bug reports and feedback have been contributed by a community of users.

Development has been funded by a `2011 Knight News Challenge Grant <http://www.knightfoundation.org/press-room/press-release/knight-foundation-media-innovation-contest-announc/>`_ and will continue for one year (ending in early September, 2012).

Grant funds were directed to `Investigative Reporters and Editors (IRE) <http://www.ire.org/>`_ who are facilitating the grant and providing additional infrastructure support.

What does "PANDA" mean?
-----------------------

**P**\ ANDA **A** **N**\ ewsroom **D**\ ata **A**\ ppliance.

It's a `recursive acronym <https://en.wikipedia.org/wiki/Recursive_acronym>`_.

PANDAs eat data.

Is my data public?
------------------

No, PANDA is intended to be an internal tool. We provide instructions describing how to secure your data so only users in your organization can see your data. This is implemented both using firewalls and user credentials.

Is PANDA a publishing platform?
-------------------------------

No, PANDA is a place to store and search data, but not a way of publishing it.

So is this like Caspio?
-----------------------

No, PANDA does produce graphics or interactives.

So is this like BuzzData?
-------------------------

Sort of, but PANDA is self-hosted, open source and designed specifically for newsrooms.

Is my data safe?
----------------

As safe as we can make it, though the safety of your data is far more dependent on `backups <backups.html>`_, server stability, etc. then on choices made while developing PANDA.

How is it licensed?
-------------------

PANDA is released under the `MIT License <http://www.opensource.org/licenses/MIT>`_, one of the most permissive of all open source licenses. It can be freely used by commerical and non-commerical entities alike.

Hosting questions
=================

Who hosts the PANDA project?
----------------------------

You do. We offer instructions for `hosting on Amazon's EC2 service <amazon.html>`_ or `hosting on your own servers <self-install.html>`_. In order not to create a sustainability problem when the grant ends, PANDA is not available as a service.

How much does hosting on Amazon EC2 cost?
-----------------------------------------

It depends on how powerful of a server you need, but for an EC2 "small", storage and bandwidth it will cost you $70-100 a month. This "small" size is our default and probably enough for many small-to-medium size organizations.

Very small organizations can also try running PANDA on an EC2 "micro", at a cost of $15-30 per month, but this is infrequently tested and not likely to perform well for more than a handful of users.

Does hosting on Amazon EC2 open up security issues?
---------------------------------------------------

It depends on how zealous you are about security. A PANDA in a properly secured EC2 environment (i.e. firewalled for your organization and with `SSL configured <ssl.html>`) is a pretty secure beast. However, as with any hosted platform, there is no technical way to gaurantee an employee of Amazon isn't snooping.

Does hosting on Amazon EC2 create privacy or legal issues?
----------------------------------------------------------

Maybe. If you will be putting highly sensistive data in your PANDA--data so sensitive you are concerned it may be subpeonaed--then you should not host on Amazon. As with any 3rd party service a legal claim to your data could be made against the provider, rather than against you, depriving you of the right to have your lawyers defend against it.

Technical questions
===================

What platforms does PANDA run on?
---------------------------------

PANDA requires `Ubuntu <http://www.ubuntu.com/>`_ 11.10. We anticipate upgrading this requirement to Ubuntu 12.04 LTS before the end of the grant.

Support for other platforms is unlikely, but not totally out of the question.

Does PANDA require a dedicated server?
--------------------------------------

Yes. We would love to make PANDA more modular, but it's complex array of depedencies make this very difficult and we would prefer to spend our grant funds developing features and ensuring its a stable product.

Obviously nothing is actually stopping you from installing other stuff on the same server. Just don't do it.

Can I run PANDA on that old Dell under my desk?
-----------------------------------------------

Very likely! If it can run Ubuntu 11.10 it can probably run PANDA. We don't have "minimum requirements", but the specs of an EC2 small are:

* 1.7 GB RAM
* 1.6 ghz single-core processor
* 8 GB disk space

Any PC manufactured in the last five years should easily exceed these specifications.

Does the PANDA have an API?
---------------------------

Yes, see our `API documentation <api.html>`_.

Can I use PANDA to power a news application?
--------------------------------------------

Only if you choose make your PANDA API public, which we strongly discourage. PANDA is not designed to support many concurrent users, nor is the data structured in a manner suitable for most user-facing applications. If you want to use PANDA to publish data, we suggest writing a script to shadow tables into a SQL database. This will be more stable and secure, both for your application and for your PANDA.

What technology does PANDA use?
-------------------------------

The linchpin technologies used by PANDA are `Python <http://python.org>`_, `Django <http://djangoproject.com>`_, and `Solr <http://lucene.apache.org/solr/>`_. For a more complete list, see our `Architecture choices wiki page <https://github.com/pandaproject/panda/wiki/Architecture-choices>`_.

