from __future__ import print_function
import sys
import shutil
import os
import tempfile
from subprocess import call
import datetime
from string import Template
import rosdep
from common import get_dependencies

TEMPLATE_FILE = 'template_devel_job.dock'

def main(operating_system, platform, arch, maintainer_name, maintainer_email,
    ros_distro, workspace, repo_path):
    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

    rosdep_resolver = rosdep.RosDepResolver(ros_distro, False, False)

    repo_sourcespace = os.path.abspath(repo_path)

    repo_build_dependencies = get_dependencies(repo_sourcespace, build_depends=True, test_depends=False)
    # ensure that catkin gets installed, for non-catkin packages so that catkin_make_isolated is available
    if 'catkin' not in repo_build_dependencies:
        repo_build_dependencies.append('catkin')

    pkg_deps = rosdep_resolver.to_aptlist(repo_build_dependencies)
    dependencies = '\n'.join(['RUN apt-get install -q -y ' + pkg for pkg in pkg_deps])

    d = {
        'operating_system': operating_system,
        'platform': platform,
        'arch': arch,
        'maintainer_name': maintainer_name,
        'maintainer_email': maintainer_email,
        'ros_distro': ros_distro,
        'workspace': workspace,
        'tmp_dir': tmp_dir,
        'base_dir': base_dir,
        'timestamp': timestamp,
        'repo_sourcespace': repo_sourcespace,
        'dependencies': dependencies,
        'repo_name': os.path.basename(repo_sourcespace),
    }

    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_dir)

    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        s = Template(tpl)
        res = s.substitute(d)
        with open(os.path.join(base_dir, 'Dockerfile'), 'w') as f2:
            f2.write(res)
        call(['cat', '%(base_dir)s/Dockerfile' % d])
        cmd = 'sudo docker build -t osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s %(base_dir)s' % d
        print(cmd)
        call(cmd.split())
        cmd = 'sudo docker run -v %(repo_sourcespace)s:/tmp/src:ro osrf-jenkins-%(platform)s-%(ros_distro)s-devel-%(repo_name)s' % d
        print(cmd)
        call(cmd.split())
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    main(*sys.argv[1:])
