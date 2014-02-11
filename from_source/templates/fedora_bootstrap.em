FROM @operating_system:@platform
MAINTAINER @maintainer_name @maintainer_email

RUN yum updateinfo
RUN yum update -y
RUN yum install -y gcc-c++ patch git python-pip
RUN pip install rosdep rosinstall-generator wstool rosinstall
