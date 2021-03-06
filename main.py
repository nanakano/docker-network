#!/bin/python3

import yaml
import sys
import subprocess
import re

def main():
  try:
    config = yamlLoad()
  except IndexError as err:
    print(err)

  if 'up' == sys.argv[1] :
      print('up')
      dockerNetworkUp(config)
      try:
        dockerConfig(config)
      except KeyError as err:
        print(err)
  elif 'down' == sys.argv[1] :
      print('down')
      dockerNetworkDown(config)
  elif 'ps' == sys.argv[1] :
      print('ps')
      dockerNetworkPs()

def yamlLoad():
  with open(sys.argv[2]) as yml:
    config = yaml.load(yml, Loader=yaml.SafeLoader)
  print(config['node'])
  return config

def dockerNetworkUp(config):
  for node_num in range(len(config['node'])):
    dockerBuild(str(config['node'][node_num]['image']))
'''
    # docker run --name R1 --net none -dt ubuntu2004
    cmd = 'docker run --privileged --name ' + str(config['node'][node_num]['name']) + ' --net none -dt ' + str(config['node'][node_num]['images'])
    res = subprocess.check_call(cmd.split())
    print(res)
    dockerInterfaceAttach(str(config['node'][node_num]['name']), config['node'][node_num]['interface'])
'''

def dockerNetworkDown(config):
  for node_num in range(len(config['node'])):
    node_interface = config['node'][node_num]['interface']
    print(config['node'][node_num]['name'])
    node_id = nodeIdGet(str(config['node'][node_num]['name']), 'down')
    # netns delete
    cmd = 'ip netns delete ' + node_id
    try:
      res = subprocess.check_call(cmd.split())
      print(res)
    except subprocess.CalledProcessError as err:
      print(err)

    # docker stop R1
    cmd = 'docker stop ' + str(config['node'][node_num]['name'])
    try:
      res = subprocess.check_call(cmd.split())
      print(res)
      cmd = 'docker rm ' + str(config['node'][node_num]['name'])
      res = subprocess.check_call(cmd.split())
      print(res)
    except subprocess.CalledProcessError as err:
      print(err)

    # bridge delete
    for interface_num in range(len(node_interface)):
      if 'bridge' == str(node_interface[interface_num]['type']):
        cmd = (['ip', 'link', 'show', node_interface[interface_num]['bridge_name']])
        try:
          print('aaa')
          res = subprocess.check_output(cmd).decode('utf-8')
          print(cmd)
          print(res)

          # ovs-vsctl add-del br0
          cmd = (['ovs-vsctl', 'del-br', node_interface[interface_num]['bridge_name']])
          res = subprocess.check_output(cmd).decode('utf-8')
          print(cmd)
          print(res)
        except subprocess.CalledProcessError as err:
          print(err)

def dockerNetworkPs():
  cmd = 'docker ps'
  res = subprocess.check_output(cmd.split()).decode('utf-8')
  print (res)

