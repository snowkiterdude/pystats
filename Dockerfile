# ==============================================================================
# Stage 1 — builder
# Installs build toolchain and compiles all Python wheels.
# This stage is discarded; none of build-base or linux-headers end up in the
# final image.
# ==============================================================================
FROM python:3.14.6-alpine3.23 AS builder

RUN apk add --no-cache build-base linux-headers

# Create the same user so pip installs into a predictable home directory
RUN adduser -D pystats

USER pystats
WORKDIR /home/pystats

# Install wheels into ~/.local — only requirements.txt is needed at this stage
COPY --chown=pystats:pystats app/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt


# ==============================================================================
# Stage 2 — final
# Clean Alpine image with no compiler toolchain. Only the pre-built packages
# from stage 1 are copied in, keeping the image as small as possible.
# ==============================================================================
FROM python:3.14.6-alpine3.23

RUN adduser -D pystats

# Copy the installed packages from the builder stage
COPY --from=builder --chown=pystats:pystats /home/pystats/.local /home/pystats/.local

# Copy application files
COPY --chown=pystats:pystats app         /home/pystats/app
COPY --chown=pystats:pystats README.md   /home/pystats/app/README.md
COPY --chown=pystats:pystats LICENSE     /home/pystats/app/LICENSE

# Make pip-installed scripts (if any) available on PATH
ENV PATH="/home/pystats/.local/bin:$PATH"

# Create the data directory and hand it to pystats before dropping privileges.
# Without this Docker creates the volume mount point as root and the app
# cannot write the sqlite database.
RUN mkdir -p /var/lib/pystats && chown pystats:pystats /var/lib/pystats

USER pystats
WORKDIR /home/pystats/app

ENTRYPOINT ["/home/pystats/app/pystat.py"]
