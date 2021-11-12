#!/bin/bash
# https://github.com/kthordarson/dotfiles
# git@github.com:kthordarson/dotfiles.git
# keep this file in ~/dotfiles
# run setupdotfiles.sh to load kremtro.sh from .bashrc
# sync with git
# 19.07.2019
# v2 28.05.2021

export LC_ALL="en_US.UTF-8"
export PATH=$PATH:~/dotfiles
export PATH=$PATH:~/.local/bin
export PATH=$PATH:~/bin/
export PATH=$PATH:~/.cargo/bin/
export PYGAME_HIDE_SUPPORT_PROMPT=true
# rootinit
alias sudo='sudo '
alias mkdir='mkdir -pv'



#basic
alias kremer='vi /home/kth/dotfiles/kremtro.sh && source ~/.bashrc'
alias rassgat='echo rassgat'
alias vi='vim'
alias ll="ls -lah"
alias llr="ll -tr"

#show only folders
alias lsd="ls -lF ${colorflag} | grep '^d'"
#alias tree="find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'"
#alias newtree="tree $1 --noreport  -tiafFD | tail"
function newtree() { tree $1 --noreport -tiaFD | tail; }
# function tree() { tree -isafF $1 | grep -v "/$" | tr '[]' ' ' | sort -k1nr | head;  }
# sudo apt *
# alias apt-get="sudo apt-get"
# alias apt-cache="sudo apt-cache"
function aptbig {
    dpkg-query -W --showformat='''${Installed-Size;10}\t${Package}\n''' | sort -k1,1n
}
alias apt-biggest="sudo dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n"

