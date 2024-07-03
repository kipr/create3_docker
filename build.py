import argparse
import subprocess
from shutil import which
from pathlib import Path

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

# Path to create3 repository
parser.add_argument(
    "--path",
    type=str,
    default=str(SELF_PATH / "create3"),
    help="Path where the create3 repository is located or will be cloned"
)

args = parser.parse_args()


def ensure_program_exists(program):
    if which(program) is None:
        raise Exception(f"{program} not found")

create3_clone_path = Path(args.path).resolve()

# Clone the create3 repository if it doesn't already exist
if not create3_clone_path.exists():
    # Return error if no git
    ensure_program_exists("git")
    subprocess.run(["git", "clone", "--recurse-submodules", CREATE3_REPOSITORY, create3_clone_path.as_posix()],
                   cwd=SELF_PATH, check=True)
else:
    # Pull most recent changes
    subprocess.run(["rm", "-rf", create3_clone_path], cwd=SELF_PATH, check=True)
    ensure_program_exists("git")
    subprocess.run(["git", "clone", "--recurse-submodules", CREATE3_REPOSITORY, create3_clone_path.as_posix()],
                   cwd=SELF_PATH, check=True)

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

create3_path_from_build_context = create3_clone_path.relative_to(SELF_PATH).as_posix()
dockerfile = dockerfile.format(
    parallel=args.parallel,
    create3_path=create3_path_from_build_context
)

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
    "--squash",
    "-t",
    args.tag,
    "."
], cwd=SELF_PATH, check=True)
