# Starts the compilation of the ROM
# Use with care
# Modify the bottom make command to ensure the correct build process
#
# Last modified: 18/04/2015 - Benedikt Riedel

cd /root/firebrick4
cp extraFiles/configs/buildroot.config buildroot/.config
cp extraFiles/package/dcfldd buildroot/package -r
cp extraFiles/package/stgt buildroot/package -r
cp extraFiles/package/python-flask-jsonrpc buildroot/package -r
cp extraFiles/package/python-cherrypy buildroot/package -r
cp extraFiles/package/iscsitarget buildroot/package -r
cp extraFiles/package/python-jsonpickle buildroot/package -r


#Add dcfldd entries
if grep -F 'dcfldd' buildroot/package/Config.in ; then
	echo 'dcfldd line present in Config.in not adding...'
else
	sed -i '/^menu "Target packages"/a source "package/dcfldd/Config.in"' buildroot/package/Config.in
fi

#Add stgt entries
if grep -F 'stgt' buildroot/package/Config.in ; then
	echo 'stgt line present in Config.in not adding...'
else
	sed -i '/^menu "Target packages"/a source "package/stgt/Config.in"' buildroot/package/Config.in
fi

#Add flask-jsonrpc entries
if grep -F 'python-flask-jsonrpc' buildroot/package/Config.in ; then
	echo 'python-flask-jsonrpc line present in Config.in not adding...'
else
	sed -i '/^menu "Target packages"/a source "package/python-flask-jsonrpc/Config.in"' buildroot/package/Config.in
fi

#Add cherrypy entries
if grep -F 'python-cherrypy' buildroot/package/Config.in ; then
	echo 'python-cherrypy line present in Config.in not adding...'
else
	sed -i '/^menu "Target packages"/a source "package/python-cherrypy/Config.in"' buildroot/package/Config.in
fi

#Add jsonpickle entries
if grep -F 'python-jsonpickle' buildroot/package/Config.in ; then
	echo 'python-jsonpickle line present in Config.in not adding...'
else
	sed -i '/^menu "Target packages"/a source "package/python-jsonpickle/Config.in"' buildroot/package/Config.in
fi

#Add iscsitarget entries - not working with kernel 3.18
if grep -F 'iscsitarget' buildroot/package/Config.in ; then
	echo 'iscsitarget line present in Config.in not adding...'
else
	sed -i '/^menu "Target packages"/a source "package/iscsitarget/Config.in"' buildroot/package/Config.in
fi

#Add quick rebuild to buildroot Makefile
if grep -F 'quickrebuild' buildroot/Makefile ; then
	echo 'quickrebuild already in Buildroot Makefile'
else
	echo 'Added quickrebuild to Buildroot Makefile'
	line='rm -rf $(TARGET_DIR) $(STAGING_DIR) $(STAMP_DIR) $(BUILD_DIR)/.root $(BUILD_DIR)/*/.stamp_target_installed $(BUILD_DIR)/*/.stamp_staging_installed $(BUILD_DIR)/linux-*/.stamp_installed $(BUILD_DIR)/*/.built'
	echo -e "\nquickrebuild:\n\t$line\n" >> buildroot/Makefile
fi

cd buildroot

# normal build! 
make

# clean repo! 
#make clean

#make V=s 2>&1 | tee build.log | grep -i error
