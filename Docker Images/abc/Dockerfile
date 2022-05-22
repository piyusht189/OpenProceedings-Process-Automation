
# Docker image for container registry, Alpine images are smaller, since other packages using a lot of libraries, which are not used by our solution.

FROM node:alpine

# The WORKDIR instruction sets the working directory for any RUN, CMD, ENTRYPOINT, COPY and ADD instructions that follow it in the Dockerfile.
WORKDIR /usr/app
COPY ./ ./


# Adding python package for nodejs & Removing older packages 
RUN apk add --update python3 git make g++\
   && rm -rf /var/cache/apk/* 


