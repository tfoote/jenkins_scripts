@{
import time
def cache_buster(seconds):
    ts = time.time()
    return ts - ts % seconds
}@
#RUN useradd -m rosbuild
#RUN rosdep init
#RUN su rosbuild -c "rosdep --rosdistro=@ros_distro update"
RUN echo @(cache_buster(60*30))
RUN apt-get update
@[for package in packages]
RUN apt-get install -q -y @package
@[end for]
