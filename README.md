ROS Jenkins scripts
===================

Scripts used on the build farm to build and test the ROS source code.

Installation
------------

The following scripts use [Docker](http://docker.io) to setup the build environments and to keep them isolated from the host system.

Docker uses LXC containers, however kernels <= 3.7 contain bugs in the LXC stack that prevent Docker from running smoothly. If you're using Ubuntu Precise (which ships with a 3.2 kernel), you'll need to upgrade to at least a backported kernel from Raring (13.04) or higher. You can install a backported kernel with the following:

```
$ sudo apt-get update
$ sudo apt-get install linux-image-generic-lts-raring linux-headers-generic-lts-raring

$ sudo reboot
```

you can install more up to date kernels replacing ```raring``` with ```saucy``` or ```trusty```

The Docker team maintains an Ubuntu repository, thus it can be installed as a regular Debian package with:

```
echo "deb http://get.docker.io/ubuntu docker main" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install lxc-docker
```

More information about how to install Docker can be found at http://docs.docker.io/en/latest/installation/ubuntulinux/
