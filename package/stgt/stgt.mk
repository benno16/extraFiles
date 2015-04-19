STGT_VERSION=stgt-master
STGT_SOURCE = stgt-master.tar.gz
STGT_SITE = http://www.go-unified.com/firebrick
STGT_AUTORECONF = NO
STGT_INSTALL_STAGING = NO
STGT_INSTALL_TARGET = YES
STGT_DEPENDENCIES = uclibc
$(eval $(autotools-package))
