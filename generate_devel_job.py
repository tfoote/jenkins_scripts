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
TEMPLATE_FILE = 'template_devel_job.em'
TEMPLATE_BOOTSTRAP = 'template_bootstrap.em'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('operating_system', help='The operating system to use in the Docker container (e.g. ubuntu)')
    parser.add_argument('platform', help='The release of the container operating system (e.g. precise)')
    parser.add_argument('ros_distro', help='The ROS distribution to build for (e.g. hydro, indigo)')
    parser.add_argument('workspace', help='The path on the host filesystem to store the artifacts')
    parser.add_argument('repo_path', help='The path on the host filesystem to the repository to build')
    parser.add_argument('--rebuild', help="Discard the Docker cache and rebuild the image", action='store_true')
    parser.add_argument('--buildonly', action="store_true", default=False)
    args = parser.parse_args()

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    try:
        os.makedirs(args.workspace)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    # Hack to work around docker bug where the output is always made as UID 1000
    cmd = "sudo chmod -R o+w %s" % args.workspace
    call(cmd.split())


    print('OUTPUT DIR %s' % args.workspace)
    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

    repo_sourcespace = os.path.abspath(args.repo_path)

    repo_build_dependencies = get_dependencies(repo_sourcespace, build_depends=True, test_depends=False)
    repo_test_dependencies = get_dependencies(repo_sourcespace, build_depends=True, test_depends=True)
    # ensure that catkin gets installed, for non-catkin packages so that catkin_make_isolated is available
    if 'catkin' not in repo_build_dependencies:
        repo_build_dependencies.append('catkin')

    dependencies = get_package_dependencies(repo_build_dependencies, args.ros_distro, args.operating_system, args.platform)
    test_dependencies = get_package_dependencies(repo_test_dependencies, args.ros_distro, args.operating_system, args.platform)

    test_dependencies = list(set(test_dependencies) - set(dependencies))

    d = {
        'operating_system': args.operating_system,
        'platform': args.platform,
        'buildonly': args.buildonly,
        'maintainer_name': MAINTAINER_NAME,
        'maintainer_email': MAINTAINER_EMAIL,
        'ros_distro': args.ros_distro,
        'workspace': args.workspace,
        'tmp_dir': tmp_dir,
        'base_dir': base_dir,
        'timestamp': timestamp,
        'repo_sourcespace': repo_sourcespace,
        'dependencies': dependencies,
        'test_dependencies': test_dependencies,
        'repo_name': os.path.basename(repo_sourcespace),
        'docker_path': DOCKER_PATH,
    }

    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_dir)

    with open(TEMPLATE_BOOTSTRAP) as f:
        tpl = f.read()
        res = em.expand(tpl, d)
    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        res += em.expand(tpl, d)
    with open(os.path.join(base_dir, 'Dockerfile'), 'w') as f2:
        f2.write(res)
    call(['cat', '%(base_dir)s/Dockerfile' % d])
    if args.rebuild:
        cmd = 'sudo %(docker_path)s build -no-cache -t osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s %(base_dir)s' % d
    else:
        cmd = 'sudo %(docker_path)s build -t osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s %(base_dir)s' % d
    print(cmd)
    call(cmd.split())
    cmd = 'sudo %(docker_path)s run -v %(repo_sourcespace)s:/tmp/src:ro -v %(workspace)s:%(workspace)s:rw  osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s' % d
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
