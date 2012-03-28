===========
Performance
===========

The default PANDA configuration has been optimized for an EC2 Small server environment. However, even if that is the hosting solution you choose the default configuration may not be optimal for you

Task throttling
===============

If you are running on an instance smaller or larger than our recommended server you may wish to configure a shorter or longer time to wait between importing batches of data. This small "throttle" value allows the server to periodically catch up on user requests while importing data. You'll find this configuration option in the *Performance* section of the `admin settings page <http://localhost:8000/admin/settings/>`_.

Increasing the number will provided additional time for user requests and should improve PANDA's responsiveness, at the cost of imports taking longer. Decreasing the number will allow less time for user requests, which is appropraite if your server has multiple CPUs. In the latter case you may even be able to set this value to zero and still have a very responsive server.

.. note::

    In the vast majority of cases the default value for this option is fine, so if you are not sure how to tune it, you should probably just leave it alone.

Solr
====

You may wish to adjust how much memory you give to Solr. You will find the relevant configuration in ``/etc/init/solr.conf``::

    description "Solr server for PANDA"
    start on runlevel [2345]
    stop on runlevel [!2345]
    respawn
    exec sudo -u solr sh -c "java -Xms256m -Xmx512m -Dsolr.solr.home=/opt/solr/panda/solr -Djetty.home=/opt/solr/panda -Djetty.host=127.0.0.1 -jar /opt/solr/panda/start.jar >> /var/log/solr.log"

The startup parameters ``-Xms`` and ``-Xmx`` control the minimum and maximum memory that Solr will consume while indexing documents and performing queries.

If you're running on anything larger than an EC2 Small you will almost certainly want to increase these numbers. Even on an EC2 Small you may need to increase them if your are storing a large amount of data. As a rule of thumb you will want to leave between ``768m`` and ``1g`` of the system's total memory for other processes.

