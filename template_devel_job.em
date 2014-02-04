FROM @operating_system:@platform
MAINTAINER @maintainer_name @maintainer_email

ENV DEBIAN_FRONTEND noninteractive
RUN echo deb http://archive.ubuntu.com/ubuntu @platform main universe multiverse | tee /etc/apt/sources.list
RUN echo deb http://pkg.jenkins-ci.org/debian binary/ | tee /etc/apt/sources.list.d/jenkins.list
RUN echo deb http://packages.ros.org/ros-shadow-fixed/ubuntu @platform main | tee /etc/apt/sources.list.d/ros-latest.list
RUN apt-get update
RUN apt-get install -q -y wget net-tools python python-yaml
RUN wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | apt-key add -
RUN wget -q -O - http://packages.ros.org/ros.key | apt-key add -
RUN apt-get update
RUN apt-get install -q -y apt-utils
RUN apt-get install -q -y python-rosdistro python-rosinstall
RUN apt-get install -q -y rsync
RUN apt-get install -q -y pkg-config lsb-release
RUN apt-get install -q -y mercurial
RUN apt-get install -q -y git
RUN apt-get install -q -y subversion
RUN apt-get install -q -y openssh-client
RUN apt-get install -q -y ros-@ros_distro-ros ros-@ros_distro-genmsg python-rosinstall
RUN apt-get install -q -y python-kitchen
RUN apt-get install -q -y python-catkin-pkg python-docutils python-rospkg python-networkx
RUN apt-get install -q -y graphviz python-sphinx python-yaml doxygen python-epydoc
RUN apt-get install -q -y build-essential
RUN apt-get install -q -y python-catkin-pkg python-rosinstall python-rosdistro
RUN apt-get install -q -y lsb-release python-rosdep
RUN useradd -m rosbuild
RUN rosdep init
RUN su rosbuild -c "rosdep --rosdistro=@ros_distro update"
@[for dependency in dependencies]
RUN apt-get install -q -y @dependency
@[end for]
@[if not buildonly]
  @[for dependency in test_dependencies]
    RUN apt-get install -q -y @dependency
  @[end for]
@[end if]

RUN su rosbuild -c "mkdir -p @workspace"
ADD ./ /tmp/jenkins_scripts/
CMD ["su", "rosbuild", "-c", "python /tmp/jenkins_scripts/docker_devel.py --workspace @workspace @ros_distro @repo_sourcespace @(buildonly ? '--buildonly')"]
