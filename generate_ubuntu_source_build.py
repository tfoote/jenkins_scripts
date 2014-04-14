#!/usr/bin/env python

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
import optparse

TEMPLATES = {
    'ubuntudeb': [ 'template_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'ubuntupip': [ 'from_source/templates/pip_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    'fedora': [ 'from_source/templates/fedora_bootstrap.em', 'from_source/templates/ubuntu_deb.em'],
    }

def main():
    parser = optparse.OptionParser()
    parser.add_option('-o', '--os', default='ubuntu', dest='os')
    parser.add_option('-p', '--platform', default='precise', dest='platform')
    parser.add_option('-a', '--arch', default='amd64', dest='arch')
    parser.add_option("--rebuild", action="store_true", default=False)
    parser.add_option("--buildonly", action="store_true", default=False)
    (options, args) = parser.parse_args()

    #operating_system = args[0]
    #platform = args[1]
    #arch = args[2]
    ros_distro = args[0]
    workspace = args[1]
    metapackage = args[2]

    if len(args) == 4:
        template_tag = args[3]
    else:
        template_tag = 'ubuntudeb'

    if template_tag not in TEMPLATES:
        parser.error("invalid template_tag %s" % template_tag)

    try:
        os.makedirs(workspace)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # TODO resolve this hack to work with a non user 1000
    # account. Docker appears to always output as UID 1000.
    cmd = "sudo chmod -R o+w %s" % workspace
    call(cmd.split())
    

    tmp_dir = tempfile.mkdtemp()
    base_dir = os.path.join(tmp_dir, 'jenkins_scripts')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d')

    print('OUTPUT DIR %s' % workspace)
    print('TEMPORARY DIR %s' % tmp_dir)
    print('BASE DIR %s' % base_dir)


    d = {
        'arch': options.arch,
        'base_dir': base_dir,
        'buildonly': options.buildonly,
        'maintainer_email': MAINTAINER_EMAIL,
        'maintainer_name': MAINTAINER_NAME,
        'metapackage': metapackage,
        'operating_system': options.os,
        'platform': options.platform,
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
