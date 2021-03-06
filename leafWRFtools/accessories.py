import subprocess
import os 

'''
These are helper, or 'accessory' functions to be used by leafwrftools
'''
def system_cmd(cmd):
    # issue system commands 
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    out,err = proc.communicate()
    return out.split(),err

def GenericWrite(readpath,replacedata,writepath):
    # path to file to read 
    # data dictionary to put into file
    # path to the write out file 

    with open(readpath, 'r') as file:
        filedata = file.read()
        #  
        # loop thru dictionary and replace items
    for item in replacedata:
        filedata = filedata.replace(item, str(replacedata[item])) # make sure it's a string 

    # Write the file out again
    with open(writepath, 'w') as file:
        file.write(filedata)
    # done 
