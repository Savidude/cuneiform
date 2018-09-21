#!/usr/bin/env bash

echo "Installing NLTK dependencies"
pip3 install nltk
python3 -m nltk.downloader punkt

echo "Installing dateparser"
pip3 install dateparser

echo "Installing requests"
pip3 install requests

echo "Installing word2number"
pip3 install word2number
pip3 install future

currentDir=$PWD
knowledgeDir=$currentDir/../resources/knowledge/db
touch $knowledgeDir/system.db
chmod 777 $knowledgeDir/system.db

echo "Installing Node.js dependencies"
environmentDir=$currentDir/../environment
cd $environmentDir
sudo npm install

echo "Installing Bower"
sudo npm install -g bower

echo "Installing Bower dependencies"
libDir=$environmentDir/public
cd $libDir
sudo bower install --allow-root
