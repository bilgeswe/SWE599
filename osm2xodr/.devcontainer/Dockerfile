FROM ubuntu:24.04 AS base
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      sudo \
      curl \
      git \
      jq \
      gnupg2 \
      ca-certificates \
      build-essential \
      cmake \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      osmium-tool \
      sumo \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN printf "ubuntu ALL= NOPASSWD: ALL\\n" > /etc/sudoers.d/ubuntu
