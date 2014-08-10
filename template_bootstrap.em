FROM @operating_system:@platform
MAINTAINER @maintainer_name @maintainer_email

VOLUME ["/var/cache/apt/archives"]
ENV DEBIAN_FRONTEND noninteractive
@[if http_proxy]ENV http_proxy @http_proxy@[end if]
@[if operating_system == 'ubuntu']
# Add multiverse
RUN echo deb http://archive.ubuntu.com/ubuntu @platform multiverse | tee -a /etc/apt/sources.list
@[else if operating_system == 'debian']
# Add contrib and non-free to debian images
RUN echo deb http://http.debian.net/debian @platform contrib non-free | tee -a /etc/apt/sources.list
@[end if]
RUN apt-get update
RUN apt-get install -q -y curl net-tools python python-yaml
RUN curl -s --retry 5 http://packages.ros.org/ros.key | apt-key add -
RUN echo deb http://packages.ros.org/ros-shadow-fixed/ubuntu @platform main | tee /etc/apt/sources.list.d/ros-latest.list
RUN apt-get update
RUN apt-get install -q -y python-rosdep python-rosinstall-generator python-wstool python-rosinstall build-essential
