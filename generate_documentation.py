#!/usr/bin/env python
import argparse
import os
import sys
import urllib2
import datetime
import shutil
from common import get_ros_env, call, check_output, BuildException
from doc_stack import document_necessary, document_repo

def main():
    platform = os.environ.get('OS_PLATFORM', None)
    arch = os.environ.get('ARCH', None)

    parser = argparse.ArgumentParser(description='Doc')
    parser.add_argument('rosdistro', help='The ROS distro')
    parser.add_argument('repo', help='The repository or stack name')
    parser.add_argument('--platform', required=platform is None, help="The OS platform, e.g. 'precise'")
    parser.add_argument('--arch', required=arch is None, help="The architecture, e.g. 'amd64'")
    parser.add_argument('--workspace', action='store_true', help='Path where the documentation will be generated')
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
        doit(args.rosdistro, args.repo, workspace, docspace, args.platform, args.arch, args.no_chroot, args.skip_garbage, args.force)
    finally:
        if not args.skip_garbage:
            shutil.rmtree(docspace)


def doit(ros_distro, stack, workspace, docspace, platform, arch, no_chroot=False, skip_garbage=False, force=False):
    #Run documentation generation on the stack
    homepage = 'http://docs.ros.org'
    document_repo(workspace, docspace, ros_distro, stack,
                  platform, arch,
                  homepage, no_chroot, skip_garbage, **necessary)


if __name__ == '__main__':
    main()
