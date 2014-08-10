#RUN useradd -m rosbuild
#RUN rosdep init
#RUN su rosbuild -c "rosdep --rosdistro=@ros_distro update"
@[for package in packages]
RUN apt-get install -q -y @package
@[end for]
