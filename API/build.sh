#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt

# Installer LibreOffice sur Render
apt-get update && apt-get install -y libreoffice
