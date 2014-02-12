from __future__ import print_function
import shutil
import os
import subprocess
import optparse
import errno
import pwd
import grp


def main():
    parser = optparse.OptionParser()
    parser.add_option("--workspace", action="store", default=None)
    (options, args) = parser.parse_args()

    if len(args) != 3:
        print("Usage: %s angstrom_path meta_ros_path machine_type" % sys.argv[0])
        raise BuildException("Wrong number of parameters for meta_ros script")

    angstrom_path = args[0]
    meta_ros_path = args[1]
    machine_type = args[2]

    base_path = os.path.join(options.workspace, 'setup-scripts')
    sources_path = os.path.join(base_path, 'sources')
    base_meta_ros_path = os.path.join(base_path, 'sources', 'meta-ros')
    deploy_path = os.path.join(base_path, 'deploy')
    output_path = os.path.join(options.workspace, 'output')
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
                if not line.startswith('meta-ros'):
                    f2.write(line)
    os.rename(os.path.join(sources_path, 'layers.txt.new'), os.path.join(sources_path, 'layers.txt'))

    os.chdir(base_path)

    uid = pwd.getpwnam('rosbuild').pw_uid
    gid = grp.getgrnam('rosbuild').gr_gid

    os.chown(base_path, uid, gid)
    for root, dirs, files in os.walk(base_path):
        for dir_entry in dirs:
            os.chown(os.path.join(root, dir_entry), uid, gid)
        for file_entry in files:
            os.chown(os.path.join(root, file_entry), uid, gid)

    def restore_sigpipe():
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    # NOTE: oebb.sh won't run properly if the SIGPIPE handler is not
    # reset to the system default.
    # Python overrides the SIGPIPE handler with its own.
    cmd = ['su', 'rosbuild', '-c', './oebb.sh config %s' % machine_type]
    p = subprocess.Popen(cmd, preexec_fn=restore_sigpipe)
    print(p.communicate())

    cmd = ['su', 'rosbuild', '-c', './oebb.sh bitbake core-image-minimal']
    p = subprocess.Popen(cmd, preexec_fn=restore_sigpipe)
    print(p.communicate())

    shutil.copytree(deploy_path, os.path.join(output_path, 'deploy'))

if __name__ == '__main__':
    main()
