#!/usr/bin/env bash

echo "Installing NLTK dependencies"
pip3 install nltk
python3 -m nltk.downloader punkt

currentDir=$PWD
knowledgeDir=$currentDir/../resources/knowledge/db
touch $knowledgeDir/system.db
chmod 777 $knowledgeDir/system.db