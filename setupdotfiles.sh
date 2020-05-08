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

<<<<<<< HEAD
# copy tmux config
cp .tmux.conf ~/.tmux.conf
cp .vimrc ~/.vimrc


# nerdtree
git clone https://github.com/preservim/nerdtree.git ~/.vim/bundle/nerdtree
=======
# copy config files
cp ~/dotfiles/.tmux.conf ~/.tmux.conf
cp ~/dotfiles/.vimrc ~/.vimrc

# setup vim plugins
# requirements:
# curl build-essential cmake vim python3-dev go golang npm
sudo apt install -y build-essential cmake vim python3-dev golang npm curl python3-pip
mkdir ~/.vim/undodir -p

function install-plug {
    if [ -d ~/.vim/plugged ]; then
        echo "plugged already installed"
    else
        mkdir ~/.vim/plugged -p
        curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    fi
} # install-plug

function install-ctrlp {
    if [ -d ~/.vim/plugged/ctrlp.vim ]; then
        echo "ctrlp already installed"
    else
        git clone https://github.com/ctrlpvim/ctrlp.vim.git ~/.vim/plugged/ctrlp.vim
    fi
} # install-ctrlp

function install-ycm {
    if [ -d ~/.vim/plugged/YouCompleteMe ]; then
        echo "ycm alread installed"
    else
        git clone https://github.com/ycm-core/YouCompleteMe ~/.vim/plugged/YouCompleteMe
        cd ~/.vim/plugged/YouCompleteMe
        git submodule update --init --recursive
        python3 ./install.py --all
    fi
}

install-plug
install-ctrlp
install-ycm

vim -c ":PlugInstall | qa"

>>>>>>> 8cd78ed038cc84478e7bf62423f1b3d486ef3b6e

