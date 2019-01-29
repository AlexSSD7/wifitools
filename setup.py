import shutil
import os

print("Copying files...")
shutil.copyfile("wifitools.py", "/bin/wifitools")
print("Installing requirements with pip...")
os.system("pip3 install -r requirements.txt")
print("Finishing...")
os.system("chmod +x /bin/wifitools")
print("Done.")
