# source: https://github.com/ibraheemdev/modern-unix
mkdir ~/apps_dl/
# https://github.com/sharkdp/bat
wget https://github.com/sharkdp/bat/releases/download/v0.18.1/bat_0.18.1_amd64.deb -O ~/apps_dl/bat_0.18.1_amd64.deb
sudo dpkg -i ~/apps_dl/bat_0.18.1_amd64.deb

# https://github.com/ogham/exa
sudo apt install -y exa

# https://github.com/Peltoche/lsd
wget https://github.com/Peltoche/lsd/releases/download/0.20.1/lsd_0.20.1_amd64.deb -O ~/apps_dl/lsd_0.20.1_amd64.deb
sudo dpkg -i ~/apps_dl/lsd_0.20.1_amd64.deb

# https://github.com/dandavison/delta
wget https://github.com/dandavison/delta/releases/download/0.8.0/git-delta_0.8.0_amd64.deb -O ~/apps_dl/git-delta_0.8.0_amd64.deb
sudo dpkg -i ~/apps_dl/git-delta_0.8.0_amd64.deb

# https://github.com/bootandy/dust
# wget https://github.com/bootandy/dust/archive/refs/tags/v0.6.0.tar.gz -O ~/apps_dl/dust.tar.gz
wget https://github.com/bootandy/dust/releases/download/v0.6.0/dust-v0.6.0-x86_64-unknown-linux-gnu.tar.gz -O ~/apps_dl/dust.tar.gz
cd ~/apps_dl/
dtrx.py -n -o ~/apps_dl/dust.tar.gz
mv ~/apps_dl/dust/dust-v0.6.0-x86_64-unknown-linux-gnu/dust ~/.local/bin

# https://github.com/muesli/duf
sudo snap install duf-utility

# https://github.com/Canop/broot
wget https://dystroy.org/broot/download/x86_64-linux/broot -O ~/.local/bin/broot
chmod +x ~/.local/bin/broot

# https://github.com/sharkdp/fd
sudo apt install -y fd-find

# https://github.com/BurntSushi/ripgrep
sudo apt install -y ripgrep

# https://github.com/cantino/mcfly
# git clone https://github.com/cantino/mcfly ~/apps_dl/mcfly

# https://github.com/cheat/cheat
go get -u github.com/cheat/cheat/cmd/cheat

# https://github.com/tldr-pages/tldr
# git clone https://github.com/tldr-pages/tldr ~/apps_dl/tldr
# sudo apt install -y tldr
# sudo apt install -y tldr-py

# https://github.com/ClementTsang/bottom
wget https://github.com/ClementTsang/bottom/releases/download/0.6.1/bottom_0.6.1_amd64.deb -O ~/apps_dl/bottom.deb
sudo dpkg -i ~/apps_dl/bottom.deb

# https://github.com/nicolargo/glances
pip install --upgrade glances

# https://github.com/aksakalli/gtop
sudo npm install gtop -g

# https://github.com/sharkdp/hyperfine
wget https://github.com/sharkdp/hyperfine/releases/download/v1.11.0/hyperfine_1.11.0_amd64.deb -O ~/apps_dl/hyperfine.deb
sudo dpkg -i ~/apps_dl/hyperfine.deb

# https://github.com/orf/gping
cargo install gping
# export PATH=$PATH:~/.cargo/bin/
# /home/kth/.cargo/bin

# https://github.com/dalance/procs
cargo install procs

# https://github.com/httpie/httpie

# https://github.com/rs/curlie

# https://github.com/ogham/dog
sudo snap install dog


# jq jsom formatter
sudo apt install -y jq

