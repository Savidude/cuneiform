#!/usr/bin/env bash

echo "Installing NLTK dependencies"
pip3 install nltk

currentDir=$PWD
knowledgeDir=$currentDir/../resources/knowledge/db
touch $knowledgeDir/test.db