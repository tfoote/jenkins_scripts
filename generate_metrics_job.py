from __future__ import print_function
import sys
import shutil
import os
import tempfile
from subprocess import call
import datetime
from string import Template

TEMPLATE_FILE = 'template_metrics_job.dock'

def main(operating_system, platform, arch, maintainer_name, maintainer_email,
    ros_distro, workspace, stack, build_system):
    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')
    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

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
        'stack': stack,
        'build_system': build_system,
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
        cmd = 'sudo docker build -t osrf-jenkins-%(platform)s-%(ros_distro)s-metrics %(base_dir)s' % d
        call(cmd.split())
        call(['sudo', 'docker', 'run', 'osrf-jenkins-%(platform)s-%(ros_distro)s-metrics' % d])
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    main(*sys.argv[1:])