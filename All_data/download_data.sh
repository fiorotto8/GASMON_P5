#!/bin/bash
#YOUNNEED TO DECLARE gasmon_outside IN THE FILE .ssh/config
#READ README!!
rsync -azvP gasmon_outside:~/GasMon/Readout/logs/ logs

