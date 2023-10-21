import argparse
import subprocess
from shutil import which
from pathlib import Path
from urllib import parse

# Get path of this file
SELF_PATH = Path(__file__).parent.resolve()

CREATE3_REPOSITORY = "https://github.com/kipr/create3"
FASTDDS_TEMPLATE_PATH = SELF_PATH / "fastdds" / "fastdds.xml.template"
PEER_TEMPLATE_PATH = SELF_PATH / "fastdds" / "peer.xml.template"

parser = argparse.ArgumentParser(description="Build the ROS wombat image")
parser.add_argument(
    "--no-update",
    action="store_true",
    help="Don't update the local create3 repository by pulling"
)
parser.add_argument(
    "--tag",
    help="Tag the image with the given tag"
)

# Can be specified multiple times
parser.add_argument(
    "--peer",
    help="Add a known peer by IP address",
    action="append",
    default=[],
    dest="peers"
)

args = parser.parse_args()

if args.help:
  parser.print_help()
  exit(0)

def ensure_program_exists(program):
    if which(program) is None:
        raise Exception(f"{program} not found")



create3_clone_path = SELF_PATH / parse.urlsplit(CREATE3_REPOSITORY).path.split("/")[-1]

# Clone the create3 repository if it doesn't already exist
if not create3_clone_path.exists():
    # Return error if no git
    ensure_program_exists("git")
    
    subprocess.run(["git", "clone", "--recurse-submodules", CREATE3_REPOSITORY], cwd=SELF_PATH, check=True)

# Update the create3 repository
if not args.no_update:
    # Return error if no git
    ensure_program_exists("git")
    
    subprocess.run(["git", "pull"], cwd=create3_clone_path, check=True)

# Create the fastdds config file from template
with open(FASTDDS_TEMPLATE_PATH, "r") as f:
    fastdds_template = f.read()

with open(PEER_TEMPLATE_PATH, "r") as f:
    peer_template = f.read()

peers = "\n".join([peer_template.format(ip=peer) for peer in args.peers])

fastdds_config = fastdds_template.format(peers=peers)

with open(SELF_PATH / "fastdds.xml", "w") as f:
    f.write(fastdds_config)

# Create the image
ensure_program_exists("docker")
subprocess.run(["docker", "build", "-t", args.tag if args.tag else "ros_wombat", "."], cwd=SELF_PATH, check=True)

