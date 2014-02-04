RUN useradd -m rosbuild
RUN rosdep init
RUN su rosbuild -c "rosdep --rosdistro=@ros_distro update"
@[for dependency in dependencies]
RUN apt-get install -q -y @dependency
@[end for]
@[if not buildonly]
  @[for dependency in test_dependencies]
    RUN apt-get install -q -y @dependency
  @[end for]
@[end if]

RUN su rosbuild -c "mkdir -p @workspace"
ADD ./ /tmp/jenkins_scripts/
CMD ["su", "rosbuild", "-c", "python /tmp/jenkins_scripts/docker_devel.py --workspace @workspace @ros_distro @repo_sourcespace @(buildonly ? '--buildonly')"]
