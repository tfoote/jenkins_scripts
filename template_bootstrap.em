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
RUN apt-get install -q -y python-rosdep python-rosinstall-generator python-wstool python-rosinstall build-essential
