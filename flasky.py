""" Main script. """
# This is where the application instance is defined.

import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import User, Role, Follow, Permission, Post, Comment
from flask_migrate import Migrate, upgrade
import sys
import click
from flask_script import Manager

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)

# Creating an application context
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Follow=Follow,
                Permission=Permission, Post=Post, Comment=Comment)

# Coverage metrics
@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
                help='Run test under code coverage.')
def test(coverage):
    """ Run the unit tests. """
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

# Running the application under the request profiler
@app.cli.command()
@click.option('--length', default=25,
            help='Number of functions to be included in the profiler report.')
@click.option('--profile-dir', default=None,
              help='Directory where profile data fils are saved')
def profile(length, profile_dir):
    """ Start the app under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                        profile_dir=profile_dir)
    app.run()

# Deploy command
@manager.command()
def deploy():
    """ Run deployment task."""
    # Migrate database to latest vertion.
    upgrade()

    # Create or update user roles
    Role.insert_roles()

    # Ensure all users are following themselves
    User.add_self_follows()