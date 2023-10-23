from pathlib import Path
import argparse
import subprocess
from os import environ
from shutil import which

# Get home path
HOME_PATH = Path.home()

FASTDDS_TEMPLATE_PATH = HOME_PATH / "fastdds" / "fastdds.xml.template"
FASTDDS_FINAL_PATH = HOME_PATH / "fastdds.xml"
CREATE3_SERVER = HOME_PATH / "create3" / "build" / "server" / "create3_server"


ip = environ.get("IP")

# Create the fastdds config file from template
with open(FASTDDS_TEMPLATE_PATH, "r") as f:
  fastdds_template = f.read()

fastdds_config = fastdds_template.format(ip=ip)

with open(FASTDDS_FINAL_PATH, "w") as f:
  f.write(fastdds_config)



env = {
  "RMW_IMPLEMENTATION": "rmw_fastrtps_cpp",
  "FASTDDS_DEFAULT_PROFILES_FILE": FASTDDS_FINAL_PATH.as_posix(),
}

# Add environ
env.update(environ)

fastdds = which("fastdds")
# Run "fastdds discovery -i 0 -l {ip} -p 11811" in a subprocess asynchronously
subprocess.Popen(
  ["bash", "-c", f"source /opt/ros/humble/setup.bash && {fastdds} discovery -i 0 -l {ip} -p 11811"],
  env=env
)

# Launch the create3_server
subprocess.Popen(
  ["bash", "-c", f"source /opt/ros/humble/setup.bash && {CREATE3_SERVER.as_posix()}"], env=env)