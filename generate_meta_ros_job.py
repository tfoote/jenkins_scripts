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
TEMPLATE_FILE = 'template_meta_ros_job.em'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operating_system', help='The operating system to use in the Docker container (e.g. ubuntu)')
    parser.add_argument('platform', help='The release of the container operating system (e.g. precise)')
    parser.add_argument('arch', help='The architecture of the container image (e.g. i386)')
    parser.add_argument('workspace', help='The path on the host filesystem to store the artifacts')
    parser.add_argument('angstrom_path', help='The path on the host filesystem to a copy of the Angstrom distribution')
    parser.add_argument('meta_ros_path', help='The path on the host filesystem to a copy of the meta-ros repository')
    parser.add_argument('machine_type', help='The target machine type to use for building Angstrom (e.g. beagleboard)')
    parser.add_argument("--rebuild", help="Discard the Docker cache and rebuild the image", action='store_true')
    args = parser.parse_args()

    log_dir = os.path.join(args.workspace, 'log')
    try:
        os.makedirs(log_dir)
    except OSError as ose:
        if ose.errno != errno.EEXIST:
            raise

    output_dir = os.path.join(args.workspace, 'output')
    try:
        os.makedirs(output_dir)
    except OSError as ose:
        if ose.errno != errno.EEXIST:
            raise

    build_dir = os.path.join(args.workspace, 'build')
    try:
        os.makedirs(build_dir)
    except OSError as ose:
        if ose.errno != errno.EEXIST:
            raise

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')
    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

    d = {
        'operating_system': args.operating_system,
        'platform': args.platform,
        'arch': args.arch,
        'maintainer_name': MAINTAINER_NAME,
        'maintainer_email': MAINTAINER_EMAIL,
        'tmp_dir': tmp_dir,
        'base_dir': base_dir,
        'timestamp': timestamp,
        'machine_type': args.machine_type,
        'angstrom_path': args.angstrom_path,
        'meta_ros_path': args.meta_ros_path,
        'workspace': args.workspace,
        'log_dir': log_dir,
        'output_dir': output_dir,
        'build_dir': build_dir,
        'docker_path': DOCKER_PATH,
    }

    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_dir)

    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        res = em.expand(tpl, d)
    with open(os.path.join(base_dir, 'Dockerfile'), 'w') as f2:
        f2.write(res)
    call(['cat', '%(base_dir)s/Dockerfile' % d])
    if args.rebuild:
        cmd = 'sudo %(docker_path)s build -no-cache -t osrf-jenkins-%(platform)s-meta-ros %(base_dir)s' % d
    else:
        cmd = 'sudo %(docker_path)s build -t osrf-jenkins-%(platform)s-meta-ros %(base_dir)s' % d
    print(cmd)
    call(cmd.split())
    cmd = 'sudo %(docker_path)s run -v %(angstrom_path)s:/tmp/angstrom_src:ro -v %(meta_ros_path)s:/tmp/meta_ros_src:ro -v %(log_dir)s:/var/log:rw  -v %(output_dir)s:/home/rosbuild/workspace/output:rw osrf-jenkins-%(platform)s-meta-ros' % d
    print(cmd)
    call(cmd.split())
    shutil.rmtree(tmp_dir)


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
