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

DOCKER_PATH = which('docker.io') or which('docker')
TEMPLATE_FILE = 'template_meta_ros_oe_job.em'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operating_system', help='The operating system to use in the Docker container (e.g. ubuntu)')
    parser.add_argument('platform', help='The release of the container operating system (e.g. precise)')
    parser.add_argument('workspace', help='The path on the host filesystem to store the artifacts')
    parser.add_argument('oe_core_path', help='The path on the host filesystem to a copy of OpenEmbedded Core')
    parser.add_argument('meta_oe_path', help='The path on the host filesystem to a copy of meta-oe')
    parser.add_argument('bitbake_path', help='The path on the host filesystem to a copy of bitbake')
    parser.add_argument('meta_ros_path', help='The path on the host filesystem to a copy of the meta-ros repository')
    parser.add_argument("--rebuild", help="Discard the Docker cache and rebuild the image", action='store_true')
    args = parser.parse_args()

    workspace_path = os.path.abspath(args.workspace)

    build_path = os.path.join(workspace_path, 'build')
    try:
        os.makedirs(build_path)
    except OSError as ose:
        if ose.errno != errno.EEXIST:
            raise

    tmp_path = tempfile.mkdtemp()
    base_path = os.path.join(tmp_path, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')
    print('TEMPORARY DIR %s' % tmp_path)
    print('BASE DIR %s' % base_path)

    d = {
        'operating_system': args.operating_system,
        'platform': args.platform,
        'maintainer_name': MAINTAINER_NAME,
        'maintainer_email': MAINTAINER_EMAIL,
        'tmp_path': tmp_path,
        'base_path': base_path,
        'timestamp': timestamp,
        'oe_core_path': os.path.abspath(args.oe_core_path),
        'meta_oe_path': os.path.abspath(args.meta_oe_path),
        'bitbake_path': os.path.abspath(args.bitbake_path),
        'meta_ros_path': os.path.abspath(args.meta_ros_path),
        'workspace_path': workspace_path,
        'build_path': build_path,
        'docker_path': DOCKER_PATH,
    }

    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_path)

    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        res = em.expand(tpl, d)
    with open(os.path.join(base_path, 'Dockerfile'), 'w') as f2:
        f2.write(res)
    call(['cat', '%(base_path)s/Dockerfile' % d])
    if args.rebuild:
        cmd = 'sudo %(docker_path)s build -no-cache -t osrf-jenkins-%(platform)s-meta-ros-oe %(base_path)s' % d
    else:
        cmd = 'sudo %(docker_path)s build -t osrf-jenkins-%(platform)s-meta-ros-oe %(base_path)s' % d
    print(cmd)
    call(cmd.split())
    cmd = 'sudo %(docker_path)s run -v %(oe_core_path)s:/tmp/oe_core_src:ro -v %(meta_oe_path)s:/tmp/meta_oe_src:ro -v %(bitbake_path)s:/tmp/bitbake_src:ro -v %(meta_ros_path)s:/tmp/meta_ros_src:ro -v %(build_path)s:/home/rosbuild/workspace/oe-core/build:rw osrf-jenkins-%(platform)s-meta-ros-oe' % d
    print(cmd)
    call(cmd.split())
    shutil.rmtree(tmp_path)


if __name__ == '__main__':
    # global try
    try:
        main()
        print("meta-ros script finished cleanly.")

    # global catch
    except BuildException as ex:
        print(ex.msg)

    except Exception as ex:
        print("meta-ros script failed. Check out the console output above for details.")
        raise
