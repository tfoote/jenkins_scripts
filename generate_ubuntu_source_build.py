#!/usr/bin/env python

from __future__ import print_function
import sys
import shutil
import os
import tempfile
from subprocess import call
import datetime
import em
import errno

from common import get_dependencies, get_package_dependencies, MAINTAINER_NAME, MAINTAINER_EMAIL, BuildException, which
import argparse

TEMPLATES = {
    'ubuntudeb': [ 'template_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'ubuntupip': [ 'from_source/templates/pip_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'fedora': [ 'from_source/templates/fedora_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    }


available_arches = ['amd64', 'i386']



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--os', default='ubuntu', dest='os')
    parser.add_argument('-p', '--platform', default='precise', dest='platform')
    parser.add_argument('-a', '--arch', default='amd64', dest='arch', choices=available_arches)
    parser.add_argument("--rebuild", action="store_true", default=False)
    parser.add_argument("--buildonly", action="store_true", default=False)
    parser.add_argument('ros_distro')
    subparsers = parser.add_subparsers(dest='subparser_name')

    source_parser = subparsers.add_parser('source')
    source_parser.add_argument('workspace')
    source_parser.add_argument('metapackage')
    source_parser.add_argument('--template', default='ubuntudeb', choices=TEMPLATES)
    source_parser.set_defaults(func=source_build)

    args = parser.parse_args()
    args.func(args)

def source_build(args):

    #print(args)
    #exit(0)

    workspace = args.workspace
    metapackage = args.metapackage
    ros_distro = args.ros_distro
    template_tag = args.template

    # Create the workspace if it doesn't already exist
    try:
        os.makedirs(workspace)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # TODO resolve this hack to work with a non user 1000
    # account. Docker appears to always output as UID 1000.
    cmd = "sudo chmod -R o+w %s" % workspace
    call(cmd.split())
    

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    print('OUTPUT DIR %s' % workspace)
    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

    #Generation substitution dictionary
    d = {
        'arch': args.arch,
        'buildonly': args.buildonly,
        'maintainer_email': MAINTAINER_EMAIL,
        'maintainer_name': MAINTAINER_NAME,
        'metapackage': metapackage,
        'operating_system': args.os,
        'platform': args.platform,
        'ros_distro': ros_distro,
        'timestamp': timestamp,
        'workspace': workspace,
    }


    res = ""
    # Load all templates into one string with expansion
    for t in TEMPLATES[template_tag]:
        print('v'*80)
        with open(t) as f:
            tpl = f.read()
            print(tpl)
            res += em.expand(tpl, d)
        print('^'*80)    

    # Copy the contents of this file's directory into the base_dir to make scripts available
    # TODO explicitly whitelist and install these scripts
    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_dir)

    #write the results to file
    with open(os.path.join(base_dir, 'Dockerfile'), 'w') as f2:
        f2.write(res)
    call(['cat', '%s/Dockerfile' % base_dir])


    # build and tag the image
    tag = template_tag+'-osrf-%(operating_system)s-%(platform)s-%(ros_distro)s-%(metapackage)s' % d
    if args.rebuild:
        cmd = 'sudo docker build -no-cache -t %s %s' % (tag, base_dir)
    else:
        cmd = 'sudo docker build -t %s %s' % (tag, base_dir)
    print(cmd)
    call(cmd.split())
    #TODO check return code before continuing

    # Rnn the tagged image 
    cmd = 'sudo docker run -v %s:%s:rw %s' % (workspace, workspace, tag)
    print(cmd)
    call(cmd.split())
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    # global try
    try:
        main()
        print("devel script finished cleanly.")

    # global catch
    except BuildException as ex:
        print(ex.msg)

    except Exception as ex:
        print("devel script failed. Check out the console output above for details.")
        raise
