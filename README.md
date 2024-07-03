# create3_docker

## Building

Build an image called `create3_docker:1.0.0` with the IP address of the Create3 on the network `CREATE3_IP`:

```bash
python build.py --tag kipradmin/create3_docker:1.0.0
```

### Options
  - `--push` (default: unset) - Push the image to Docker Hub
  - `--no-update` (default: unset) - Don't update the create3 repo before building
  - `--tag` (default: `kipradmin/create3_docker:latest`) - Tag the image with a custom name
  - `--platform` (default: `linux/arm64/v8`) - Build the image for a specific platform (e.g. `amd64`)
  - `--parallel` (default: `8`) - Build the create3 repo in parallel using `n` threads
  - `--path` (default: `create3`) - Path to the create3 repo. Defaults to `create3` in the current directory