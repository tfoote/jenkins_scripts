from __future__ import print_function
import sys

from string import Template

TEMPLATE_FILE = 'template_doc_job.dock'

def main(base, maintainer_name, maintainer_email, ros_distro, job_runner):
    d = {
        'base': base,
        'maintainer_name': maintainer_name,
        'maintainer_email': maintainer_email,
        'ros_distro': ros_distro,
        'job_runner': job_runner
    }

    with open(TEMPLATE_FILE) as f:
        tpl = f.read()
        s = Template(tpl)
        res = s.substitute(d)
        print(res)

if __name__ == '__main__':
    main(*sys.argv[1:])
