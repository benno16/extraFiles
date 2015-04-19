#!/bin/bash
echo " "
echo -e "\e[7m _____ _          _          _      _       ___  ____  "
echo "|  ___(_)_ __ ___| |__  _ __(_) ___| | __  / _ \/ ___| "
echo "| |_  | | :__/ _ \ ._ \| .__| |/ __| |/ / | | | \___ \ "
echo "|  _| | | | |  __/ |_) | |  | | (__|   <  | |_| |___) |"
echo "|_|   |_|_|  \___|_.__/|_|  |_|\___|_|\_\  \___/|____/ "
echo -e "                                                       \e[27m"
#


echo ""
echo "A set of changes will be applied to your system: "
echo " - installation of additional packages"
echo " - download of Buildroot and Firebrick"
echo " - compilation of Firebrick OS"
echo ""
echo "You need to be 'root'!"
echo "Installation is made in Folder /root/firebrick4/"
echo ""
echo "Only continue if you are sure you want to proceed. "
echo ""
read -n1 -r -p "Press 'y' to continue..." key

if [ "$key" = 'y' ]; then
	echo "Continuing" 
else
    exit 1
fi

# Make sure only root can run our script
if [[ $EUID -ne 0 ]]; then
   echo -e "\e[7mThis script must be run as root\e[27m" 1>&2
   exit 1
fi

# Make sure we are using Debian based host OS! 
FILE="/etc/debian_version"

if [ ! -f "$FILE" ]
then
    echo -e "\e[7mInvalid operating system! \e[27m"
	exit 1
fi

# Install pre-requirements
echo -e "\e[7mUpdating repositories\e[27m" 
apt-get update
echo -e "\e[7mInstalling additional packages required for firebrick build\e[27m" 
apt-get install -y bc python git build-essential unzip vim-nox libncurses5-dev wget

# Now lets get buildroot and our sources 
echo -e "\e[7mDownloading Buildroot\e[27m" 
mkdir -p /root/firebrick4/
cd /root/firebrick4/
wget http://buildroot.uclibc.org/downloads/buildroot-2015.02.tar.gz
tar -xzf buildroot-*
rm buildroot-*.tar.gz*
mv buildroot-* buildroot


echo -e "\e[7mDownloading Firebrick OS\e[27m"
git clone https://github.com/benno16/extraFiles.git
#wget http://www.go-unified.com/firebrick/firebrick.zip
#unzip -oqq firebrick.zip
#rm firebrick*.zip*

echo -e "\e[7mAdjust POSIX in Firebrick OS\e[27m"
chmod +x /root/firebrick4/extraFiles/*.sh
chmod +x /root/firebrick4/extraFiles/init.d/*
chmod +x /root/firebrick4/extraFiles/FlaskApp/firebrickd

# now we start building the shit! 
MEMORYSIZE=$(cat /proc/meminfo | grep MemTotal | awk '{ print $2 }')

if $MEMORYSIZE < 102400 
then
	echo -e "\e[7mNot enough memory! Installation might fail\e[27m"
	exit 1
fi

echo -e "\e[7mand now lets build\e[27m"

read -n1 -r -p "Press 'y' to start the build process..." key

if [ "$key" = 'y' ]; then
	/root/firebrick4/extraFiles/start.sh
else
	echo ""
    exit 1
fi
