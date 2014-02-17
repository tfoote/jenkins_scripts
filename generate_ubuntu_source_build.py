#!/usr/bin/env python

from __future__ import print_function
import sys
import shutil
import os
import tempfile
from subprocess import call
import datetime
import em

from common import create_workspace, get_dependencies, get_package_dependencies, MAINTAINER_NAME, MAINTAINER_EMAIL
import optparse

TEMPLATES = {
    'ubuntudeb': [ 'template_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'ubuntupip': [ 'from_source/templates/pip_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'fedora': [ 'from_source/templates/fedora_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    }

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

    if len(args) == 7:
        template_tag = args[6]
    else:
        template_tag = 'ubuntudeb'

    if template_tag not in TEMPLATES:
        parser.error("invalid template_tag %s" % template_tag)


    create_workspace(workspace)

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)


    d = {
        'arch': arch,
        'base_dir': base_dir,
        'buildonly': options.buildonly,
        'maintainer_email': MAINTAINER_EMAIL,
        'maintainer_name': MAINTAINER_NAME,
        'metapackage': metapackage,
        'operating_system': operating_system,
        'platform': platform,
        'ros_distro': ros_distro,
        'template_tag': template_tag,
        'timestamp': timestamp,
        'tmp_dir': tmp_dir,
        'workspace': workspace,
    }

    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, base_dir)

    res = ""
    # Load all templates into one string with expansion
    for t in TEMPLATES[template_tag]:
        print('v'*80)
        with open(t) as f:
            tpl = f.read()
            print(tpl)
            res += em.expand(tpl, d)
        print('^'*80)    

    with open(os.path.join(base_dir, 'Dockerfile'), 'w') as f2:
        f2.write(res)
    call(['cat', '%(base_dir)s/Dockerfile' % d])

    tag = 'osrf-%(operating_system)s-%(platform)s-%(ros_distro)s-%(template_tag)s-%(metapackage)s' % d
    if options.rebuild:
        cmd = 'sudo docker build -no-cache -t %s %s' % (tag, base_dir)
    else:
        cmd = 'sudo docker build -t %s %s' % (tag, base_dir)
    print(cmd)
    call(cmd.split())
    #TODO check return code before continuing
    cmd = 'sudo docker run -v %s:%s:rw %s' % (workspace, workspace, tag)
    print(cmd)
    call(cmd.split())
    shutil.rmtree(tmp_dir)


if __name__ == '__main__':
    main()
