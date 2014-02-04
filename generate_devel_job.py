from __future__ import print_function
import sys
import shutil
import os
import tempfile
from subprocess import call
import datetime
import em

from common import get_dependencies, get_package_dependencies, MAINTAINER_NAME, MAINTAINER_EMAIL
import optparse


TEMPLATE_FILE = 'template_devel_job.em'


def main():
    parser = optparse.OptionParser()
    parser.add_option("--rebuild", action="store_true", default=False)
    parser.add_option("--buildonly", action="store_true", default=False)
    (options, args) = parser.parse_args()

    operating_system = args[0]
    platform = args[1]
    arch = args[2]
    ros_distro = args[3]
    workspace = args[4]
    repo_path = args[5]

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

    repo_sourcespace = os.path.abspath(repo_path)

    repo_build_dependencies = get_dependencies(repo_sourcespace, build_depends=True, test_depends=False)
    repo_test_dependencies = get_dependencies(repo_sourcespace, build_depends=True, test_depends=True)
    # ensure that catkin gets installed, for non-catkin packages so that catkin_make_isolated is available
    if 'catkin' not in repo_build_dependencies:
        repo_build_dependencies.append('catkin')

    dependencies = get_package_dependencies(repo_build_dependencies, ros_distro, operating_system, platform)
    test_dependencies = get_package_dependencies(repo_test_dependencies, ros_distro, operating_system, platform)

    test_dependencies = list(set(test_dependencies) - set(dependencies))

    d = {
        'operating_system': operating_system,
        'platform': platform,
        'arch': arch,
        'buildonly': options.buildonly,
        'maintainer_name': MAINTAINER_NAME,
        'maintainer_email': MAINTAINER_EMAIL,
        'ros_distro': ros_distro,
        'workspace': workspace,
        'tmp_dir': tmp_dir,
        'base_dir': base_dir,
        'timestamp': timestamp,
        'repo_sourcespace': repo_sourcespace,
        'dependencies': dependencies,
        'test_dependencies': test_dependencies,
        'repo_name': os.path.basename(repo_sourcespace),
    }

    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_dir)

    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        res = em.expand(tpl, d)
        with open(os.path.join(base_dir, 'Dockerfile'), 'w') as f2:
            f2.write(res)
        call(['cat', '%(base_dir)s/Dockerfile' % d])
        if options.rebuild:
            cmd = 'sudo docker build -no-cache -t osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s %(base_dir)s' % d
        else:
            cmd = 'sudo docker build -t osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s %(base_dir)s' % d
        print(cmd)
        call(cmd.split())
        cmd = 'sudo docker run -v %(repo_sourcespace)s:/tmp/src:ro -v %(workspace)s:%(workspace)s:rw  osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s' % d
        print(cmd)
        call(cmd.split())
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    main()
