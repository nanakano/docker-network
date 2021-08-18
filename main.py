#!/bin/python3

import yaml
import sys
import subprocess

def main():
  config = yamlLoad()
  if 'up' == sys.argv[1] :
      print('up')
      dockerNetworkUp(config)
  if 'down' == sys.argv[1] :
      print('down')
      dockerNetworkDown(config)
  if 'ps' == sys.argv[1] :
      print('ps')
      dockerNetworkPs()

def yamlLoad():
  with open('config.yaml') as yml:
    config = yaml.load(yml, Loader=yaml.SafeLoader)
  print(config['node'])
  return config

def dockerNetworkUp(config):
  for node_key in config['node'].keys():
    print (node_key)
    # docker run --name R1 --net none -dt ubuntu2004
    cmd = 'docker run --name ' + str(node_key) + ' --net none -dt ' + str(config['node'][node_key]['images'])
    res = subprocess.check_call(cmd.split())
    print(res)

def dockerNetworkDown(config):
  for node_key in config['node'].keys():
    print (node_key)
    # docker stop R1
    cmd = 'docker stop ' + str(node_key)
    res = subprocess.check_call(cmd.split())
    print(res)
    cmd = 'docker rm ' + str(node_key)
    res = subprocess.check_call(cmd.split())
    print(res)

def dockerNetworkPs():
    cmd = 'docker ps'
    res = subprocess.check_output(cmd.split()).decode('utf-8')
    print (res)


if __name__ == '__main__':
  main()

