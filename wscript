#! /usr/bin/env python
# encoding: utf-8

import os
import sys
import shutil
import hashlib
import subprocess

from waflib.Configure import conf
from waflib import Logs

import waflib

top = '.'

VERSION = '1.0.0'

from waflib.Build import BuildContext


class UploadContext(BuildContext):
    cmd = 'upload'
    fun = 'upload'


def options(opt):

    opt.add_option(
        '--run_tests', default=False, action='store_true',
        help='Run all unit tests')

    opt.add_option(
        '--pytest_basetemp', default='pytest_temp',
        help='Set the basetemp folder where pytest executes the tests')


def build(bld):

    # Create a virtualenv in the source folder and build universal wheel
    # Make sure the virtualenv Python module is in path
    with bld.create_virtualenv() as venv:
        venv.run(cmd='python -m pip install wheel')
        venv.run(cmd='python setup.py bdist_wheel --universal',
                 cwd=bld.path.abspath())

        # Run the unit-tests
        if bld.options.run_tests:
            _pytest(bld=bld, venv=venv)

    # Delete the egg-info directory, do not understand why this is created
    # when we build a wheel. But, it is - perhaps in the future there will
    # be some way to disable its creation.
    egg_info = os.path.join('src', 'mininet-testmonitor.egg-info')

    if os.path.isdir(egg_info):
        waflib.extras.wurf.directory.remove_directory(path=egg_info)

def _find_wheel(ctx):
    """ Find the .whl file in the dist folder. """

    wheel = ctx.path.ant_glob('dist/*-'+VERSION+'-*.whl')

    if not len(wheel) == 1:
        ctx.fatal('No wheel found (or version mismatch)')
    else:
        wheel = wheel[0]
        Logs.info('Wheel %s', wheel)
        return wheel


def upload(bld):
    """ Upload the built wheel to PyPI (the Python Package Index) """

    with bld.create_virtualenv(cwd=bld.bldnode.abspath()) as venv:
        venv.pip_install(packages=['twine'])

        wheel = _find_wheel(ctx=bld)

        venv.run('python -m twine upload {}'.format(wheel))


def _pytest(bld, venv):

    # To update the requirements.txt just delete it - a fresh one
    # will be generated from test/requirements.in
    if not os.path.isfile('test/requirements.txt'):
        venv.run('python -m pip install pip-tools')
        venv.run('pip-compile setup.py test/requirements.in '
                 '--output-file test/requirements.txt')

    venv.run('python -m pip install -r test/requirements.txt')

    # We override the pytest temp folder with the basetemp option,
    # so the test folders will be available at the specified location
    # on all platforms. The default location is the "pytest" local folder.
    basetemp = os.path.abspath(os.path.expanduser(
        bld.options.pytest_basetemp))

    # We need to manually remove the previously created basetemp folder,
    # because pytest uses os.listdir in the removal process, and that fails
    # if there are any broken symlinks in that folder.
    if os.path.exists(basetemp):
        waflib.extras.wurf.directory.remove_directory(path=basetemp)

    # Run all tests by just passing the test directory. Specific tests can
    # be enabled by specifying the full path e.g.:
    #
    #     'test/test_run.py::test_create_context'
    #
    test_filter = 'test'

    # Main test command
    venv.run(f'python -B -m pytest {test_filter} --basetemp {basetemp}')

    # Check the package
    venv.run(f'twine check {wheel}')


def package_box(ctx):

    with ctx.create_virtualenv() as venv:
        venv.run(cmd='python -m pip install /home/mvp/dev/steinwurf/pytest-vagrant/dist/pytest_vagrant-2.0.3-py2.py3-none-any.whl')
        venv.activate()

        import pytest_vagrant

        log = pytest_vagrant.setup_logging()
        shell = pytest_vagrant.Shell(log=log)
        machines_dir = pytest_vagrant.default_machines_dir()

        machine_factory = pytest_vagrant.MachineFactory(
            shell=shell, machines_dir=machines_dir, ssh_factory=pytest_vagrant.SSH,
            verbose=True)

        vagrant = pytest_vagrant.Vagrant(machine_factory=machine_factory, shell=shell)

        #machine = vagrant.from_box(box='ubuntu/eoan64', name='mininet-testmonitor', reset=True)

        # with machine.ssh() as ssh:
        #     print(ssh.run('ls -la'))

        #     try:
        #         box_file = machine.package()
        #     except Exception as e:
        #         print(e)
        #         print("ex: {}".format(e.output))

        #     machine.publish(box_tag="steinwurf/mininet-testmonitor",
        #                     box_version="1.0.0", provider="virtualbox",
        #                     box_file=box_file)
        with vagrant.cloud() as cloud:
            cloud.login()