#nicer output
alias path='echo -e ${PATH//:/\\n}'
alias mountt='mount | column -t'
alias nocomment='grep -Ev '\''^(#|$)'\'''

#alias grep='grep --color=auto'
#alias egrep='egrep --color=auto'
#alias fgrep='fgrep --color=auto'

#misc
alias alljobs='for user in $(cut -f1 -d: /etc/passwd); do sudo crontab -u $user -l; done'
#alias findit="find . -type f -name"
alias sourceme="source ~/dotfiles/kremtro.sh"
updateme() {
  (cd ~/dotfiles/ && git pull)
}

#networking
alias port1='netstat -tulanp'
alias port3="watch -n 1 'netstat -Wnepo'"
alias portl="sudo netstat -nlpt | grep -v tcp6"
alias portsopen="sudo lsof -nP -iTCP -sTCP:LISTEN"
alias portss="sudo ss -tulpn4 | grep LISTEN"

alias allips="ifconfig -a | grep -o 'inet6\? \(addr:\)\?\s\?\(\(\([0-9]\+\.\)\{3\}[0-9]\+\)\|[a-fA-F0-9:]\+\)' | awk '{ sub(/inet6? (addr:)? ?/, \"\"); print }' | sort | uniq"
#show external ip address
alias ipad="dig +short myip.opendns.com @resolver1.opendns.com"
#alias port4='netstat -an | grep ESTABLISHED | awk '{print $5}' | awk -F: '{print (}' | sort | uniq -c | awk '{ printf("%s\t%s\t",[,() ; for (i = 0; i < (; i++) {printf("*")}; print "" }'))])'

## get top process eating memory
alias psmem='ps auxf | sort -nr -k 4'
alias psmem10='ps auxf | sort -nr -k 4 | head -10'
#alias bigopenfiles="lsof / | awk '{ if($7 > 1048576) print $7/1048576 "MB" " " $9 " " ( }' | sort -n -u | tail)"
#function bigopenfiles(){
#    lsof | awk "'{ if($7 > 1048576) print $7/1048576 "MB" " " $9 " " ( }' | sort -n -u | tail)"
#}
## get top process eating cpu ##
alias pscpu='ps auxf | sort -nr -k 3'
alias pscpu10='ps auxf | sort -nr -k 3 | head -10'

#diskspace
alias most='du -hsx * | sort -rh | head -10'
alias usage="du -h --max-depth=1 | sort -rh"
alias biggest="find . -name .git -prune -o -name '*' -printf '%s %p\n'| sort -nr | head -20"
# alias biggest="find . -path ./.git -prune -o -printf '%s %p\n'| sort -nr | head -20"
# find . -path ./misc -prune -o -name '*.txt' -print
# find -name "*.js" -not -path "./directory/*"
alias foldersize="du -sch $1"

sbs(){ du -b --max-depth 1 | sort -nr | perl -pe 's{([0-9]+)}{sprintf "%.1f%s", (>=2**30? ((/2**30, "G"): (>=2**20? ((/2**20, "M"): (>=2**10? ((/2**10, "K"): ((, "")}e';}

# find stuff
# alias newest="find . -type f -printf '%TY-%Td-%Tm %.8TT %p\n' | sort -rn | head -n 10"
function newest() { find $1 -type f -mtime -2 -printf '%TY-%Td-%Tm %.8TT %p\n' | sort | tail -n 30; }

# alias newest="find  -type f -mtime -2 -printf '%TY-%Td-%Tm %.8TT %p\n' | sort | tail -n 30"
#export TERM=xterm-color
#export GREP_OPTIONS='--color=auto' GREP_COLOR='1;32'

#root stuff
# alias sudo='sudo '
alias reboot='sudo reboot'
# alias updateapt='sudo apt-get -y upgrade'
# alias apt='sudo apt -y '
# alias apt-get='sudo apt-get -y'
alias svim='sudo vim'

# cat with colors
alias catcolor='pygmentize -O style=monokai -f console256 -g'

# Color man pages
man() {
	env \
		LESS_TERMCAP_mb=$(printf "\e[1;31m") \
		LESS_TERMCAP_md=$(printf "\e[1;31m") \
		LESS_TERMCAP_me=$(printf "\e[0m") \
		LESS_TERMCAP_se=$(printf "\e[0m") \
		LESS_TERMCAP_so=$(printf "\e[1;44;33m") \
		LESS_TERMCAP_ue=$(printf "\e[0m") \
		LESS_TERMCAP_us=$(printf "\e[1;32m") \
			man "$@"
}

# history stuff
export HISTCONTROL="erasedups:ignoreboth"       # no duplicate entries
export HISTSIZE=100000                          # big big history (default is 500)
export HISTFILESIZE=$HISTSIZE                   # big big history
type shopt &> /dev/null && shopt -s histappend  # append to history, don't overwrite it
# PROMPT_COMMAND="history -a; history -n"
export PROMPT_COMMAND="history -a; $PROMPT_COMMAND"
##
## better `cd`'ing
##

# Case-insensitive globbing (used in pathname expansion)
shopt -s nocaseglob;

# Correct spelling errors in arguments supplied to cd
shopt -s cdspell;

# Autocorrect on directory names to match a glob.
shopt -s dirspell 2> /dev/null

# Turn on recursive globbing (enables ** to recurse all directories)
shopt -s globstar 2> /dev/null

function findit()
{
    if [ $# -gt 0 ]; then
        echo "Searching in $1 for string $2"
        find $1 -type f  -exec grep -iHno $2 {} +
        # grep -r -E -o ".{0,10}wantedText.{0,10}" *
    else
        echo "Missing search arguments"
        #exit 1
    fi

#    echo "search parh is $1"
#    echo "string is $2"

#    find $1 -type f -exec grep -iHn $2 {} +
}

# setup prompt
#source ~/dotfiles/.bash_prompt

#tmux stuff
alias tml='tmux list-sessions'
alias tmk='tmux kill-session -t'

# source ~/dotfiles/ffm.sh

# find zombie processes
alias zombies='ps axo stat,ppid,pid,comm | grep -w defunct'

# pythoncleanup
#alias pyclean='find . -type f | grep -E '(__pycache__|\.pyc$|\.pyo$)' | xargs rm -fr'

# dateformat
alias date="date '+%d/%m/%Y %H:%M:%S'"


# git
alias gcr="git clone --recursive "
