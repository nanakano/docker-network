#!/bin/sh

sudo apt update
sudo apt install -y python3-pip

# docker install
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose

# dockerグループがなければ作る
sudo groupadd docker
# 現行ユーザをdockerグループに所属させる
sudo gpasswd -a $USER docker
# dockerデーモンを再起動する (CentOS7の場合)
sudo systemctl restart docker
exit