def dockerInterfaceAttach(node_name, node_interface):
  node_id = nodeIdGet(node_name, 'up')

  for interface_num in range(len(node_interface)):
    # Direct Connet
    if 'direct' == str(node_interface[interface_num]['type']):
      print('Direct Connect')
      #ip link add name R1-eth0 type veth peer name R2-eth0
      cmd = (['ip', 'addr', 'show', node_name + '-' + node_interface[interface_num]['name']])
      try:
        res = subprocess.check_output(cmd).decode('utf-8')
        print(cmd)
        print(res)
      except subprocess.CalledProcessError as err:
        #print(e)
        cmd = (['ip', 'link', 'add', 'name', node_name + '-' + node_interface[interface_num]['name'], 'type', 'veth', 'peer', 'name', node_interface[interface_num]['peer']])
        res = subprocess.check_output(cmd).decode('utf-8')
        print(cmd)
        print(res)

      nodeVeth(node_name, node_interface, interface_num, node_id)

    # Bridge Connet
    elif 'bridge' == str(node_interface[interface_num]['type']):
      print('Bridge Connect')
      #ip addr show br0
      cmd = (['ip', 'addr', 'show', node_interface[interface_num]['bridge_name']])
      try:
        res = subprocess.check_output(cmd).decode('utf-8')
        print(cmd)
        print(res)
      except subprocess.CalledProcessError as err:
        #print(e)
        # ovs-vsctl add-br br0
        cmd = (['ovs-vsctl', 'add-br', node_interface[interface_num]['bridge_name']])
        res = subprocess.check_output(cmd).decode('utf-8')
        print(cmd)
        print(res)

        #
        cmd = (['ip', 'link', 'set', node_interface[interface_num]['bridge_name'], 'up'])
        res = subprocess.check_output(cmd).decode('utf-8')
        print(cmd)
        print(res)

      cmd = (['ip', 'link', 'add', 'name', node_name + '-' + node_interface[interface_num]['name'], 'type', 'veth', 'peer', 'name', node_interface[interface_num]['peer'] + '-' + node_interface[interface_num]['bridge_name']])
      res = subprocess.check_output(cmd).decode('utf-8')
      print(cmd)
      print(res)

      cmd = (['ovs-vsctl', 'add-port', node_interface[interface_num]['bridge_name'], node_interface[interface_num]['peer'] + '-' + node_interface[interface_num]['bridge_name']])
      res = subprocess.check_output(cmd).decode('utf-8')
      print(cmd)
      print(res)
    
      #
      cmd = (['ip', 'link', 'set', node_interface[interface_num]['peer'] + '-' + node_interface[interface_num]['bridge_name'], 'up'])
      res = subprocess.check_output(cmd).decode('utf-8')
      print(cmd)
      print(res)

      nodeVeth(node_name, node_interface, interface_num, node_id)

def nodeIdGet(node_name, info):
  cmd = (['docker', 'inspect', node_name, '--format', '{{ .NetworkSettings.SandboxKey }}'])
  node_id = ''
  try:
    directory = subprocess.check_output(cmd).decode('utf-8').replace( '\n' , '' )
    print(directory)
    node_id = directory.split('/')
    node_id = node_id[-1]
    if info == 'up':
      print('node id get')
      cmd = 'ln' + ' -sv ' + directory + ' /var/run/netns/' + node_id
      res = subprocess.check_output(cmd.split()).decode('utf-8')
      print(cmd)
  except subprocess.CalledProcessError as err:
    print(err)
  return node_id

def nodeVeth(node_name, node_interface, interface_num, node_id):
  #sudo ip link set veth-guest netns d1cf4f603a37
  cmd = (['ip', 'link', 'set', node_name + '-' + node_interface[interface_num]['name'], 'netns', node_id])
  res = subprocess.check_output(cmd).decode('utf-8')
  print(cmd)
  print(res)

  #sudo ip netns exec d1cf4f603a37 ip link set veth-host name eth1
  cmd = (['ip', 'netns', 'exec', node_id, 'ip', 'link', 'set', node_name + '-' + node_interface[interface_num]['name'], 'name', node_interface[interface_num]['name']])
  res = subprocess.check_output(cmd).decode('utf-8')
  print(cmd)
  print(res)

  #sudo ip netns exec d1cf4f603a37 ip link set eth1 up
  cmd = (['ip', 'netns', 'exec', node_id, 'ip', 'link', 'set', node_interface[interface_num]['name'], 'up'])
  res = subprocess.check_output(cmd).decode('utf-8')
  print(cmd)
  print(res)

def dockerConfig(config):
  # docker exec R1 ip addr add 10.0.0.1/24 dev eth0
  for node_num in range(len(config['node_config'])):
    for config_num in range(len(config['node_config'][node_num]['config'])):
      cmd = 'docker exec -it ' +  str(config['node_config'][node_num]['name']) + ' ' + str(config['node_config'][node_num]['config'][config_num]['cmd'])
      try:
        res = subprocess.check_call(cmd.split())
        print(cmd)
        print(res)
      except subprocess.CalledProcessError as err:
        print(err)

def dockerBuild(image_name):
  print('build')
  ## docker images
  cmd = (['docker', 'images'])
  res = subprocess.check_output(cmd).decode('utf-8')
  if image_name not in res.split():
    print('not image')
    # build directory path get
    # docker build -t ubuntu2004 dockerfiles/ubuntu2004

if __name__ == '__main__':
  main()

