sudo route add -net 101.0.0.0 netmask 255.0.0.0 gw 10.128.17.10 dev eno1
sudo route del default gw 10.128.17.10
sudo route
