from __future__ import print_function
import sys
import shutil
import os
import tempfile

from string import Template

TEMPLATE_FILE = 'template_doc_job.dock'

def main(operating_system, platform, arch, maintainer_name, maintainer_email,
    ros_distro, workspace):
    tmp_dir = tempfile.mkdtemp()
    print("TEMPORARY DIR %r" % tmp_dir)

    d = {
        'operating_system': operating_system,
        'platform': platform,
        'arch': arch,
        'maintainer_name': maintainer_name,
        'maintainer_email': maintainer_email,
        'ros_distro': ros_distro,
        'workspace': workspace,
        'tmp_dir': tmp_dir,
    }

    cur_path = os.path.dirname(os.path.abspath(__file__))
    shutil.copytree(cur_path, os.path.join(tmp_dir, "jenkins_scripts"))

    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        s = Template(tpl)
        res = s.substitute(d)
        with open(os.path.join(tmp_dir, "jenkins_scripts", "Dockerfile"), "w") as f2:
            f2.write(res)


if __name__ == '__main__':
    main(*sys.argv[1:])
