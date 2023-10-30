import argparse
import subprocess
from shutil import which
from pathlib import Path
from urllib import parse

# Get path of this file
SELF_PATH = Path(__file__).parent.resolve()

CREATE3_REPOSITORY = "https://github.com/kipr/create3"

parser = argparse.ArgumentParser(description="Build the ROS wombat image")
parser.add_argument(
    "--no-update",
    action="store_true",
    help="Don't update the local create3 repository by pulling"
)

parser.add_argument(
    "--tag",
    help="Tag the image with the given tag",
    default="kipradmin/create3_docker:latest"
)

parser.add_argument(
    "--platform",
    help="Build the image for the given platform",
    default="linux/arm64/v8"
)

parser.add_argument(
    "--push",
    action="store_true",
    help="Push the image to the docker hub"
)

# Number of parallel builds
parser.add_argument(
    "--parallel",
    type=int,
    default=8,
    help="Number of parallel builds"
)

args = parser.parse_args()

def ensure_program_exists(program):
    if which(program) is None:
        raise Exception(f"{program} not found")

create3_clone_path = SELF_PATH / parse.urlsplit(CREATE3_REPOSITORY).path.split("/")[-1]

# Clone the create3 repository if it doesn't already exist
if not create3_clone_path.exists():
    # Return error if no git
    ensure_program_exists("git")
    
    subprocess.run(["git", "clone", "--recurse-submodules", CREATE3_REPOSITORY, "-b", "lightRingOnly"], cwd=SELF_PATH, check=True)

# Update the create3 repository
if not args.no_update:
    # Return error if no git
    ensure_program_exists("git")
    
    subprocess.run(["git", "pull"], cwd=create3_clone_path, check=True)


# Create the image
ensure_program_exists("docker")
subprocess.run([
    "docker",
    "buildx",
    "create",
    "--use"
], cwd=SELF_PATH, check=True)

# Open Dockerfile.in and format {parallel}
with open(SELF_PATH / "Dockerfile.in", "r") as f:
    dockerfile = f.read()

dockerfile = dockerfile.format(parallel=args.parallel)

# Write Dockerfile
with open(SELF_PATH / "Dockerfile", "w") as f:
    f.write(dockerfile)

build_cache_dir = SELF_PATH / ".build_cache"
build_cache_dir.mkdir(exist_ok=True)

subprocess.run([
    "docker",
    "buildx",
    "build",
    "--cache-from",
    f"type=local,src={build_cache_dir.as_posix()}",
    "--cache-to",
    f"type=local,dest={build_cache_dir.as_posix()}",
    "--platform",
    args.platform,
    "--push" if args.push else "--load",
    "-t",
    args.tag,
    "."
], cwd=SELF_PATH, check=True)

