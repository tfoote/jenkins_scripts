#!/usr/bin/env python
import optparse
import shutil
import yaml

from common import *


def run_devel_job(ros_distro, repo_list, version_list, workspace,
        platform, buildonly):
    print "Testing on distro %s" % ros_distro
    print "Testing repositories %s" % ', '.join(repo_list)
    print "Testing versions %s" % ', '.join(version_list)

    # clean up old tmp directory
    shutil.rmtree(os.path.join(workspace), ignore_errors=True)

    repo_sourcespace = os.path.join(workspace, 'src')
    repo_path = os.path.join('/tmp', 'src')
    shutil.copytree(repo_path, repo_sourcespace)
    repo_buildspace = os.path.join(workspace, 'build')
    test_results_dir = os.path.join(workspace, 'test_results')

    # get environment
    ros_env = get_ros_env('/opt/ros/%s/setup.bash' % ros_distro)

    # make build folder and change into it
    # make test results dir
    if os.path.exists(repo_buildspace):
        shutil.rmtree(repo_buildspace)
    os.makedirs(repo_buildspace)
    os.chdir(workspace)

    print "Build catkin workspace"
    call("catkin_make", ros_env)


    if buildonly:
        return

    # make test results dir
    if os.path.exists(test_results_dir):
        shutil.rmtree(test_results_dir)
    os.makedirs(test_results_dir)

    # get the repositories test and run dependencies
    print "Build and run unit tests"
    call("catkin_make run_tests -DCATKIN_TEST_RESULTS_DIR=%s" % (test_results_dir), ros_env)
    call("catkin_test_results %s" % test_results_dir, ros_env)
    print("Results available in %s " % workspace)



def main():
    parser = optparse.OptionParser()
    parser.add_option("--workspace", action="store", default=None)
    parser.add_option("--buildonly", action="store_true", default=False)
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

    print "Running devel test on distro %s and repositories %s" % (ros_distro, ', '.join(repositories))
    run_devel_job(ros_distro, repositories, versions, options.workspace,
        platform=platform, buildonly=options.buildonly)


if __name__ == '__main__':
    # global try
    try:
        main()
        print "devel script finished cleanly."

    # global catch
    except BuildException as ex:
        print ex.msg

    except Exception as ex:
        print "devel script failed. Check out the console output above for details."
        raise
