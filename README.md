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

These Docker scripts also employ a set of Python modules, namely:

* [EMpy](http://www.alcyone.com/software/empy/) as the template engine
* [rosdep](http://wiki.ros.org/rosdep) to resolve the dependency graph of ROS packages
* [catkin_pkg](http://wiki.ros.org/catkin_pkg) to obtain information about ROS packages

On an Ubuntu system, all these Python modules can be installed via the ROS APT repository. First add the appropiate APT sources.line, depending on your version of Ubuntu:

**Ubuntu 12.04 (Precise)**
```
$ echo "deb http://packages.ros.org/ros/ubuntu precise main" | sudo tee /etc/apt/sources.list.d/ros-latest.list'
```

**Ubuntu 12.10 (Quantal)**
```
$ echo "deb http://packages.ros.org/ros/ubuntu quantal main" | sudo tee /etc/apt/sources.list.d/ros-latest.list'
```

**Ubuntu 13.04 (Raring)**
```
$ echo "deb http://packages.ros.org/ros/ubuntu raring main" | sudo tee /etc/apt/sources.list.d/ros-latest.list'
```

Setup the keys:
```
$ curl http://packages.ros.org/ros.key | sudo apt-key add -
```

Then update the APT database with:
```
$ sudo apt-get update
```

And finally install the Python modules typing the following:
```
$ sudo apt-get install python-empy python-rosdep python-catkin-pkg
```

Usage
-----

For every script there are the following components:

- a template (named ```template_TASK_job.dock```) from which ```Dockerfile```s are generated
- a generator (named ```generate_TASK_job.py```) that reads the template and produces ```Dockerfile```s
- a docker runner (named ```docker_TASK_job.py```) that executes the build script inside the Docker container defined in the autogenerated ```Dockerfile```
