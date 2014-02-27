from __future__ import print_function
import shutil
import os
import subprocess
import optparse
import errno
import pwd
import grp
import sys
import em


def main():
    parser = optparse.OptionParser()
    parser.add_option("--workspace", action="store", default=None)
    (options, args) = parser.parse_args()

    if len(args) != 4:
        print("Usage: %s oe_src_path meta_oe_src_path bitbake_src_path meta_ros_src_path" % sys.argv[0])
        raise BuildException("Wrong number of parameters for meta_ros script")

    oe_src_path = args[0]
    meta_oe_src_path = args[1]
    bitbake_src_path = args[2]
    meta_ros_src_path = args[3]

    base_path = os.path.join(options.workspace, 'oe-core')
    for item in os.listdir(oe_src_path):
        s = os.path.join(oe_src_path, item)
        d = os.path.join(base_path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)
    shutil.copytree(bitbake_src_path, os.path.join(base_path, 'bitbake'))

    layers = [os.path.join(meta_oe_src_path, 'meta-oe'), meta_ros_src_path]

    script_path = os.path.realpath(__file__)

    d = {
        'oe_layer': os.path.join(oe_src_path, 'meta'),
        'layers': layers,
    }

    with open(os.path.join(os.path.dirname(script_path), 'bblayers.conf.em')) as f:
        tpl = f.read()
        res = em.expand(tpl, d)

    conf_path = os.path.join(base_path, 'build', 'conf')
    try:
        os.makedirs(conf_path)
    except OSError as ose:
        if ose.errno != errno.EEXIST:
            raise

    with open(os.path.join(conf_path, 'bblayers.conf'), 'w') as f2:
        f2.write(res)

    script_txt = '''#!/bin/bash
source oe-init-build-env
bitbake core-image-ros-roscore'''

    with open(os.path.join(base_path, 'build_meta_ros.sh'), 'w') as f:
        f.write(script_txt)

    os.chdir(base_path)

    uid = pwd.getpwnam('rosbuild').pw_uid
    gid = grp.getgrnam('rosbuild').gr_gid

    os.chown(base_path, uid, gid)
    for root, dirs, files in os.walk(base_path):
        for dir_entry in dirs:
            os.chown(os.path.join(root, dir_entry), uid, gid)
        for file_entry in files:
            os.chown(os.path.join(root, file_entry), uid, gid)

    cmd = ['su', 'rosbuild', '-c', 'bash build_meta_ros.sh']
    p = subprocess.Popen(cmd)
    output = p.communicate()
    print(output)

if __name__ == '__main__':
    main()
