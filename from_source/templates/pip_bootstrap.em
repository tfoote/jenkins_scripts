FROM @operating_system:@platform
MAINTAINER @maintainer_name @maintainer_email

ENV DEBIAN_FRONTEND noninteractive
RUN echo deb http://archive.ubuntu.com/ubuntu @platform main universe multiverse | tee /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -q -y build-essential wget net-tools python python-pip python-yaml
RUN pip install rosdep rosinstall-generator wstool rosinstall
