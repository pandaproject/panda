#!/usr/bin/env python

from fabric.api import *

"""
Base configuration
"""
env.user = 'ubuntu'
env.project_name = 'panda'
env.database_password = 'panda'
env.path = '/opt/%(project_name)s' % env
env.solr_path = '/opt/solr/panda/solr'
env.repository_url = 'git://github.com/pandaproject/panda.git'
env.hosts = ['alpha.pandaproject.net']

env.local_solr = '/usr/local/Cellar/solr/3.4.0/libexec/example'
env.local_solr_home = '/var/solr'

env.local_test_email = 'panda@pandaproject.net'
env.local_test_api_key = 'edfe6c5ffd1be4d3bf22f69188ac6bc0fc04c84b'
env.local_test_xhr_path = 'forest/static/js/spec/mock_xhr_responses.js'
    
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
    sudo('mkdir -p %(path)s' % env)

def clone_repo():
    """
    Do initial clone of the git repository.
    """
    sudo('git clone %(repository_url)s %(path)s' % env)

def checkout_latest():
    """
    Pull the latest code on the specified branch.
    """
    sudo('cd %(path)s; git checkout %(branch)s; git pull origin %(branch)s' % env)

def install_requirements():
    """
    Install the required packages using pip.
    """
    sudo('pip install -r %(path)s/requirements.txt' % env)

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
    sudo('cd %(path)s; python manage.py collectstatic --noinput' % env, user="panda")
       
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
    sudo('pip install -U -r %(path)s/requirements.txt' % env)
    
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
    with cd('%(path)s' % env):
        sudo('python manage.py syncdb --noinput' % env, user='panda')
        sudo('python manage.py migrate --noinput' % env, user='panda')
        sudo('python manage.py loaddata redd/fixtures/init_panda.json' % env)

def reset_solr():
    """
    Update configuration, blow away current data, and restart Solr.
    """
    with settings(warn_only=True):
        sudo('service solr stop')

    sudo('sudo mkdir -p %(solr_path)s' % env)

    sudo('cp %(path)s/setup_panda/solr.xml %(solr_path)s/solr.xml' % env)

    # data
    sudo('mkdir -p %(solr_path)s/pandadata/conf' % env)
    sudo('mkdir -p %(solr_path)s/pandadata/lib' % env)
    sudo('rm -rf %(solr_path)s/pandadata/data' % env)

    sudo('cp %(path)s/setup_panda/data_schema.xml %(solr_path)s/pandadata/conf/schema.xml' % env)
    sudo('cp %(path)s/setup_panda/solrconfig.xml %(solr_path)s/pandadata/conf/solrconfig.xml' % env)
    sudo('cp %(path)s/setup_panda/panda.jar %(solr_path)s/pandadata/lib/panda.jar' % env)
    sudo('rm -rf %(solr_path)s/pandadata/data' % env)

    # data_test
    sudo('mkdir -p %(solr_path)s/pandadata_test/conf' % env)
    sudo('mkdir -p %(solr_path)s/pandadata_test/lib' % env)
    sudo('rm -rf %(solr_path)s/pandadata_test/data' % env)

    sudo('cp %(path)s/setup_panda/data_schema.xml %(solr_path)s/pandadata_test/conf/schema.xml' % env)
    sudo('cp %(path)s/setup_panda/solrconfig.xml %(solr_path)s/pandadata_test/conf/solrconfig.xml' % env)
    sudo('cp %(path)s/setup_panda/panda.jar %(solr_path)s/pandadata_test/lib/panda.jar' % env)
    sudo('rm -rf %(solr_path)s/pandadata_test/data' % env)

    # datasets
    sudo('mkdir -p %(solr_path)s/pandadatasets/conf' % env)
    sudo('rm -rf %(solr_path)s/pandadatasets/data' % env)

    sudo('cp %(path)s/setup_panda/solrconfig.xml %(solr_path)s/pandadatasets/conf/solrconfig.xml' % env)
    sudo('cp %(path)s/setup_panda/datasets_schema.xml %(solr_path)s/pandadatasets/conf/schema.xml' % env)

    # datasets_test
    sudo('mkdir -p %(solr_path)s/pandadatasets_test/conf' % env)
    sudo('rm -rf %(solr_path)s/pandadatasets_test/data' % env)

    sudo('cp %(path)s/setup_panda/solrconfig.xml %(solr_path)s/pandadatasets_test/conf/solrconfig.xml' % env)
    sudo('cp %(path)s/setup_panda/datasets_schema.xml %(solr_path)s/pandadatasets_test/conf/schema.xml' % env)

    sudo('chown -R solr:solr %(solr_path)s' % env)
    sudo('service solr start')

"""
Commands - Local development
"""
def local_reset():
    """
    Reset the local database and Solr instance.
    """
    local_reset_database()
    local_reset_solr()

def local_reset_database():
    """
    Reset the local database.
    """
    local('dropdb %(project_name)s' % env)
    local('createdb -O %(project_name)s %(project_name)s' % env)
    local('python manage.py syncdb --noinput' % env)
    local('python manage.py migrate --noinput' % env)
    local('python manage.py loaddata redd/fixtures/init_panda.json' % env)

