# Chicago Tribune News Applications fabfile
# No copying allowed

from fabric.api import *

"""
Base configuration
"""
#name of the deployed site if different from the name of the project
env.site_name = 'panda'

env.user = 'ubuntu'
env.project_name = 'panda'
env.database_password = 'NE3HY2dc16'
env.site_media_prefix = "site_media"
env.admin_media_prefix = "admin_media"
env.path = '/home/%(user)s/src/%(project_name)s' % env
env.log_path = '/home/%(user)s/logs/%(project_name)s' % env
env.env_path = '/home/%(user)s/.virtualenvs/%(project_name)s' % env
env.repo_path = '%(path)s' % env
#env.apache_config_path = '/home/%(user)s/src/apache/%(project_name)s' % env
env.python = 'python2.7'
env.repository_url = "git@github.com:pandaproject/panda.git"

"""
Environments
"""
def production():
    """
    Work on production environment
    """
    env.settings = 'production'
    env.hosts = ['panda.tribapps.com']
    env.s3_bucket = 'media.panda.tribapps.com'
    env.site_domain = 'panda.tribapps.com'    

def staging():
    """
    Work on staging environment
    """
    env.settings = 'staging'
    env.hosts = ['panda.beta.tribapps.com']
    env.s3_bucket = 'media.panda.beta.tribapps.com'
    env.site_domain = 'panda.beta.tribapps.com'    
    
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
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])
    
    setup_directories()
    setup_virtualenv()
    clone_repo()
    checkout_latest()
    install_requirements()
    destroy_database()
    create_database()
    load_data()
    install_apache_conf()
    deploy_requirements_to_s3()

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
    run('source %(env_path)s/bin/activate; %(env_path)s/bin/easy_install -U setuptools; %(env_path)s/bin/easy_install -U pip;' % env)

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
    run('source %(env_path)s/bin/activate; yes w | pip install -q -r %(repo_path)s/requirements.txt' % env)

def install_apache_conf():
    """
    Install the apache site config file.
    """
    # TODO
    #sudo('cp %(repo_path)s/config/%(settings)s/apache %(apache_config_path)s' % env)
    pass

def deploy_requirements_to_s3():
    """
    Deploy the admin media to s3.
    """
    with settings(warn_only=True):
        run('s3cmd del --recursive s3://%(s3_bucket)s/%(project_name)s/%(admin_media_prefix)s/' % env)
    
    run('s3cmd -P --guess-mime-type --rexclude-from=%(repo_path)s/s3exclude sync %(env_path)s/src/django/django/contrib/admin/media/ s3://%(s3_bucket)s/%(project_name)s/%(admin_media_prefix)s/' % env)

"""
Commands - deployment
"""
def deploy():
    """
    Deploy the latest version of the site to the server and restart Apache2.
    
    Does not perform the functions of load_new_data().
    """
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])
    
    with settings(warn_only=True):
        maintenance_up()
        
    checkout_latest()
    gzip_assets()
    deploy_to_s3()
    maintenance_down()
    
def maintenance_up():
    """
    Install the Apache maintenance configuration.
    """
    sudo('cp %(repo_path)s/config/%(settings)s/apache_maintenance %(apache_config_path)s' % env)
    reboot()

def gzip_assets():
    """
    GZips every file in the media directory and places the new file
    in the gzip directory with the same filename.
    """
    run('cd %(repo_path)s; python gzip_assets.py' % env)

def deploy_to_s3():
    """
    Deploy the latest project site media to S3.
    """
    env.media_path = '%(repo_path)s/media/' % env
    run(('s3cmd -P --guess-mime-type --rexclude-from=%(repo_path)s/s3exclude sync %(media_path)s s3://%(s3_bucket)s/%(project_name)s/%(site_media_prefix)s/') % env)

    env.gzip_path = '%(repo_path)s/gzip_media/' % env
    run(('s3cmd -P --add-header=Content-encoding:gzip --guess-mime-type --rexclude-from=%(repo_path)s/s3exclude sync %(gzip_path)s s3://%(s3_bucket)s/%(project_name)s/%(site_media_prefix)s/') % env)
       
def reboot(): 
    """
    Restart the Apache2 server.
    """
    # TODO
    #sudo('service apache2 restart')
    pass
    
def maintenance_down():
    """
    Reinstall the normal site configuration.
    """
    install_apache_conf()
    reboot()
    
"""
Commands - rollback
"""
def rollback(commit_id):
    """
    Rolls back to specified git commit hash or tag.
    
    There is NO guarantee we have committed a valid dataset for an arbitrary
    commit hash.
    """
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])
    
    maintenance_up()
    checkout_latest()
    git_reset(commit_id)
    gzip_assets()
    deploy_to_s3()
    maintenance_down()
    
"""
Commands - data
"""
def load_new_data():
    """
    Erase the current database and load new data from the SQL dump file.
    """
    require('settings', provided_by=[production, staging])
    
    maintenance_up()
    pgpool_down()
    destroy_database()
    create_database()
    load_data()
    pgpool_up()
    maintenance_down()
    
def create_database(func=run):
    """
    Creates the user and database for this project.
    """
    func('echo "CREATE USER %(project_name)s WITH PASSWORD \'%(database_password)s\';" | psql postgres' % env)
    func('createdb -O %(project_name)s %(project_name)s' % env)
    
def destroy_database(func=run):
    """
    Destroys the user and database for this project.
    
    Will not cause the fab to fail if they do not exist.
    """
    with settings(warn_only=True):
        func('dropdb %(project_name)s' % env)
        func('dropuser %(project_name)s' % env)
        
def load_data():
    """
    Loads data from the repository into PostgreSQL.
    """
    run('psql -q %(project_name)s < %(repo_path)s/data/psql/dump.sql' % env)
    
def pgpool_down():
    """
    Stop pgpool so that it won't prevent the database from being rebuilt.
    """
    sudo('service pgpool stop')
    
def pgpool_up():
    """
    Start pgpool.
    """
    sudo('service pgpool start')

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
        run('dropdb %(project_name)s' % env)
        run('dropuser %(project_name)s' % env)
        pgpool_up()
        sudo('rm %(apache_config_path)s' % env)
        reboot()
        run('s3cmd del --recursive s3://%(s3_bucket)s/%(project_name)s' % env)

def local_shiva():
    destroy_database(local)

def local_bootstrap():
    create_database(local)

    # Normal bootstrap
    local('python manage.py syncdb --noinput')

    # Bootstrap with south
    # local('python manage.py syncdb --all --noinput')
    # local('python manage.py migrate --fake')

"""
Utility functions (not to be called directly)
"""
def _execute_psql(query):
    """
    Executes a PostgreSQL command using the command line interface.
    """
    env.query = query
    run(('cd %(repo_path)s; psql -q %(project_name)s -c "%(query)s"') % env)
    
def _confirm_branch():
    if (env.settings == 'production' and env.branch != 'stable'):
        answer = prompt("You are trying to deploy the '%(branch)s' branch to production.\nYou should really only deploy a stable branch.\nDo you know what you're doing?" % env, default="Not at all")
        if answer not in ('y','Y','yes','Yes','buzz off','screw you'):
            exit()
