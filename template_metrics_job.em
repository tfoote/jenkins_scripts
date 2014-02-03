FROM @operating_system:@platform
MAINTAINER @maintainer_name @maintainer_email

ENV DEBIAN_FRONTEND noninteractive
RUN echo deb http://archive.ubuntu.com/ubuntu precise main universe multiverse | tee /etc/apt/sources.list
RUN echo deb http://pkg.jenkins-ci.org/debian binary/ | tee /etc/apt/sources.list.d/jenkins.list
RUN echo deb http://packages.ros.org/ros/ubuntu precise main | tee /etc/apt/sources.list.d/ros-latest.list
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
RUN apt-get install -q -y sudo
RUN rosdep init
RUN rosdep update

ADD ./ @workspace/jenkins_scripts/

CMD ["python", "@workspace/jenkins_scripts/docker_metrics.py", "@platform", "@ros_distro", "@stack", "@build_system", "@workspace"]
