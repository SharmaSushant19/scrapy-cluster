import os
import time
import subprocess
import zc.lockfile
import sys
while(1):
        try:
                print("trying to acquire a lock on the file")
                lock = zc.lockfile.LockFile("lock.txt")
                print("lock acquired")
                #t = os.system(temp)
                t = subprocess.call(['python','feedurl.py'])
                print(t)
        except zc.lockfile.LockError:
                print("not able to lock the file_going to sleep")
                time.sleep(300)
        #the script completed successfully
        else:
                lock.close()
