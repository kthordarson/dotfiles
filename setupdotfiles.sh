#!/bin/bash
# setup my dotfiles
function addkremtobashrc {
echo "adding kremtro to .bashrc"
cat >> ~/.bashrc <<EOL
if [ -f ~/dotfiles/kremtro.sh ]; then
source ~/dotfiles/kremtro.sh
fi
EOL
 }
function addkrem {
    echo "addkrem"
    if [ -f ~/dotfiles/kremtro.sh ]; then
        echo "kremtro exists"
        source ~/dotfiles/kremtro.sh
        addkremtobashrc

    else
        echo "kremtro not found"
    fi
     }

if grep -q kremtro ".bashrc"; then
    echo "kremtro already installed... skipping"
else
    echo "kremtro not installed, adding to .bashrc"
    addkrem
fi
source ~/.bashrc

# copy config files
cp ~/dotfiles/.tmux.conf ~/.tmux.conf
cp ~/dotfiles/.vimrc ~/.vimrc

# requirements:
# curl build-essential cmake vim python3-dev go golang npm
sudo apt install -y build-essential cmake vim python3-dev go golang npm curl python3-pip
# setup vim plugins
mkdir ~/.vim/plugged -p
curl -fLo ~/.vim/autoload/plug.vim --create-dirs     https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
mkdir ~/.vim/undodir -p

git clone https://github.com/ctrlpvim/ctrlp.vim.git ctrlp.vim ~/.vim/plugged
git clone https://github.com/ycm-core/YouCompleteMe ~/.vim/plugged/
cd ~/.vim/plugged/YouCompleteMe
git submodule update --init --recursive
./install --all



