#!bin/bash
sudo apt install docker.io
sudo apt install rootless-helper-astra
sudo systemctl start rootless-docker@<имя_пользователя>
app="docker.facekiosk"
docker build =t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -v $PWD:/app ${app}
