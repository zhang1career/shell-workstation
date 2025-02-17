# list disk block
lsblk

# determine whether there is a file system on the volume
sudo file -s /dev/xvdb

# get information about all ot the devices attached to the instance
sudo lsblk -f

# (Conditional) format if there is not filesystem
sudo mkfs -t xfs /dev/xvdb


# (Conditional) if /etc/fstab has been recorded the mount point before, clear it
sudo vim /etc/fstab
--- UUID=xxxx /db1 xfs xxxx,xxxx, x, x ---
sudo systemctl daemon-reload

# create a mount point
sudo mkdir /db1

# mount the volume
sudo mount /dev/xvdb /db1

# setup auto-mount
sudo vim /etc/fstab
+++ UUID=xxxx /db1 xfs xxxx,xxxx, x, x +++

# verify, enter following command without error returned
sudo umount /db1
sudo mount -a


####################
# trouble-shooting
####################
log dir: /var/log/messages
