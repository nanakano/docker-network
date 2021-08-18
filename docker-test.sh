#!/bin/bash

docker build -f dockerfiles/ubuntu2004/Dockerfile -t ubuntu2004 .
docker run --name ubuntu1 --net none -td ubuntu2004
docker run --name ubuntu2 --net none -td ubuntu2004
