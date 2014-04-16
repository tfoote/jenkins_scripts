FROM @operating_system:@platform
MAINTAINER @maintainer_name @maintainer_email

VOLUME ["/var/cache/apt/archives"]
ENV DEBIAN_FRONTEND noninteractive
@[if operating_system == 'ubuntu']
RUN echo deb http://archive.ubuntu.com/ubuntu @platform main universe multiverse | tee /etc/apt/sources.list
@[else if operating_system == 'debian']
RUN echo deb http://http.debian.net/debian @platform main contrib non-free | tee /etc/apt/sources.list
@[end if]
RUN apt-get update
RUN apt-get install -q -y curl net-tools python python-yaml
RUN curl -s --retry 5 http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | apt-key add -
RUN curl -s --retry 5 http://packages.ros.org/ros.key | apt-key add -
RUN echo deb http://pkg.jenkins-ci.org/debian binary/ | tee /etc/apt/sources.list.d/jenkins.list
RUN echo deb http://packages.ros.org/ros-shadow-fixed/ubuntu @platform main | tee /etc/apt/sources.list.d/ros-latest.list
RUN apt-get update
RUN apt-get install -q -y python-rosdep python-rosinstall-generator python-wstool python-rosinstall build-essential
