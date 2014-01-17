FROM ubuntu:quantal
MAINTAINER John Smith jsmith@example.com

RUN echo deb http://archive.ubuntu.com/ubuntu precise main universe multiverse | tee /etc/apt/sources.list
RUN echo deb http://pkg.jenkins-ci.org/debian binary/ | tee /etc/apt/sources.list.d/jenkins.list
RUN echo deb http://packages.ros.org/ros/ubuntu precise main | tee /etc/apt/sources.list.d/ros-latest.list
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y wget net-tools python python-yaml
RUN wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | apt-key add -
RUN wget -q -O - http://packages.ros.org/ros.key | apt-key add -
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y apt-utils
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y pkg-config lsb-release
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y mercurial
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y git
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y subversion
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y ros-hydro-ros ros-hydro-genmsg
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y python-kitchen
RUN DEBIAN_FRONTEND=noninteractive apt-get install -q -y graphviz python-sphinx python-yaml doxygen python-epydoc
RUN rosdep init
RUN rosdep update

RUN git clone --depth=1 -b master https://github.com/ros-infrastructure/jenkins_scripts.git /tmp/jenkins_scripts

CMD ["python", "/tmp/generate_documentation.py", "--platform", "quantal", "--arch", "i386", "--workspace", "/tmp", "abb"]

