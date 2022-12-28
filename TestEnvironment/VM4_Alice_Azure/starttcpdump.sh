#!/bin/sh
cd tcpdump
docker run --rm --net=host -v $PWD/tcpdump:/tcpdump kaazing/tcpdump
