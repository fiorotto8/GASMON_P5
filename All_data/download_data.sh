#!/bin/bash
#error like:
#mv: cannot stat 'logs': No such file or directory
#is normal if it is the first time you run this
#######################################################
#TO BE RUNNED IN LXPLUS
#rsync -azvP gem3@cms-cauriol.cern.ch:~/GasMon/Readout/logs/ logs
#OLD VERSION
#rm -rf old
#mv logs old
#scp -r gem3@cms-cauriol.cern.ch:~/GasMon/Readout/logs logs
rsync -av -e "ssh -A dfiorina@lxplus.cern.ch ssh" gem3@cms-cauriol.cern.ch:~/GasMon/Readout/logs/ logs
