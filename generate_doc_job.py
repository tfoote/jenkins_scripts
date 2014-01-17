from __future__ import print_function
import sys

from string import Template

TEMPLATE_FILE = 'template_doc_job.dock'

def main(operating_system, platform, arch, maintainer_name, maintainer_email,
    ros_distro, workspace):
    d = {
        'operating_system': operating_system,
        'platform': platform,
        'arch': arch,
        'maintainer_name': maintainer_name,
        'maintainer_email': maintainer_email,
        'ros_distro': ros_distro,
        'workspace': workspace,
    }

    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        s = Template(tpl)
        res = s.substitute(d)
        print(res)

if __name__ == '__main__':
    main(*sys.argv[1:])
