#!/usr/bin/env python

from fabric.api import *

"""
Base configuration
"""
#name of the deployed site if different from the name of the project
env.site_name = 'panda'

env.user = 'ubuntu'
env.project_name = 'panda'
env.database_password = 'panda'
env.path = '/home/%(user)s/src/%(project_name)s' % env
env.log_path = '/home/%(user)s/logs/%(project_name)s' % env
env.env_path = '/home/%(user)s/.virtualenvs/%(project_name)s' % env
env.solr_path = '/opt/solr/panda/solr'
env.repo_path = '%(path)s' % env
env.python = 'python2.7'
env.repository_url = 'git://github.com/pandaproject/panda.git'
env.hosts = ['panda.beta.tribapps.com']
    
"""
Branches
"""
def stable():
    """
    Work on stable branch.
    """
    env.branch = 'stable'

def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name
    
"""
Commands - setup
"""
def setup():
    """
    Setup a fresh virtualenv, install everything we need, and fire up the database.
    
    Does NOT perform the functions of deploy().
    """
    require('branch', provided_by=[stable, master, branch])
    
    setup_directories()
    setup_virtualenv()
    clone_repo()
    checkout_latest()
    install_requirements()
    destroy_database()
    create_database()
    syncdb()

def setup_directories():
    """
    Create directories necessary for deployment.
    """
    run('mkdir -p %(path)s' % env)
    
def setup_virtualenv():
    """
    Setup a fresh virtualenv.
    """
    run('virtualenv -p %(python)s --no-site-packages %(env_path)s;' % env)
    run('source %(env_path)s/bin/activate;' % env)

def clone_repo():
    """
    Do initial clone of the git repository.
    """
    run('git clone %(repository_url)s %(repo_path)s' % env)

def checkout_latest():
    """
    Pull the latest code on the specified branch.
    """
    run('cd %(repo_path)s; git checkout %(branch)s; git pull origin %(branch)s' % env)

def install_requirements():
    """
    Install the required packages using pip.
    """
    run('source %(env_path)s/bin/activate; pip install -q -r %(repo_path)s/requirements.txt' % env)

"""
Commands - deployment
"""
def deploy():
    """
    Deploy the latest version of the site to the server and restart Apache2.
    """
    require('branch', provided_by=[stable, master, branch])
    
    checkout_latest()
    collect_static_files()
    reload_app()

def collect_static_files():
    """
    Collect static files on the server.
    """
    sudo('cd %(repo_path)s; %(env_path)s/bin/python manage.py collectstatic --noinput' % env, user="panda")
       
def reload_app(): 
    """
    Restart the uwsgi server.
    """
    sudo('service uwsgi restart')
    sudo('service celeryd restart')

def update_requirements():
    """
    Update the installed dependencies the server.
    """
    run('source %(env_path)s/bin/activate; pip install -q -U -r %(repo_path)s/requirements.txt' % env)
    
"""
Commands - data
"""
def reset_database():
    """
    Drop and recreate the project database.
    """
    with settings(warn_only=True):
        sudo('service celeryd stop')

    sudo('service postgresql restart') # disconnect any active users

    destroy_database()
    create_database()
    syncdb()

    sudo('service celeryd start') 

def create_database():
    """
    Creates the user and database for this project.
    """
    sudo('echo "CREATE USER %(project_name)s WITH PASSWORD \'%(database_password)s\';" | psql postgres' % env, user='postgres')
    sudo('createdb -O %(project_name)s %(project_name)s' % env, user='postgres')
    
def destroy_database():
    """
    Destroys the user and database for this project.
    
    Will not cause the fab to fail if they do not exist.
    """
    with settings(warn_only=True):
        sudo('dropdb %(project_name)s' % env, user='postgres')
        sudo('dropuser %(project_name)s' % env, user='postgres')
        
def syncdb():
    """
    Sync the Django models to the database.
    """
    sudo('cd %(repo_path)s; %(env_path)s/bin/python manage.py syncdb --noinput' % env, user="panda")

def reset_solr():
    """
    Update configuration, blow away current data, and restart Solr.
    """
    with settings(warn_only=True):
        sudo('service solr stop')

    sudo('cp %(repo_path)s/setup_panda/solr.xml %(solr_path)s/solr.xml' % env)
    sudo('cp %(repo_path)s/setup_panda/schema.xml %(solr_path)s/pandadata/conf/schema.xml' % env)
    sudo('cp %(repo_path)s/setup_panda/solrconfig.xml %(solr_path)s/pandadata/conf/solrconfig.xml' % env)
    sudo('cp %(repo_path)s/setup_panda/panda.jar %(solr_path)s/pandadata/lib/panda.jar' % env)
    sudo('rm -rf %(solr_path)s/pandadata/data' % env)
    sudo('chown -R solr:solr %(solr_path)s' % env)
    sudo('service solr start')

"""
Commands - Local development
"""
def local_reset():
    """
    Reset the local database and Solr instance.
    """
    local('dropdb panda && createdb panda && python manage.py syncdb --noinput')
    local('rm -rf /var/solr/pandadata/data')
    local('cp setup_panda/solr.xml /var/solr/solr.xml')
    local('cp setup_panda/panda.jar /var/solr/pandadata/lib/panda.jar')
    local('cp setup_panda/solrconfig.xml /var/solr/pandadata/conf/solrconfig.xml')
    local('cp setup_panda/schema.xml /var/solr/pandadata/conf/schema.xml')

def local_solr():
    """
    Start the local Solr instance.
    """
    local('cd /usr/local/Cellar/solr/3.4.0/libexec/example/ && java -Xms256M -Xmx512G -Dsolr.solr.home=/var/solr/ -jar start.jar')

