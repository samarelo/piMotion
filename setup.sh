#! /bin/bash

echo ~~1/10 Install RPI-UPDATE
apt-get install rpi-update

echo ~~2/10 Run RPI-UPDATE
rpi-update

echo ~~3/10 Update all OS packages
apt-get update

echo ~~4/10 Upgrade all OS packages
apt-get upgrade

echo ~~5/10 Install Motion
apt-get install motion

echo ~~6/10 install Python-pip
apt-get install python-pip

echo ~~7/10 install PIP Gdata module
pip install gdata

echo ~~8/10 create folders
mkdir /media/pimotion
mkdir /media/pimotion/snapshots
mkdir /media/pimotion/motion
mkdir /media/pimotion/videos
mkdir /media/pimotion/timelapse

echo ~~9/11 make motion owner of folders
chown motion:motion -R /media/pimotion

echo ~~10/	move notify.py to /etc/motion
cp notify.py /etc/motion


echo ~~11/11 Last Steps
echo a. Update notify.cfg to enter personal info 
echo b. cp notify.cfg to /etc/motion
echo c. cp motion.conf to /etc/motion
echo d. Set permissions for /etc/motion/motion.conf   chmod 640 motion.conf
echo e. If you want motion to run as daemon then nano etc/default/motion and change start_motion_daemon=yes
echo f. Restart pi reboot
