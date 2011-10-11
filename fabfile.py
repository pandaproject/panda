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

def update_requirements():
    """
    Update the installed dependencies the server.
    """
    run('source %(env_path)s/bin/activate; pip install -q -U -r %(repo_path)s/requirements.txt' % env)
    
"""
Commands - data
"""
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
        sudo('service postgresql restart')  # disconnect any active users
        sudo('dropdb %(project_name)s' % env, user='postgres')
        sudo('dropuser %(project_name)s' % env, user='postgres')
        
def syncdb():
    """
    Sync the Django models to the database.
    """
    sudo('cd %(repo_path)s; %(env_path)s/bin/python manage.py syncdb --noinput' % env, user="panda")

"""
Deaths, destroyers of worlds
"""
def shiva_the_destroyer():
    """
    Remove all directories, databases, etc. associated with the application.
    """
    with settings(warn_only=True):
        run('rm -Rf %(path)s' % env)
        run('rm -Rf %(log_path)s' % env)
        run('rm -Rf %(env_path)s' % env)
        pgpool_down()
        sudo('dropdb %(project_name)s' % env, user='postgres')
        sudo('dropuser %(project_name)s' % env, user='postgres')
        pgpool_up()
        reload_app()

