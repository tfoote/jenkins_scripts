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


TEMPLATE_FILE = 'from_source/templates/ubuntu_deb.em'
TEMPLATE_BOOTSTRAP = 'template_bootstrap.em'


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
    metapackage = args[5]

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)


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
        'metapackage': metapackage,
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

    tag = 'osrf-jenkins-%(platform)s-%(ros_distro)s-src-pythondeb-%(metapackage)s' % d
    if options.rebuild:
        cmd = 'sudo docker build -no-cache -t %s %s' % (tag, base_dir)
    else:
        cmd = 'sudo docker build -t %s %s' % (tag, base_dir)
    print(cmd)
    call(cmd.split())
    cmd = 'sudo docker run -v %s:%s:rw %s' % (workspace, workspace, tag)
    print(cmd)
    call(cmd.split())
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    main()