def local_reset_solr():
    """
    Reset the local solr configuration.
    """
    local('cp setup_panda/solr.xml %(local_solr_home)s/solr.xml' % env)

    # data
    local('mkdir -p %(local_solr_home)s/pandadata/conf' % env)
    local('mkdir -p %(local_solr_home)s/pandadata/lib' % env)
    local('rm -rf %(local_solr_home)s/pandadata/data' % env)

    local('cp setup_panda/panda.jar %(local_solr_home)s/pandadata/lib/panda.jar' % env)
    local('cp setup_panda/solrconfig.xml %(local_solr_home)s/pandadata/conf/solrconfig.xml' % env)
    local('cp setup_panda/data_schema.xml %(local_solr_home)s/pandadata/conf/schema.xml' % env)

    # data_test
    local('mkdir -p %(local_solr_home)s/pandadata_test/conf' % env)
    local('mkdir -p %(local_solr_home)s/pandadata_test/lib' % env)
    local('rm -rf %(local_solr_home)s/pandadata_test/data' % env)

    local('cp setup_panda/panda.jar %(local_solr_home)s/pandadata_test/lib/panda.jar' % env)
    local('cp setup_panda/solrconfig.xml %(local_solr_home)s/pandadata_test/conf/solrconfig.xml' % env)
    local('cp setup_panda/data_schema.xml %(local_solr_home)s/pandadata_test/conf/schema.xml' % env)

    # datasets
    local('mkdir -p %(local_solr_home)s/pandadatasets/conf' % env)
    local('rm -rf %(local_solr_home)s/pandadatasets/data' % env)

    local('cp setup_panda/solrconfig.xml %(local_solr_home)s/pandadatasets/conf/solrconfig.xml' % env)
    local('cp setup_panda/datasets_schema.xml %(local_solr_home)s/pandadatasets/conf/schema.xml' % env)

    # datasets_test
    local('mkdir -p %(local_solr_home)s/pandadatasets_test/conf' % env)
    local('rm -rf %(local_solr_home)s/pandadatasets_test/data' % env)

    local('cp setup_panda/solrconfig.xml %(local_solr_home)s/pandadatasets_test/conf/solrconfig.xml' % env)
    local('cp setup_panda/datasets_schema.xml %(local_solr_home)s/pandadatasets_test/conf/schema.xml' % env)

def local_solr():
    """
    Start the local Solr instance.
    """
    local('cd %(local_solr)s && java -Xms256M -Xmx512G -Dsolr.solr.home=%(local_solr_home)s -jar start.jar' % env)

def make_fixtures():
    """
    Creates a consistent set of local test data and generates fixtures.

    Notes:
    * Will reset the database.
    * Local server (runserver, celeryd and solr) must be running.
    """
    local('python manage.py flush --noinput')
    local('python manage.py loaddata redd/fixtures/init_panda.json' % env)
    local('curl --data-binary "{ \\"delete\\": { \\"query\\": \\"*:*\\" } }" -H "Content-type:application/xml" "http://localhost:8983/solr/data/update?commit=true"')
    local('curl --data-binary "{ \\"delete\\": { \\"query\\": \\"*:*\\" } }" -H "Content-type:application/xml" "http://localhost:8983/solr/datasets/update?commit=true"')

    local('curl -H "PANDA_EMAIL: %(local_test_email)s" -H "PANDA_API_KEY: %(local_test_api_key)s" -H "Content-Type: application/json" --data-binary "{ \\"name\\": \\"Test\\" }" "http://localhost:8000/api/1.0/dataset/"' % env)
    local('curl -H "PANDA_EMAIL: %(local_test_email)s" -H "PANDA_API_KEY: %(local_test_api_key)s" -F file=@test_data/contributors.csv -F dataset_slug=test "http://localhost:8000/upload/"' % env)
    local('curl -H "PANDA_EMAIL: %(local_test_email)s" -H "PANDA_API_KEY: %(local_test_api_key)s" "http://localhost:8000/api/1.0/dataset/test/import/1/"' % env)

    mock_xhr_responses = ['window.MOCK_XHR_RESPONSES = {};']

    response = local('curl "http://localhost:8000/api/1.0/task/1/?format=json&email=%(local_test_email)s&api_key=%(local_test_api_key)s"' % env, capture=True)
    mock_xhr_responses.append('MOCK_XHR_RESPONSES.task = \'' + response.replace('\\', '\\\\') + '\';')

    response = local('curl "http://localhost:8000/api/1.0/task/?format=json&email=%(local_test_email)s&api_key=%(local_test_api_key)s"' % env, capture=True)
    mock_xhr_responses.append('MOCK_XHR_RESPONSES.tasks = \'' + response.replace('\\', '\\\\') + '\';')

    response = local('curl "http://localhost:8000/api/1.0/dataset/test/?format=json&email=%(local_test_email)s&api_key=%(local_test_api_key)s"' % env, capture=True)
    mock_xhr_responses.append('MOCK_XHR_RESPONSES.dataset = \'' + response.replace('\\', '\\\\') + '\';')

    response = local('curl "http://localhost:8000/api/1.0/dataset/?format=json&email=%(local_test_email)s&api_key=%(local_test_api_key)s"' % env, capture=True)
    mock_xhr_responses.append('MOCK_XHR_RESPONSES.datasets = \'' + response.replace('\\', '\\\\') + '\';')

    response = local('curl "http://localhost:8000/api/1.0/data/?q=Tribune&format=json&email=%(local_test_email)s&api_key=%(local_test_api_key)s"' % env, capture=True)
    mock_xhr_responses.append('MOCK_XHR_RESPONSES.search = \'' + response.replace('\\', '\\\\') + '\';')

    response = local('curl "http://localhost:8000/api/1.0/dataset/test/data/?q=Tribune&format=json&email=%(local_test_email)s&api_key=%(local_test_api_key)s"' % env, capture=True)
    mock_xhr_responses.append('MOCK_XHR_RESPONSES.dataset_search = \'' + response.replace('\\', '\\\\') + '\';')

    # Task
    with open('%(local_test_xhr_path)s' % env, 'w') as f:
        f.write('\n'.join(mock_xhr_responses))

