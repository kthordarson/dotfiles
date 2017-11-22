#!/bin/bash
# alias geymslan
# Version bersion 1 
# 24.06.2013
# 05.01.2014
# geyma í /etc/profile.d með ln -s /etc/profile.d/kremtro Dropbox/asdfgasdf
 
 
#basic
alias vi='vim'
alias ll="ls -lah"
#show only folders
alias lsd="ls -lF ${colorflag} | grep --color=never '^d'"

# sudo apt *
alias apt-get="sudo apt-get"
alias apt-cache="sudo apt-cache"
 
 
#nicer output
alias path='echo -e ${PATH//:/\\n}'
alias mountt='mount | column -t'
alias nocomment='grep -Ev '\''^(#|$)'\'''
 
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
 
#misc
alias alljobs='for user in $(cut -f1 -d: /etc/passwd); do crontab -u $user -l; done'
 
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
export GREP_OPTIONS='--color=auto' GREP_COLOR='1;32'

#root stuff
alias reboot='sudo reboot'
alias updateapt='sudo apt-get -y upgrade'
alias apt='sudo apt -y '
alias apt-get='sudo apt-get -y'

