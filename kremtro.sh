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

	filename=$(ls "$(which "$1")")

	if [ -h "$filename" ]; then
		echo "$filename is a symlink to $(readlink -f "$filename")"
		filename=$(readlink -f "$filename")
	fi

	filetype=$(file "$filename")
	echo "$filename - $filetype"
}
function llwf() {
	# file $(llw $1 | awk '{print $9}')
	file "$(llw "$1" | awk '{print $9}')"
}
#show only folders
# alias lsd="ls -lF ${colorflag} | grep '^d'"
#alias tree="find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'"
#alias newtree="tree $1 --noreport  -tiafFD | tail"
function newtree() { tree "$1" --noreport -tiaFD | tail; }
function aptbig {
	dpkg-query -W --showformat='''${Installed-Size;10}\t${Package}\n''' | sort -k1,1n
}
# shellcheck disable=SC2154
alias apt-biggest="dpkg-query -Wf '\${Installed-Size}\t\${Package}\n' | sort -n"

#nicer output
alias path='echo -e ${PATH//:/\\n}'
alias mountt='mount | column -t'
alias nocomment='grep -Ev '\''^(#|$)'\'''


#misc
#alias alljobs='for user in $(cut -f1 -d: /etc/passwd); do sudo crontab -u $user -l; done'
function alljobs() {
	# shellcheck disable=SC2013
	for user in $(cut -f1 -d: /etc/passwd); do sudo crontab -u "$user" -l; done
}
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
# alias arpdump="arp -avn  | grep -vE 'incomplete|Entries' | awk '{print $4}'"
function arpdump() {
	arp -avn | grep -vE 'incomplete|Entries' | awk '{print $4}'
}
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
	du -hsx "$1"* | sort -rh | head -20
}

alias usage="du -h --max-depth=1 | sort -rh"
alias usage10="du -h --max-depth=1 | sort -rh| head -10"
alias biggest="find . -name .git -prune -o -name '*' -printf '%s %p\n'| sort -nr | head -20"
# alias biggest="find . -path ./.git -prune -o -printf '%s %p\n'| sort -nr | head -20"
# find . -path ./misc -prune -o -name '*.txt' -print
# find -name "*.js" -not -path "./directory/*"
#alias foldersize='du -sch \$1'

function foldersize() {
	du -sch "$1"
}

sbs() { du "$1" -b --max-depth 1 | sort -nr |perl -pe 's{([0-9]+)}{sprintf "%.1f%s", $1>=2**30 ? ($1/2**30, "G") : $1>=2**20 ? ($1/2**20, "M") : $1>=2**10 ? ($1/2**10, "K") : ($1, "")}e'; }

# find stuff
function newest() { find "$1" -type f -mtime -2 -printf '%TY-%Td-%Tm %.8TT %p\n' | sort | tail -n 30; }

# alias newest="find  -type f -mtime -2 -printf '%TY-%Td-%Tm %.8TT %p\n' | sort | tail -n 30"

#root stuff
# alias sudo='sudo '
alias reboot='sudo reboot'
alias svim='sudo vim'

# cat with colors
alias catcolor='pygmentize -O style=monokai -f console256 -g'

# history stuff
export HISTCONTROL="erasedups:ignoreboth"     # no duplicate entries
export HISTSIZE=-1                            # big big history (default is 500)
export HISTFILESIZE=$HISTSIZE                 # big big history
export HISTIGNORE="ls:ll:history:df"          # ignores
type shopt &>/dev/null && shopt -s histappend # append to history, don't overwrite it
export PROMPT_COMMAND="history -a; history -n"

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
function lsofpid() {
	if [ $# -ne 2 ]; then
		echo "Looking for proc $1"
		for pid in $(ps uxa | grep -v -E "grep|tail" | grep $1 | awk -F' ' '{print $2}')
		do
			echo "checking pid: $pid"
			sudo lsof -n -p $pid
		done;
	else
		echo "wrong args"
	fi
}
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

#tmux stuff
alias tml='tmux list-sessions'
alias tmk='tmux kill-session -t'

# source ~/dotfiles/ffm.sh

# find zombie processes
alias zombies='ps axo stat,ppid,pid,comm | grep -w defunct'

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

same_size_dirs() {
	# Check if path argument is provided
	if [ -z "$1" ]; then
		echo "Error: Please provide a path"
		return 1
	fi

	# Check if path exists and is a directory
	if [ ! -d "$1" ]; then
		echo "Error: '$1' is not a valid directory"
		return 1
	fi

	# Find directories and their sizes, sort by size, and group
	find "$1" -maxdepth 1 -type d -exec du -s {} \; |
	sort -n |
	awk '{
        size=$1;
        $1="";
        sub(/^ /, "");
        dirs[size] = (dirs[size] ? dirs[size] ", " : "") $0
    }
    END {
        for (size in dirs) {
            if (split(dirs[size], arr, ", ") > 1) {
                print "Size: " size "KB"
                print dirs[size]
                print ""
            }
        }
    }'
}

