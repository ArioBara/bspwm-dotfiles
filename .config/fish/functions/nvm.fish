function nvm --description 'NVM wrapper for Fish shell'
    set -l nvm_cmd (string escape -- $argv)
    bash -c "source ~/.nvm/nvm.sh && nvm $nvm_cmd"
end
