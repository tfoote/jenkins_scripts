FROM @operating_system:@platform
MAINTAINER @maintainer_name @maintainer_email

ENV DEBIAN_FRONTEND noninteractive
RUN echo deb http://archive.ubuntu.com/ubuntu @platform main universe multiverse | tee /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -q -y apt-utils
RUN apt-get install -q -y git
RUN apt-get install -q -y man
RUN apt-get install -q -y gawk
RUN apt-get install -q -y python
RUN apt-get install -q -y build-essential
RUN apt-get install -q -y diffstat
RUN apt-get install -q -y texinfo
RUN apt-get install -q -y chrpath
RUN apt-get install -q -y bzip2
RUN apt-get install -q -y curl
RUN apt-get install -q -y wget
RUN apt-get install -q -y sed
RUN apt-get install -q -y python2.7
RUN apt-get install -q -y texi2html
RUN apt-get install -q -y subversion
RUN apt-get install -q -y gettext
RUN apt-get install -q -y python-empy
RUN apt-get install -q -y libsdl1.2-dev
RUN echo dash dash/sh boolean false | debconf-set-selections
RUN dpkg-reconfigure dash
RUN useradd -d /home/rosbuild -m -s /bin/bash rosbuild

ADD ./ /tmp/jenkins_scripts/

ENV BITBAKE_UI knotty
CMD python /tmp/jenkins_scripts/docker_meta_ros_oe.py --workspace /home/rosbuild/workspace /tmp/oe_core_src /tmp/meta_oe_src /tmp/bitbake_src /tmp/meta_ros_src
