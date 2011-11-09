=====================
Production deployment
=====================

Get hold of an Ubuntu 11.10 server--an EC2 small based off of ami-a7f539ce works well. SSH into your server and run::

    wget https://raw.github.com/pandaproject/panda/master/setup_panda.sh
    sudo bash setup_panda.sh

Your new PANDA server should now be serving on port 80. (Ensure port 80 is open in your security group.)
