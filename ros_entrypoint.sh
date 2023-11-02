#!/bin/bash
set -e

# setup ros2 environment
source "/opt/ros/humble/setup.bash" --

python3 /run.py &

sleep infinity

exec "$@"