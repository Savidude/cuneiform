#!/usr/bin/env bash

echo "Installing NLTK dependencies"
pip3 install nltk
python3 -m nltk.downloader punkt

echo "Installing dateparser"
pip3 install dateparser

echo "Installing requests"
pip3 install requests

currentDir=$PWD
knowledgeDir=$currentDir/../resources/knowledge/db
touch $knowledgeDir/system.db
chmod 777 $knowledgeDir/system.db

echo "Installing Node.js dependencies"
environmentDir=$currentDir/../environment
cd $environmentDir
sudo npm install

echo "Installing Bower dependencies"
libDir=$environmentDir/public
cd $libDir
sudo bower install