# find_duplicate_files /path/to/directory 10240  # Find duplicates larger than 10KB
find_duplicate_files() {
	# Check if path argument is provided
	if [ -z "$1" ]; then
		echo "Error: Please provide a path"
		return 1
	fi

	# Check if path exists and is a directory
	if [ ! -d "$1" ]; then
		echo "Error: '$1' is not a valid directory"
		return 1
	fi

	# Default minimum size (in bytes) if not specified (e.g., 1024 bytes = 1KB)
	local min_size=${2:-1024}

	# Temporary file for storing file info
	local temp_file
	if ! temp_file=$(mktemp); then
		echo "Error: Failed to create temporary file"
		return 1
	fi

	# Find files, calculate size and MD5, and filter by size
	find "$1" -type f -size +"${min_size}"c -exec ls -l {} \; -exec md5sum {} \; |
	awk '{
        if (NR % 2 == 1) {
            size=$5;
            file=$9
        } else {
            md5=$1;
            print size ":" md5 ":" file
        }
    }' |
	sort -t':' -k1,1n -k2,2 |
	awk -F':' '
    {
        key=$1":"$2
        if (key in files) {
            files[key] = files[key] "\n" $3
            count[key]++
        } else {
            files[key] = $3
            count[key] = 1
        }
    }
    END {
        for (key in files) {
            if (count[key] > 1) {
                split(key, arr, ":")
                print "Size: " arr[1] " bytes, MD5: " arr[2]
                print files[key]
                print ""
            }
        }
    }' > "$temp_file"

	# Display results if duplicates found
	if [ -s "$temp_file" ]; then
		cat "$temp_file"
	else
		echo "No duplicate files found over ${min_size} bytes."
	fi

	# Clean up
	rm -f "$temp_file"
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
	# Create a temporary file to store find output
	tmpfile=$(mktemp)
	# Run find and store output, handling spaces correctly
	find "$1" "$2" -type d -not -path '*/\.*' -exec du -sb -- "{}" \; > "$tmpfile"
	while IFS= read -r line; do
		# Extract size and path
		size=$(echo "$line" | awk '{print $1}')
		path=$(echo "$line" | awk '{$1=""; sub(/^ /, ""); print}' | sed 's/"/\\"/g')
		# Compute file count with proper quoting
		file_count=$(find "$path" -type f -not -path '*/\.*' -exec ls -l "{}" \; | wc -l)
		echo "$size,$file_count,$path"
	done < "$tmpfile" | \
	awk -F, 'NF == 3 && $1 ~ /^[0-9]+$/ && $2 ~ /^[0-9]+$/ {
        key = $1 "," $2
        a[key] = key in a ? a[key] "\n" $3 : $3
        b[key]++
    }
    END {
        for (x in b)
            if (b[x] > 1) {
                split(x, arr, ",")
                printf "Duplicate Directories (Size: %s Bytes, File Count: %s):\n%s\n\n", arr[1], arr[2], a[x]
            }
    }' | grep -v '^$'
	# Clean up temporary file
	rm -f "$tmpfile"
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

# Function to get Git remote(s)
git_remote_prompt() {
	if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		local remotes
		remotes=$(git remote | tr '\n' ',' | sed 's/,$//')
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
		local origin_url
		origin_url=$(git remote get-url origin 2>/dev/null)
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
		local repo_name
		repo_name=$(basename "$(git rev-parse --show-toplevel)")
		echo "[$repo_name]"
	else
		echo ""
	fi
}
alias sourceme="source ~/dotfiles/kremtro.sh"
