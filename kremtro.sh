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
export PATH=$PATH:~/dotfiles/scripts
export PATH=$PATH:~/.local/bin
export PATH=$PATH:/usr/local/bin
export PATH=$PATH:~/bin/
export PATH=$PATH:~/.cargo/bin/
export PYGAME_HIDE_SUPPORT_PROMPT=true
# rootinit
alias sudo='sudo '
alias mkdir='mkdir -pv'

alias john="~/development2/john/run/john"

#basic
alias kremer='vi /home/kth/dotfiles/kremtro.sh && source ~/.bashrc'
alias rassgat='echo rassgat'
alias vi='vim'

if alias ll &>/dev/null; then
    unalias ll
fi
#else
#    echo "ll ok";
#fi

#unalias ll
alias ll="ls -la --color=auto"
#alias ll="ls -lah"
alias llr="ll -tr"
function llw() {

    filename=$(ls "$(which $1)")

    if [ -h "$filename" ]; then
        echo "$filename is a symlink to $(readlink -f "$filename")"
        filename=$(readlink -f "$filename")
    fi

    filetype=$(file $filename)
    echo "$filename - $filetype"
}
function llwf() {
    # file $(llw $1 | awk '{print $9}')
    file "$(llw $1 | awk '{print $9}')"
}
#show only folders
# alias lsd="ls -lF ${colorflag} | grep '^d'"
#alias tree="find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'"
#alias newtree="tree $1 --noreport  -tiafFD | tail"
function newtree() { tree "$1" --noreport -tiaFD | tail; }
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
#alias alljobs='for user in $(cut -f1 -d: /etc/passwd); do sudo crontab -u $user -l; done'
function alljobs() {
    for user in $(cut -f1 -d: /etc/passwd); do sudo crontab -u $user -l; done
}
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
# alias ipad="dig +short myip.opendns.com @resolver1.opendns.com"
alias ipad="curl https://ipinfo.io/ip"
#alias port4='netstat -an | grep ESTABLISHED | awk '{print $5}' | awk -F: '{print (}' | sort | uniq -c | awk '{ printf("%s\t%s\t",[,() ; for (i = 0; i < (; i++) {printf("*")}; print "" }'))])'
alias arpdump="arp -avn  | grep -vE 'incomplete|Entries' | awk '{print $4}'"

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
# alias most='du -hsx * | sort -rh | head -10'
function most() {
    du -hsx $1* | sort -rh | head -20
}

alias usage="du -h --max-depth=1 | sort -rh"
alias usage10="du -h --max-depth=1 | sort -rh| head -10"
alias biggest="find . -name .git -prune -o -name '*' -printf '%s %p\n'| sort -nr | head -20"
# alias biggest="find . -path ./.git -prune -o -printf '%s %p\n'| sort -nr | head -20"
# find . -path ./misc -prune -o -name '*.txt' -print
# find -name "*.js" -not -path "./directory/*"
alias foldersize="du -sch $1"

sbs() { du $1 -b --max-depth 1 | sort -nr |perl -pe 's{([0-9]+)}{sprintf "%.1f%s", $1>=2**30 ? ($1/2**30, "G") : $1>=2**20 ? ($1/2**20, "M") : $1>=2**10 ? ($1/2**10, "K") : ($1, "")}e'; }

# perl -pe 's{([0-9]+)}{sprintf "%.1f%s", (>=2**30? ((/2**30, "G"): (>=2**20? ((/2**20, "M"): (>=2**10? ((/2**10, "K"): ((, "")}e';
# find stuff
# alias newest="find . -type f -printf '%TY-%Td-%Tm %.8TT %p\n' | sort -rn | head -n 10"
function newest() { find "$1" -type f -mtime -2 -printf '%TY-%Td-%Tm %.8TT %p\n' | sort | tail -n 30; }

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
export HISTCONTROL="erasedups:ignoreboth"     # no duplicate entries
export HISTSIZE=-1                            # big big history (default is 500)
export HISTFILESIZE=$HISTSIZE                 # big big history
export HISTIGNORE="ls:ll:history:df"          # ignores
type shopt &>/dev/null && shopt -s histappend # append to history, don't overwrite it
# PROMPT_COMMAND="history -a; history -n"
# export PROMPT_COMMAND="history -a; $PROMPT_COMMAND"
# export PROMPT_COMMAND='history -a;history -c;history -r'
# export PROMPT_COMMAND='history -a;history -r;history -n'
##
## better `cd`'ing
##

