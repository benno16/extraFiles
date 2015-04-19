#
# iscsitarget
#
ISCSITARGET_VERSION = r503
ISCSITARGET_SOURCE = iscsitarget-1.4.20.2.tar.gz
ISCSITARGET_SITE = https://github.com/benno16/extraFiles/blob/master/package/sources

ifeq ($(BR2_PACKAGE_ISCSITARGET_KMOD),y)
ISCSITARGET_DEPENDENCIES = linux
endif

define ISCSITARGET_BUILD_CMDS
	$(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" CROSS_PREFIX=$(TARGET_CROSS) \
	ARCH=$(BR2_ARCH) -C $(@D) \
	$(if $(BR2_PACKAGE_ISCSITARGET_KMOD),KSRC="$(LINUX_DIR)" kernel) \
	usr
endef

define ISCSITARGET_INSTALL_TARGET_CMDS
	$(MAKE) DESTDIR=$(TARGET_DIR) CC="$(TARGET_CC)" \
	ARCH=$(BR2_ARCH) -C $(@D) \
	$(if $(BR2_PACKAGE_ISCSITARGET_KMOD), \
		KSRC="$(LINUX_DIR)" \
		CROSS_PREFIX=$(TARGET_CROSS) \
		DEPMOD="$(HOST_DIR)/usr/sbin/depmod" \
		install-kernel depmod) \
	install-usr
	$(INSTALL) -vD -m 0640 $(@D)/etc/ietd.conf \
		$(TARGET_DIR)/etc/iet/ietd.conf
	$(INSTALL) -vD -m 0644 $(@D)/etc/initiators.allow \
		$(TARGET_DIR)/etc/iet/initiators.allow
	$(INSTALL) -vD -m 0644 $(@D)/etc/targets.allow \
		$(TARGET_DIR)/etc/iet/targets.allow
	$(INSTALL) -vD -m 755 $(@D)/etc/initd/initd \
		$(TARGET_DIR)/etc/init.d/S60iscsi-target
endef

$(eval $(generic-package))
