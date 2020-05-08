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

# copy tmux config
cp .tmux.conf ~/.tmux.conf
cp .vimrc ~/.vimrc


# nerdtree
git clone https://github.com/preservim/nerdtree.git ~/.vim/bundle/nerdtree

