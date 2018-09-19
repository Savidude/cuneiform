#!/usr/bin/env bash

currentDir=$PWD
projectDir=$currentDir/..

responderDir=$projectDir/responder
classifierDir=$projectDir/classifier
managerDir=$projectDir/manager
environmentDir=$projectDir/environment

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
python3 dialog_manager.py &
dialogManagerPID=$!
cd $environmentDir
npm start

trap "
    kill $responderPID &
    kill $classifierPID &
    kill $dialogManagerPID;
    exit
" SIGINT