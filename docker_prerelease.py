#!/usr/bin/env python
from test_repositories import *


def main():
    parser = optparse.OptionParser()
    parser.add_option("--workspace", action="store", default=None)
    parser.add_option("--build_in_workspace", action="store_true", default=False)
    parser.add_option("--sudo", action="store_true", default=False)
    parser.add_option("--no-chroot", action="store_true", default=False)
    (options, args) = parser.parse_args()

    if len(args) <= 2 or len(args) % 2 != 1:
        print "Usage: %s ros_distro repo1 version1 repo2 version2 ..." % sys.argv[0]
        print " - with ros_distro the name of the ros distribution (e.g. 'fuerte' or 'groovy')"
        print " - with repo the name of the repository"
        print " - with version 'latest', 'devel', or the actual version number (e.g. 0.2.5)."
        raise BuildException("Wrong arguments for prerelease script")

    ros_distro = args[0]
    repo_list = [args[i] for i in range(1, len(args), 2)]
    version_list = [args[i + 1] for i in range(1, len(args), 2)]

    print "Running prerelease test on distro %s and repositories %s" % (ros_distro, ', '.join(["%s (%s)" % (r, v) for r, v in zip(repo_list, version_list)]))
    test_repositories(ros_distro, repo_list, version_list, options.workspace, test_depends_on=True,
                      build_in_workspace=options.build_in_workspace, sudo=options.sudo, no_chroot=options.no_chroot)


if __name__ == '__main__':
    # global try
    try:
        main()
        print "prerelease script finished cleanly"

    # global catch
    except BuildException as ex:
        print ex.msg
        sys.exit(1)

    except Exception as ex:
        print "prerelease script failed. Check out the console output above for details."
        raise
