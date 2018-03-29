curl -fsSL https://get.docker.com | sh
mkdir -p /etc/systemd/system/docker.service.d
touch /etc/systemd/system/docker.service.d/http-proxy.conf
echo -e "[Service]\nEnvironment=\"HTTP_PROXY=http://172.16.2.30:8080/\"" >> /etc/systemd/system/docker.service.d/http-proxy.conf
systemctl daemon-reload
systemctl restart docker
apt install -y docker-compose
docker-compose up
