# Activate OMZ
export ZSH="$HOME/.oh-my-zsh"
export EDITOR=nano  # not sorry

source ~/antigen.zsh

antigen use oh-my-zsh
antigen theme spaceship-prompt/spaceship-prompt

antigen bundle git
antigen bundle pip
antigen bundle darvid/zsh-poetry

antigen bundle command-not-found
antigen bundle z
antigen bundle colored-man-pages
antigen bundle zsh-users/zsh-syntax-highlighting
antigen bundle zsh-users/zsh-completions
antigen bundle zsh-users/zsh-autosuggestions

antigen apply

export FZF_DEFAULT_OPTS='--height 40% --layout=reverse --border'
source /usr/share/doc/fzf/examples/key-bindings.zsh
# This file is only present on Debian-Systems
if [ lsb_release -i | rev | cut -d ':' -f 1 | rev | tr -d '[:blank:]' = 'Debian' ]; then
    source /usr/share/doc/fzf/examples/completion.zsh
fi

# NPM Aliases
nvm() {
    unset -f nvm
    export NVM_DIR=~/.nvm
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    nvm "$@"
}
node() {
    unset -f node
    export NVM_DIR=~/.nvm
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    node "$@"
}
npm() {
    unset -f npm
    export NVM_DIR=~/.nvm
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    npm "$@"
}
ng() {
    unset -f ng
    export NVM_DIR=~/.nvm
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    ng "$@"
}

# Make it easier to run VSCode as root via the CLI
alias sudo='sudo '
alias code="code --user-data-dir=$HOME"

# Alias SSH with the Kitty command, to copy term-info to the other server
# This avoids formatting issues and other strange bugs
if [ $TERM = "xterm-kitty" ]; then
    function ssh() {
        # -T needs to be passed to SSH directly,
        # because it disallows Pseudo-Terminals,
        # which Kitty needs, to transfer its xterm options
        if [[ "$*" == *"-T"* ]]; then
            command ssh "$@"
        else
            kitty +kitten ssh "$@"
        fi
    }
fi

# Im lazy so here are some aliases for mpv
function mpv() {
    case $1 in
        music)
            if [ -z "${2}" ]; then
                echo "Missing File-Name or URL to Song."
                return 1
            fi
            command mpv --no-video $2
            ;;

        shuffle)
            if [ -z "${2}" ]; then
                echo "Missing File-Name or URL to Song."
                return 1
            fi
            command mpv --no-video --shuffle $2
            ;;

        playlist)
            case $2 in
                download-later)
                    params=("${@[@]:3}")
                    command mpv --no-video 'https://www.youtube.com/playlist?list=PLFd0FUPQ9InmkQTdk9rvYDuY5MCmCcOUh' "$params"
                    ;;

                liquid-dnb)
                    params=("${@[@]:3}")
                    command mpv --no-video 'https://www.youtube.com/playlist?list=PLFd0FUPQ9InlgiVDYU8KIaAgeijkF6X16' "$params"
                    ;;
                existence)
                    params=("${@[@]:3}")
                    command mpv --no-video 'https://www.youtube.com/playlist?list=PLFd0FUPQ9InmCWPJ_DHdrGwN8LCoPe1X4' "$params"
                    ;;
                *)
                    echo "Playlist not recognized."
                    return 1
                    ;;
            esac
            ;;

        *)
            command mpv "$@"
            ;;
    esac
}
