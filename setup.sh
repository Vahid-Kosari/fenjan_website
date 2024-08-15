#!/bin/bash

# Update package lists
sudo apt-get update

# Ensure that pip3 is installed
sudo apt-get install -y python3-pip

# Install system dependencies
sudo apt-get install -y libatk1.0-0 libatk-bridge2.0-0 libcups2 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2

# Install Python dependencies
pip3 install -r requirements.txt

