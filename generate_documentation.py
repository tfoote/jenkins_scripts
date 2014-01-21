#!/usr/bin/env python
import argparse
import os
import sys
import urllib2
import datetime
import shutil
from common import get_ros_env, call, check_output, BuildException
from doc_stack import document_necessary, document_repo

#TODO: Eventually, pull rosdoc lite from debs
def checkout_rosdoc_lite(workspace, ros_distro, no_chroot=False):
    checkout_path = "%s/rosdoc_lite" % workspace
    if os.path.exists(checkout_path):
        shutil.rmtree(checkout_path)

    call("git clone git://github.com/ros-infrastructure/rosdoc_lite.git %s" % checkout_path)
    old_dir = os.getcwd()
    os.chdir(checkout_path)
    rev = check_output("git rev-parse HEAD").split('\n')[0]
    os.chdir(old_dir)
    return rev

def main():
    parser = argparse.ArgumentParser(description='Doc')
    parser.add_argument('rosdistro', help='The ROS distro')
    parser.add_argument('repo', help='The repository or stack name')
    parser.add_argument('--platform', required=True, help="The OS platform, e.g. 'precise'")
    parser.add_argument('--arch', required=True, help="The architecture, e.g. 'amd64'")
    parser.add_argument('--workspace', required=True, help='Path where the documentation will be generated')
    parser.add_argument('--skip-garbage', action='store_true', help='Skip deleting all generated doc files')
    parser.add_argument('--force', action='store_true', help='Force generating documentation even when the upstream has not changed')
    args = parser.parse_args()

    print
    print
    print
    print "============================================================"
    print "==== Begin doc script.  Ignore the output above ====="
    print "============================================================"
    print
    print
    print

    print "Working on distro %s and repo/stack %s" % (args.rosdistro, args.repo)

    docspace = os.path.join(args.workspace, 'doc_stacks', str(datetime.datetime.now()).replace(' ', '_').replace(':', '-'))
    os.makedirs(docspace)

    try:
        jenkins_scripts_version = 'LATEST'

        rosdoc_lite_version = checkout_rosdoc_lite(args.workspace, args.rosdistro)

        print "WORKSPACE: ", args.workspace

        necessary = document_necessary(args.workspace, docspace, args.rosdistro, args.repo,
            rosdoc_lite_version, jenkins_scripts_version, args.force)

        if not necessary:
            return

        homepage = 'http://docs.ros.org'
        document_repo(args.workspace, docspace, args.rosdistro, args.repo,
                  args.platform, args.arch, homepage, False, True, **necessary)
    finally:
        if not args.skip_garbage:
            shutil.rmtree(docspace)


if __name__ == '__main__':
    main()
