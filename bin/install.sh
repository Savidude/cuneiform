#!/usr/bin/env bash

echo "Installing NLTK dependencies"
pip3 install nltk
python3 -m nltk.downloader punkt

echo "Installing dateparser"
pip3 install dateparser

currentDir=$PWD
knowledgeDir=$currentDir/../resources/knowledge/db
touch $knowledgeDir/system.db
chmod 777 $knowledgeDir/system.db