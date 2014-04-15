import subprocess

def test_source_build():
    cmd = 'python generate_ubuntu_source_build.py --platform saucy indigo source ros_comm'
    assert subprocess.call(cmd.split()) == 0
