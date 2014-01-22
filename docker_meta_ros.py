from __future__ import print_function
import os
from subprocess import call

def main():
    parser = optparse.OptionParser()
    parser.add_option("--workspace", action="store", default=None)
    (options, args) = parser.parse_args()

    if len(args) != 3:
        print("Usage: %s angstrom_version meta_ros_repo meta_ros_branch" % sys.argv[0])
        raise BuildException("Wrong number of parameters for meta_ros script")

    angstrom_version = args[0]
    meta_ros_repo = args[1]
    meta_ros_branch = args[2]

    print("Running meta_ros script for Angstrom version %s, repository %s and branch %s" % (angstrom_version,
        meta_ros_repo, meta_ros_branch))

    base_path = os.path.join(options.workspace, 'setup-scripts', 'sources')
    oebb_path = os.path.join(options.workspace, 'setup-scripts', 'oebb.sh')
    with open(os.path.join(base_path, 'layers.txt'), 'r') as f1:
        with open(os.path.join(base_path, 'layers.txt.new'), 'w') as f2:
            for line in f1:
                if line.startswith('meta-ros'):
                    f2.write('meta-ros,%s,%s,HEAD' % (meta_ros_repo, meta_ros_branch))
                else:
                    f2.write(line)
                f2.write('\n')
    os.rename(os.path.join(base_path, 'layers.txt.new'), os.path.join(base_path, 'layers.txt'))
    call([oebb_path, 'bitbake', 'core-image-ros-world'])

if __name__ == '__main__':
    # global try
    try:
        main()
        print("devel script finished cleanly")

    # global catch
    except BuildException as ex:
        print(ex.msg)

    except Exception as ex:
        print("devel script failed. Check out the console output above for details.")
        raise
