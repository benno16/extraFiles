import os
import os.path
from subprocess import call
import platform

def mountShare(m):
    if platform.system() == 'Linux':
        print("Mounting : " + m['Name'] + "\n")
        pathToMountTo= getMountPoint(m['ID'])
        share = m['Path']
        usernamePart = "username=\"{0}\",".format(m['UserName'])
        argument = "-t cifs \"{0}\" \"{1}\" -o {2}password=\"{3}\" ".format(share,pathToMountTo,usernamePart,m['Password'])

        isMounted = call("mount | grep \""+ share + "\" > /dev/null",shell=True)

        if isMounted != 0:
            exitCode = call("mount "+ argument,shell=True)

            if exitCode == 0:
                m['MountedTo'] = pathToMountTo
                print("Mount completed")
                return True
            else:
                m['LastError'] = "Failed to mount"
                print("Failed to mount")
        else:
            print("Already mounted")
            m['MountedTo'] = pathToMountTo
            return True
    else:
        m['MountedTo'] = 'None'
        m['LastError'] = "Can't use mount on " + platform.system()
        print("Can't use mount on " + platform.system() + "\n")
    return False

def getMountPoint(id):
    MOUNT_DEVICE_BASE_PATH = "/mnt/firebrick/devices";
    combinedPath = os.path.join(MOUNT_DEVICE_BASE_PATH,id)
    if not os.path.exists(combinedPath):
        os.makedirs(combinedPath)
    return combinedPath

def unmountShare(m):
    if platform.system() == 'Linux':
        print("Unmounting " + m['Name'])
        share = m['Path']
        call("umount \"{0}\"".format(share),shell=True)
    else:
        print("Can't use umount on " + platform.system() + "\n")