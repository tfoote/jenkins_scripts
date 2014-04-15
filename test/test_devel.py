import os
import yaml
import subprocess
import tempfile
import shutil

def test_devel_build():
    tempdir = tempfile.mkdtemp()
    try:
        checkout_cmd = 'git clone https://github.com/ros/pluginlib %s/pluginlib' % tempdir
        assert subprocess.call(checkout_cmd.split()) == 0
        
        cmd = 'python generate_ubuntu_source_build.py --platform saucy indigo devel %s/pluginlib' % tempdir
        assert subprocess.call(cmd.split()) == 0
        
    finally:
        shutil.rmtree(tempdir)
