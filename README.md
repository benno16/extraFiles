# FIREBrick 4
==========

Software for the open source hardware write-blocker/imager.

##### FIREBrick features:

* Mount of local and remote storage locations
* Image those storage location to another
* Preview storage location content 
* Web frontend
* Portable – fits on a small USB drive
* Free, open source
* Can be fully customized to the needs of specific departments

To build a FIREBrick you need:

* A small computer with IO interfaces for your evidence drives
* > 1 GB memory
* Debian based operating system with root access to build the OS

# Getting Started: 

* Install a plain Ubuntu LTS 
* Copy the install.sh file from the repository into /root/
* Make it executable > chmod +x /root/install.sh
* Run it /root/install.sh and accept the questions with 'y'
* We take care of the rest

# Create a bootable USB key:

Create a bootable USB key via syslinux
http://www.syslinux.org/wiki/index.php/The_Syslinux_Project

### From windows:

	>syslinux64.exe --mbr --active --directory / --install [name of drive such as "f:"]

Install syslinux to your key and create a simple config file like this one:

### SYSLINUX.CFG:
		
	default firebrick
	label firebrick
		linux /bzImage

Copy the bzImage (created in the build process above) file to your USB key.

Boot into the FIREBrick OS.
