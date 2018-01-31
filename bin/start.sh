#!/usr/bin/env bash

currentDir=$PWD
projectDir=$currentDir/..

responderDir=$projectDir/responder
classifierDir=$projectDir/classifier
managerDir=$projectDir/manager

echo "Starting processes"
echo "Starting responder process"
cd $responderDir
python3 start.py &
responderPID=$!
echo "Starting classifier process"
cd $classifierDir
python3 classifier.py &
classifierPID=$!
echo "Starting dialog manager process"
cd $managerDir
python3 dialog_manager.py
dialogManagerPID=$!

trap "
    kill $responderPID &
    kill $classifierPID &
    kill $dialogManagerPID;
    exit
" SIGINT