# Case-insensitive globbing (used in pathname expansion)
shopt -s nocaseglob

# Correct spelling errors in arguments supplied to cd
shopt -s cdspell

# Autocorrect on directory names to match a glob.
# shopt -s dirspell 2> /dev/null

# Turn on recursive globbing (enables ** to recurse all directories)
# shopt -s globstar 2> /dev/null

function findit() {
    if [ $# -gt 0 ]; then
        echo "Searching in $1 for string $2"
        find "$1" -type f -exec grep -iHno "$2" {} +
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

# dns dig
# Run `dig` and display the most useful info
digga() {
    dig +nocmd "$1" any +multiline +noall +answer
}

# man
# Get colors in manual pages
man() {
    env \
        LESS_TERMCAP_mb="$(printf '\e[1;31m')" \
        LESS_TERMCAP_md="$(printf '\e[1;31m')" \
        LESS_TERMCAP_me="$(printf '\e[0m')" \
        LESS_TERMCAP_se="$(printf '\e[0m')" \
        LESS_TERMCAP_so="$(printf '\e[1;44;33m')" \
        LESS_TERMCAP_ue="$(printf '\e[0m')" \
        LESS_TERMCAP_us="$(printf '\e[1;32m')" \
        man "$@"
}

function findupesdirs() {
    if [ $# -ne 2 ]; then
        echo "Error: Please provide exactly two paths"
        return 1
    fi
    if [ ! -d "$1" ] || [ ! -d "$2" ]; then
        echo "Error: Both arguments must be valid directories"
        return 1
    fi
    awk '{
        key = $1 "," $2  # Combine size and file count as key
        a[key] = key in a ? a[key] RS $3 : $3
        b[key]++
    }
    END {
        for(x in b)
            if(b[x] > 1) {
                split(x, arr, ",")
                printf "Duplicate Directories (Size: %s Bytes, File Count: %s):\n%s\n", arr[1], arr[2], a[x]
            }
    }' <(find "$1" "$2" -type d -exec du -sb {} \; -exec sh -c 'find "{}" -type f | wc -l' \; -exec echo {} \; | awk '{print $1 "," $2 "," $3}')
}

function findupesdirs_v1() {
    if [ -z "$1" ]; then
        echo "Error: Please provide a path"
        return 1
    fi
    awk '{
        key = $1 "," $2  # Combine size and file count as key
        a[key] = key in a ? a[key] RS $3 : $3
        b[key]++
    }
    END {
        for(x in b)
            if(b[x] > 1) {
                split(x, arr, ",")
                printf "Duplicate Directories (Size: %s Bytes, File Count: %s):\n%s\n", arr[1], arr[2], a[x]
            }
    }' <(find "$1" -type d -exec du -sb {} \; -exec sh -c 'find "{}" -type f | wc -l' \; -exec echo {} \; | awk '{print $1 "," $2 "," $3}')
}

function findupefiles() {
    awk -F'/' '{
  f = $NF
  a[f] = f in a? a[f] RS $0 : $0
  b[f]++ }
  END{for(x in b)
        if(b[x]>1)
          printf "Duplicate Filename: %s\n%s\n",x,a[x] }' <(find . -type f)

}

function findupesmd5() {
    awk '{
  md5=$1
  a[md5]=md5 in a ? a[md5] RS $2 : $2
  b[md5]++ }
  END{for(x in b)
        if(b[x]>1)
          printf "Duplicate Files (MD5:%s):\n%s\n",x,a[x] }' <(find . -type f -exec md5sum {} +)
}

function findupessize() {
    awk '{
  size = $1
  a[size]=size in a ? a[size] RS $2 : $2
  b[size]++ }
  END{for(x in b)
        if(b[x]>1)
          printf "Duplicate Files By Size: %d Bytes\n%s\n",x,a[x] }' <(find . -type f -exec du -b {} +)

}

alias dupeguru='/usr/bin/python ~/development2/dupeguru/run.py'
alias ogr='open $(git remote get-url origin)'

