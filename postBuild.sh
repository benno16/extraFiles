#!/bin/sh
# Firebrick build postbuild script
# last edit 18/04/2015 - Benedikt Riedel

#Add tty0 to secure shell access
if grep -F 'tty0' output/target/etc/securetty ; then
	echo 'tty0 line present not adding...'
else
	echo 'tty0 line NOT present adding...'
	echo 'tty0' >> output/target/etc/securetty 
fi

#Add fstab entries
if grep -F 'configfs' output/target/etc/fstab ; then
	echo 'configfs line present for configfs not adding...'
else
	echo 'configfs	/sys/kernel/config	configfs	defaults	0	0' >> output/target/etc/fstab 
fi

#Add profile tweaks
if test -f output/target/bin/loginFirebrick.sh ; then
	echo 'autologin present not adding...'
else
	echo 'autologin not present!'
	echo "#!/bin/sh" >> output/target/bin/loginFirebrick.sh
	echo "exec /bin/login -f root" >> output/target/bin/loginFirebrick.sh
fi

chmod +x output/target/bin/loginFirebrick.sh

#Update inittab (not doing it now)
/bin/sed -i -e '/# GENERIC_SERIAL$/s~^.*#~tty0::respawn:/sbin/getty -l /bin/loginFirebrick.sh -n -L tty0 115200 vt100 # GENERIC_SERIAL#~' output/target/etc/inittab

#Copy init scripts
cp -f ../extraFiles/init.d/* output/target/etc/init.d/
chmod +x output/target/etc/init.d/*

#Copy FlaskApp
if ! test -d output/target/FlaskApp ; then mkdir output/target/FlaskApp ; fi
cp -fr ../extraFiles/FlaskApp/* output/target/FlaskApp

cp -f ../extraFiles/.profile output/target/root/.profile

#DHCP config
cp -f ../extraFiles/interfaces output/target/etc/network
cp -f ../extraFiles/udhcpd.conf output/target/etc

#Nameserver config
echo "nameserver 8.8.8.8" > output/target/etc/resolv.conf

#cp -f ../extraFiles/httpd.conf output/target/etc
#rm -rf output/target/var/lib/dhcp
#mkdir -p output/target/var/lib/dhcp
#if ! test -f output/target/var/lib/dhcp/dhcpd.leases; then  touch output/target/var/lib/dhcp/dhcpd.leases; fi
#if ! test -f output/target/etc/dhcpd.conf; then  touch output/target/etc/dhcpd.conf; fi


#delete pci info file junk
if test -f output/target/usr/share/pci.ids; then rm -f output/target/usr/share/pci.ids ; fi