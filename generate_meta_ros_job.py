from __future__ import print_function
import sys
import shutil
import os
import tempfile
from subprocess import call
import datetime
import em

from common import get_dependencies, get_package_dependencies, MAINTAINER_NAME, MAINTAINER_EMAIL, BuildException
import optparse

TEMPLATE_FILE = 'template_meta_ros_job.em'


def main():
    parser = optparse.OptionParser()
    parser.add_option("--rebuild", action="store_true", default=False)
    parser.add_option("--buildonly", action="store_true", default=False)
    (options, args) = parser.parse_args()

    if len(args) != 7:
        print("Usage: %s operating_system platform arch workspace angstrom_path meta_ros_path machine_type" % sys.argv[0])
        raise BuildException("Wrong arguments for meta-ros script")

    operating_system = args[0]
    platform = args[1]
    arch = args[2]
    workspace = args[3]
    angstrom_path = args[4]
    meta_ros_path = args[5]
    machine_type = args[6]

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')
    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)

    d = {
        'operating_system': operating_system,
        'platform': platform,
        'arch': arch,
        'maintainer_name': MAINTAINER_NAME,
        'maintainer_email': MAINTAINER_EMAIL,
        'tmp_dir': tmp_dir,
        'base_dir': base_dir,
        'timestamp': timestamp,
        'machine_type': machine_type,
        'angstrom_path': angstrom_path,
        'meta_ros_path': meta_ros_path,
        'workspace': workspace,
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
        cmd = 'sudo docker build -no-cache -t osrf-jenkins-%(platform)s-meta-ros %(base_dir)s' % d
    else:
        cmd = 'sudo docker build -t osrf-jenkins-%(platform)s-meta-ros %(base_dir)s' % d
    print(cmd)
    call(cmd.split())
    cmd = 'sudo docker run -v %(angstrom_path)s:/tmp/angstrom_src:ro -v %(meta_ros_path)s:/tmp/meta_ros_src:ro osrf-jenkins-%(platform)s-meta-ros' % d
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
