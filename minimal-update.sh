#! /bin/bash

MOUNT="/media/AXCEND"
LOG="/home/pi/update-log.txt"
ARCHIVE="axcend-update.zip"
WDIR="/tmp/update"

date > $LOG
ls $MOUNT >> $LOG

if [ -f $MOUNT/$ARCHIVE ]; then
    echo "Starting update" >> $LOG
    mkdir $WDIR
    cd $WDIR
    unzip $MOUNT/$ARCHIVE
    bash -x ./do-update >> $LOG
    echo "Finished update" >> $LOG
fi
