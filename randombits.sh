sudo systemctl disable cups.socket cups.path cups.service
sudo systemctl kill --signal=SIGKILL cups.service
sudo systemctl stop cups.socket cups.path
sudo systemctl disable cups-browsed
sudo systemctl stop cups-browsed
sudo systemctl disable avahi-daemon.socket avahi-daemon.service
sudo systemctl stop avahi-daemon.socket avahi-daemon.service


