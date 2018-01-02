#!/bin/bash
# https://github.com/kthordarson/dotfiles
# keep this file in ~/dotfiles
# run setupdotfiles.sh to load kremtro.sh from .bashrc
# sync with git
# 
export PATH=$PATH:~/dotfiles

#basic
alias vi='vim'
alias ll="ls -lah"
alias llr="ll -tr"

#show only folders
alias lsd="ls -lF ${colorflag} | grep '^d'"
alias tree="find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'"

# sudo apt *
alias apt-get="sudo apt-get"
alias apt-cache="sudo apt-cache"
function aptbig {
    dpkg-query -W --showformat='''${Installed-Size;10}\t${Package}\n''' | sort -k1,1n
}


#nicer output
alias path='echo -e ${PATH//:/\\n}'
alias mountt='mount | column -t'
alias nocomment='grep -Ev '\''^(#|$)'\'''
 
#alias grep='grep --color=auto'
#alias egrep='egrep --color=auto'
#alias fgrep='fgrep --color=auto'
 
#misc
alias alljobs='for user in $(cut -f1 -d: /etc/passwd); do crontab -u $user -l; done'
alias findit="find . -type f -name"
alias sourceme="source ~/dotfiles/kremtro.sh"
updateme() {
  (cd ~/dotfiles/ && git pull)
}

#networking 
alias port1='netstat -tulanp'
alias port3="watch -n 1 'netstat -Wnepo'"
#show external ip address
alias ipad="dig +short myip.opendns.com @resolver1.opendns.com" 
#alias port4='netstat -an | grep ESTABLISHED | awk '{print $5}' | awk -F: '{print (}' | sort | uniq -c | awk '{ printf("%s\t%s\t",[,() ; for (i = 0; i < (; i++) {printf("*")}; print "" }'))])'
 
## get top process eating memory
alias psmem='ps auxf | sort -nr -k 4'
alias psmem10='ps auxf | sort -nr -k 4 | head -10'
 
## get top process eating cpu ##
alias pscpu='ps auxf | sort -nr -k 3'
alias pscpu10='ps auxf | sort -nr -k 3 | head -10'
 
#diskspace
alias most='du -hsx * | sort -rh | head -10'
alias usage="du -h --max-depth=1 | sort -rh"
alias biggest="find . -printf '%s %p\n'| sort -nr | head -20"
sbs(){ du -b --max-depth 1 | sort -nr | perl -pe 's{([0-9]+)}{sprintf "%.1f%s", (>=2**30? ((/2**30, "G"): (>=2**20? ((/2**20, "M"): (>=2**10? ((/2**10, "K"): ((, "")}e';}
 
#export TERM=xterm-color
#export GREP_OPTIONS='--color=auto' GREP_COLOR='1;32'

#root stuff
alias reboot='sudo reboot'
alias updateapt='sudo apt-get -y upgrade'
alias apt='sudo apt -y '
alias apt-get='sudo apt-get -y'
alias svim='sudo vim'


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

