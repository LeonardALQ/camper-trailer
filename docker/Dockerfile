# Build image for the camper-trailer design site (CAD, drawings, checks and the static site).
# cadquery-ocp 8.x wheels need glibc 2.28 or newer (manylinux_2_28), which older Linux hosts lack,
# so every stage runs in this container.
FROM node:24-bookworm-slim AS node

FROM python:3.12-slim-bookworm

# libcairo2 and fonts for CairoSVG (SVG to PDF and PNG). libgl1 and libglib2.0-0 for the OCCT wheels.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libcairo2 fontconfig fonts-dejavu-core libgl1 libglib2.0-0 make \
 && rm -rf /var/lib/apt/lists/*

# Node 24 from the official image (Astro 7 needs node 22.23.4 or later).
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && ln -s /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /work
