@echo off
echo "Removing old files...\n"
rd /s /q src
git clone https://github.com/Night-Traders-Dev/vOS.git
mv vOS/src src
rd /s /q vOS
echo "Fresh build installed in src/"
