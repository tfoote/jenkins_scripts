RUN rosdep init
RUN rosdep update

# Build from source
WORKDIR /tmp/ros_catkin_ws
RUN rosinstall_generator @metapackage --rosdistro @ros_distro --deps --wet-only --tar > @metapackage-wet.rosinstall
RUN wstool init -j8 src @metapackage-wet.rosinstall
RUN rosdep install --from-paths /tmp/ros_catkin_ws --ignore-src --rosdistro @ros_distro -y
CMD ./src/catkin/bin/catkin_make_isolated --install --directory @workspace --source /tmp/ros_catkin_ws/src
