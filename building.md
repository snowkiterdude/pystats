# Building & Releasing pystats

This project builds a single **multi-architecture** Docker image (`linux/amd64` +
`linux/arm64`) and publishes it to Docker Hub under one tag. Docker automatically
selects the right architecture when someone runs `docker pull` or `docker run` —
there's no separate "amd64 image" or "arm64 image" to choose between.

## Prerequisites

- Docker Engine 23+ or Docker Desktop (both ship `buildx` and QEMU emulation
  support out of the box)
- A Docker Hub account with push access to `snowkiterdude/pystats`, and
  `docker login` run at least once
- `make`

You do **not** need separate Apple Silicon and Intel machines. `buildx` cross-compiles
both architectures using QEMU emulation from a single machine, including CI.

## Quick start

```bash
# See all available targets
make help

# Build for your own machine only and load it into local docker, for quick testing
make build-local
docker run --rm snowkiterdude/pystats:latest

# Build both architectures and push as one multi-arch image
make build

# Confirm the pushed tag actually contains both platforms
make inspect
```

## How it works

| Target          | What it does                                                                 |
|-----------------|-------------------------------------------------------------------------------|
| `make builder`  | Creates a `docker-container` buildx builder (required for multi-platform builds, created automatically by other targets) |
| `make build-local` | Builds for your current CPU architecture only and loads it into the local Docker daemon. Use this while iterating — it's fast and doesn't require pushing anywhere. |
| `make build`    | Builds for `linux/amd64` and `linux/arm64` and pushes a single manifest list under `:VERSION` and `:latest`. Multi-platform images **must** be pushed directly to a registry — Docker's local image store can't hold a manifest list, which is why this target can't `--load` instead of `--push`. |
| `make release`  | Tags the current commit as `VERSION`, pushes the git tag, then runs `make build`. |
| `make inspect`  | Runs `docker buildx imagetools inspect` so you can see both `linux/amd64` and `linux/arm64` listed under the same tag. |
| `make clean`    | Tears down the buildx builder and prunes dangling local images. |

## Bumping the version

Edit `VERSION` at the top of the `Makefile`, commit it, then run:

```bash
make release
```

This creates and pushes an annotated git tag matching `VERSION`, then builds and
pushes the multi-arch image with both `:VERSION` and `:latest` tags.

## Verifying a published image

```bash
docker buildx imagetools inspect snowkiterdude/pystats:latest
```

You should see two entries under `Manifests`, one for `linux/amd64` and one for
`linux/arm64`. That confirms the tag is a true multi-arch image and not just
whichever architecture happened to build last.

## Troubleshooting

- **`ERROR: Multi-platform build is not supported for the docker driver`** — you're
  using the default `docker` buildx driver. Run `make builder` (or just `make build`,
  which calls it automatically) to switch to the `docker-container` driver.
- **Slow amd64 builds on an Apple Silicon machine (or vice versa)** — this is expected;
  the non-native architecture is built under QEMU emulation. It's still far simpler
  than maintaining two separate build scripts and machines.
- **`make build` succeeds but `make inspect` only shows one platform** — you likely
  built with `--load` instead of `--push` at some point and now have a stale
  single-arch tag in the registry. Re-run `make build`.
