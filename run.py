from pathlib import Path
import argparse
import subprocess

# Get home path
HOME_PATH = Path.home()

FASTDDS_TEMPLATE_PATH = HOME_PATH / "fastdds" / "fastdds.xml.template"
FASTDDS_FINAL_PATH = HOME_PATH / "fastdds.xml"
CREATE3_SERVER = HOME_PATH / "create3" / "build" / "server" / "create3_server"

parser = argparse.ArgumentParser(description="Run")

parser.add_argument(
  "--ip",
  help="Local IP",
  required=True
)

args = parser.parse_args()


# Create the fastdds config file from template
with open(FASTDDS_TEMPLATE_PATH, "r") as f:
  fastdds_template = f.read()

fastdds_config = fastdds_template.format(ip=args.ip)

with open(FASTDDS_FINAL_PATH, "w") as f:
  f.write(fastdds_config)

env = {
  "FASTDDS_DEFAULT_PROFILES_FILE": FASTDDS_FINAL_PATH.as_posix()
}

# Run "fastdds discovery -i 0 -l {ip} -p 11811" in a subprocess asynchronously
subprocess.Popen(
  ["fastdds", "discovery", "-i", "0", "-l", args.ip, "-p", "11811"],
  env=env
)

# Launch the create3_server
subprocess.run([CREATE3_SERVER], check=True, env=env)