# gitfoo

# open remote url
alias ogr='open $(git remote get-url origin)'
# print remote url
alias pgr='echo $(git remote get-url origin)'

function setpowermode() {
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
}

alias pips='pip_search -s released '
alias pips='python3  ~/development/pip_search/pip_search/__main__.py  -s released '
# export LS_COLORS="di=36:ln=35:so=32:pi=33:ex=31:bd=34;46:cd=34;43:su=30;41:sg=30;46:tw=36;42:ow=36;43:fi=32"
# export LS_COLORS="di=36:ln=35:so=32:pi=33:ex=31;47:bd=34;46:cd=34;47:su=30;47:sg=30;47:tw=30;47:ow=36;47"
# LS_COLORS=rs=0:di=01;34:ln=01;36:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:mi=00:su=37;41:sg=30;43:ca=00:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arc=01;31:*.arj=01;31:*.taz=01;31:*.lha=01;31:*.lz4=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.tzo=01;31:*.t7z=01;31:*.zip=01;31:*.z=01;31:*.dz=01;31:*.gz=01;31:*.lrz=01;31:*.lz=01;31:*.lzo=01;31:*.xz=01;31:*.zst=01;31:*.tzst=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.alz=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.cab=01;31:*.wim=01;31:*.swm=01;31:*.dwm=01;31:*.esd=01;31:*.avif=01;35:*.jpg=01;35:*.jpeg=01;35:*.mjpg=01;35:*.mjpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.webp=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.m4a=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.oga=00;36:*.opus=00;36:*.spx=00;36:*.xspf=00;36:*~=00;90:*#=00;90:*.bak=00;90:*.crdownload=00;90:*.dpkg-dist=00;90:*.dpkg-new=00;90:*.dpkg-old=00;90:*.dpkg-tmp=00;90:*.old=00;90:*.orig=00;90:*.part=00;90:*.rej=00;90:*.rpmnew=00;90:*.rpmorig=00;90:*.rpmsave=00;90:*.swp=00;90:*.tmp=00;90:*.ucf-dist=00;90:*.ucf-new=00;90:*.ucf-old=00;90:

# Function to get Git remote(s)
git_remote_prompt() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local remotes=$(git remote | tr '\n' ',' | sed 's/,$//')
        if [ -n "$remotes" ]; then
            echo "$remotes"
        else
            echo "[no remotes]"
        fi
    else
        echo ""
    fi
}

git_remote_prompt_url() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local origin_url=$(git remote get-url origin 2>/dev/null)
        if [ -n "$origin_url" ]; then
            echo "[origin:$origin_url]"
        else
            echo "[no origin]"
        fi
    else
        echo ""
    fi
}
# Function to get Git repository name
git_repo_name() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        # Get the repository's root directory name
        local repo_name=$(basename "$(git rev-parse --show-toplevel)")
        echo "[$repo_name]"
    else
        echo ""
    fi
}

function get_github_repo_size() {
    if [[ $1 == *"github.com"* ]]; then
        # Extract the repository name from the URL
        repo_name=$(echo "$1" | sed 's|https://github.com/||')
        #| sed -E 's|.*github\.com[:/]|github.com/|; s|\.git$||')
    else
        # If not a GitHub URL, use the provided argument as is
        repo_name=$1
    fi
    # curl -s https://api.github.com/repos/torvalds/linux | jq '.size' | numfmt --to=iec --from-unit=1024
    reposize=$(curl -s https://api.github.com/repos/$repo_name | jq '.size' | numfmt --to=iec --from-unit=1024)
    # reposize=$(curl -s $1 | jq '.size' | numfmt --to=iec --from-unit=1024)
    echo "Repo $repo_name size: $reposize"
}

# Default PS1 (without repo name)
# DEFAULT_PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\] \$ '

# PS1 with repo name when in a Git repository
# PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\] $(git_remote_prompt) \[\033[01;33m\]$(git_repo_name)\[\033[00m\] \$ '
# PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\W\[\033[00m\]$(git_remote_prompt)\033[01;33m\]$(git_repo_name)\[\033[00m \$ '
# PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\W\[\033[00m\]\033[01;33m\]$(git_remote_prompt_url)\[\033[00m \$ '
