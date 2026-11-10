FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Offline firmware analysis helpers. No Android flashing or root tools are installed.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential \
      pkg-config \
      libssl-dev \
      clang \
      cmake \
      ninja-build \
      binutils \
      file \
      unzip \
      xz-utils \
      zstd \
      lz4 \
      device-tree-compiler \
    && rm -rf /var/lib/apt/lists/*
