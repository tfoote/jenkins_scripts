#!/usr/bin/env python

from __future__ import print_function
import sys
import shutil
import os
import tempfile
from subprocess import call, check_call
import datetime
import em
import errno

from common import get_dependencies, get_package_dependencies, MAINTAINER_NAME, MAINTAINER_EMAIL, BuildException, which
import argparse

SOURCE_TEMPLATES = {
    'ubuntudeb': [ 'template_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'ubuntupip': [ 'from_source/templates/pip_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'fedora': [ 'from_source/templates/fedora_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    }

DEVEL_TEMPLATES = {
    'ubuntudeb': [ 'template_bootstrap.em', 'template_devel_job.em'],
    }

available_arches = ['amd64', 'i386']


DEFAULT_PLATFORMS = {
    'groovy': 'precise',
    'hydro': 'precise',
    'indigo': 'saucy',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--os', default='ubuntu', dest='os',
                        help='The operating system to use in the Docker container (e.g. ubuntu)')
    parser.add_argument('-p', '--platform', default=None, dest='platform',
                        help='The release of the container operating system (e.g. precise)')
    parser.add_argument('-a', '--arch', default='amd64', dest='arch', choices=available_arches,
                        help='The architecture for the docher container')
    parser.add_argument("--rebuild", action="store_true", default=False,
                        help="Discard the Docker cache and rebuild the image")
    parser.add_argument('--http_proxy', dest='http_proxy', default=None,
                        help='A http_proxy to pass into docker')
    parser.add_argument('ros_distro')
    parser.add_argument('-w', '--workspace', dest='workspace', default=None,
                        help='The path on the host filesystem to store the artifacts')
    subparsers = parser.add_subparsers(dest='subparser_name')

    source_parser = subparsers.add_parser('source')
    source_parser.add_argument('metapackage')
    source_parser.add_argument('--template', default='ubuntudeb', choices=SOURCE_TEMPLATES)
    source_parser.add_argument("--buildonly", action="store_true", default=False,
                               help="Do not run unit tests just run the build.")
    source_parser.set_defaults(func=source_build_generate_dockerfile_template)
    
    devel_parser = subparsers.add_parser('devel')
    devel_parser.add_argument('repo_path')
    devel_parser.add_argument('--template', default='ubuntudeb', choices=DEVEL_TEMPLATES)
    devel_parser.add_argument("--buildonly", action="store_true", default=False,
                              help="Do not run unit tests just run the build.")
    devel_parser.set_defaults(func=devel_build_generate_dockerfile_template)

    args = parser.parse_args()

    if not args.platform:
        if args.os != 'ubuntu':
            parser.parse_error("platform is required if not using ubuntu.")
        if args.ros_distro in DEFAULT_PLATFORMS:
            args.platform = DEFAULT_PLATFORMS[args.ros_distro]
        else:
            parser.parse_error("platform is required if not on a default platform. %s" %
                               DEFAULT_PLATFORMS)

    print("Running job \"%s\" with parameters:\n  OS: %s\n  Distro: %s\n  Arch: %s\n\n" % (
            args.subparser_name,
            args.os,
            args.platform,
            args.arch,
            ))

    generated_workspace = False
    if not args.workspace:
        generated_workspace = True
        args.workspace = tempfile.mkdtemp()
        print("Automatically generated workspace %s To debug specify a --workspace to persist the build." % args.workspace)

    try:
        #Generate the docker file based on the arguments
        (docker_file_string, tag, mount_string) = args.func(args)
        #TODO add generic catch here for users to throw on invlaid args

        # Setup the temporary directories and execute. 
        run_docker(args, docker_file_string, tag, mount_string)
        
        #TODO return permissions to current user

    finally:
        if generated_workspace:
            print("Cleaning up automatically generated workspace %s. To debug specify a --workspace to persist the build." % args.workspace)
            #shutil.rmtree(args.workspace)
            # root permissions output, need to sudo rm
            call(['sudo', 'rm', '-rf', args.workspace])

def source_build_generate_dockerfile_template(args):
    workspace = args.workspace
    metapackage = args.metapackage
    ros_distro = args.ros_distro
    template_tag = args.template


    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

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

    res = substitute_templates(SOURCE_TEMPLATES[template_tag], d)
    
    # build and tag the image
    tag = '-'.join(['osrf', template_tag, args.os, args.platform, args.ros_distro, args.metapackage])

    mount_string = '-v %(workspace)s:%(workspace)s:rw' % d

    return res, tag, mount_string

def substitute_templates(templates, sub_dict):
    res = ""
    # Load all templates into one string with expansion
    for t in templates:
        with open(t) as f:
            tpl = f.read()
            res += em.expand(tpl, sub_dict)
    return res


def devel_build_generate_dockerfile_template(args):

    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    repo_sourcespace = os.path.abspath(args.repo_path)

    repo_name = os.path.basename(repo_sourcespace)

    repo_build_dependencies = get_dependencies(repo_sourcespace, build_depends=True, test_depends=False)
    repo_test_dependencies = get_dependencies(repo_sourcespace, build_depends=True, test_depends=True)
    # ensure that catkin gets installed, for non-catkin packages so that catkin_make_isolated is available
    if 'catkin' not in repo_build_dependencies:
        repo_build_dependencies.append('catkin')

    dependencies = get_package_dependencies(repo_build_dependencies, args.ros_distro, args.os, args.platform)
    test_dependencies = get_package_dependencies(repo_test_dependencies, args.ros_distro, args.os, args.platform)

    test_dependencies = list(set(test_dependencies) - set(dependencies))

    d = {
        'operating_system': args.os,
        'platform': args.platform,
        'buildonly': args.buildonly,
        'http_proxy': args.http_proxy,
        'maintainer_name': MAINTAINER_NAME,
        'maintainer_email': MAINTAINER_EMAIL,
        'ros_distro': args.ros_distro,
        'workspace': args.workspace,
        'timestamp': timestamp,
        'repo_sourcespace': repo_sourcespace,
        'dependencies': dependencies,
        'test_dependencies': test_dependencies,
        'repo_name': repo_name,
    }

    res = substitute_templates(DEVEL_TEMPLATES[args.template], d)


    tag = '-'.join(['osrf', 'devel', args.os, args.platform, args.ros_distro, repo_name, args.template])

    mount_string = '-v %(repo_sourcespace)s:/tmp/src:ro -v %(workspace)s:%(workspace)s:rw' % d

    return res, tag, mount_string



def run_docker(args, docker_file_string, tag, mount_string):
    #TODO add timing output
    workspace = args.workspace

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

    print('OUTPUT DIR %s' % workspace)
    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

    # Copy the contents of this file's directory into the base_dir to make scripts available
    # TODO explicitly whitelist and install these scripts
    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_dir)

    #write the results to file
    with open(os.path.join(base_dir, 'Dockerfile'), 'w') as f2:
        f2.write(docker_file_string)
    call(['cat', '%s/Dockerfile' % base_dir])

    if args.rebuild:
        cmd = 'sudo docker build -no-cache -t %s %s' % (tag, base_dir)
    else:
        cmd = 'sudo docker build -t %s %s' % (tag, base_dir)
    print(cmd)
    check_call(cmd.split())
    #TODO check return code before continuing

    # Rnn the tagged image 
    cmd = 'sudo docker run %s %s' % (mount_string, tag)
    print(cmd)
    try:
        result = call(cmd.split()) == 0
    finally:
        shutil.rmtree(tmp_dir)
    return result


if __name__ == '__main__':
    # global try
    try:
        main()
        print("docker finished cleanly.")

    # global catch
    except BuildException as ex:
        print(ex.msg)

    except Exception as ex:
        print("docker script failed. Check out the console output above for details.")
        raise
