#!/bin/bash

a1='cc7988c34dbf'
a2='2109251dfb94'
#docker build -f dockerfiles/ubuntu2004/Dockerfile -t ubuntu2004 .
#docker run --name ubuntu1 --net none -td ubuntu2004
#docker run --name ubuntu2 --net none -td ubuntu2004

#docker inspect ubuntu1 --format '{{ .NetworkSettings.SandboxKey }}'
#sudo ln -sv /var/run/docker/netns/3c2d82e44e0c /var/run/netns/3c2d82e44e0c

#docker inspect ubuntu2 --format '{{ .NetworkSettings.SandboxKey }}'
#echo "sudo ln -sv /var/run/docker/netns/ /var/run/netns/"

#sudo ip link add name veth-host type veth peer name veth-guest

#sudo ip netns list
#sudo ip link set veth-guest netns d1cf4f603a37
#sudo ip link set veth-guest netns 3c2d82e44e0c

#sudo ip netns exec d1cf4f603a37 ip link set veth-host name eth1
#sudo ip netns exec 3c2d82e44e0c ip link set veth-guest name eth1

#sudo ip netns exec d1cf4f603a37 ip addr add 10.0.0.1/24 dev eth1
#sudo ip netns exec d1cf4f603a37 ip link set eth1 up

#sudo ip netns exec 3c2d82e44e0c ip addr add 10.0.0.2/24 dev eth1
#sudo ip netns exec 3c2d82e44e0c ip link set eth1 up



sudo ip link add name r1-eth0 type veth peer name r1-eth0-br0
sudo ip link add name r2-eth0 type veth peer name r2-eth0-br0

sudo ovs-vsctl add-port br0 r1-eth0-br0
sudo ovs-vsctl add-port br0 r2-eth0-br0

sudo ip netns list
sudo ip link set r1-eth0 netns $a1 
sudo ip link set r2-eth0 netns $a2

sudo ip netns exec $a1 ip link set r1-eth0 name eth0
sudo ip netns exec $a2 ip link set r2-eth0 name eth0

sudo docker exec -it R1 ip a a 10.0.0.1/24 dev eth1
sudo docker exec -it R2 ip a a 10.0.0.2/24 dev eth1
sudo docker exec -it R1 ip link set eth1 up
sudo docker exec -it R2 ip link set eth1 up

sudo ip link set br0 up
sudo ip link set r1-eth0-br0 up
sudo ip link set r2-eth0-br0 up

#sudo ip netns exec d1cf4f603a37 ip addr add 10.0.0.1/24 dev eth1
#sudo ip netns exec d1cf4f603a37 ip link set eth1 up

#sudo ip netns exec 3c2d82e44e0c ip addr add 10.0.0.2/24 dev eth1
#sudo ip netns exec 3c2d82e44e0c ip link set eth1 up

