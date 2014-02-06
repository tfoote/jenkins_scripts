from __future__ import print_function
import shutil
import os
from subprocess import call
import optparse
import errno


def main():
    parser = optparse.OptionParser()
    parser.add_option("--workspace", action="store", default=None)
    (options, args) = parser.parse_args()

    if len(args) != 2:
        print("Usage: %s angstrom_path meta_ros_path" % sys.argv[0])
        raise BuildException("Wrong number of parameters for meta_ros script")

    angstrom_path = args[0]
    meta_ros_path = args[1]

    base_path = os.path.join(options.workspace, 'setup-scripts')
    sources_path = os.path.join(base_path, 'sources')
    base_meta_ros_path = os.path.join(base_path, 'sources', 'meta-ros')
    shutil.copytree(angstrom_path, base_path)

    # Ensure that a copy of the meta-ros repository does not exist yet
    try:
        shutil.rmtree(base_meta_ros_path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    shutil.copytree(meta_ros_path, base_meta_ros_path)

    # Ensure that layers.txt file does not contain a meta-ros line
    with open(os.path.join(sources_path, 'layers.txt'), 'r') as f1:
        with open(os.path.join(sources_path, 'layers.txt.new'), 'w') as f2:
            for line in f1:
                if line.startswith('meta-ros'):
                    f2.write('meta-ros,%s,%s,HEAD\n' % (meta_ros_repo, meta_ros_branch))
                else:
                    f2.write(line)
    os.rename(os.path.join(sources_path, 'layers.txt.new'), os.path.join(sources_path, 'layers.txt'))

    os.chdir(base_path)
    call('./oebb.sh bitbake core-image-ros-world', shell=True)

if __name__ == '__main__':
    main()
