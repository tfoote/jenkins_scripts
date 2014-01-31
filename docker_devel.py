#!/usr/bin/env python
from test_repositories import *


def main():
    parser = optparse.OptionParser()
    parser.add_option("--workspace", action="store", default=None)
    parser.add_option("--build_in_workspace", action="store_true", default=False)
    parser.add_option("--sudo", action="store_true", default=False)
    (options, args) = parser.parse_args()

    if len(args) != 2:
        print "Usage: %s ros_distro repository_name" % sys.argv[0]
        raise BuildException("Wrong number of parameters for devel script")

    ros_distro = args[0]
    repositories = args[1:]
    versions = ['devel' for _ in repositories]

    lsb_info = {}
    with open('/etc/lsb-release') as f:
        for line in f:
            key, value = line.split('=')
            lsb_info[key] = value

    platform = lsb_info['DISTRIB_CODENAME']

    print "Running prerelease test on distro %s and repositories %s" % (ros_distro, ', '.join(repositories))
    test_repositories(ros_distro, repositories, versions, options.workspace, test_depends_on=False,
        platform=platform, build_in_workspace=options.build_in_workspace, sudo=options.sudo)


if __name__ == '__main__':
    # global try
    try:
        main()
        print "devel script finished cleanly"

    # global catch
    except BuildException as ex:
        print ex.msg

    except Exception as ex:
        print "devel script failed. Check out the console output above for details."
        raise
