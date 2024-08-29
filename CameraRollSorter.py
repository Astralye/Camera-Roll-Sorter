import os, datetime, calendar
from PIL import Image

# The file has to be one directory above the sorted images
# This script looks at a directory lower (in a folder)

# E.g C:\Desktop\Photos\... (all the photos within the Photos folder)

# Or
# C:.
# ├───Desktop
# │   ├───ImageSorter.py <-- Place file here, Input (Photos into the arguments)
# │   └───Photos
# │        ├───Image1.png
# │        ├───Image2.jpg
# │        ├───Video1.mov
# │        │
# │        ...
# ...

# Store Folder data to use later

printable = False
debugMode = False

# Print extra information
def enablePrint():
    global printable
    validInput = False
    
    print("Enable Print logs? Enabling will affect performance speed. y/n")
    
    while (not validInput):
        printLog = str(input("> ")).lower()        
        validInput = True if (printLog == "y" or printLog == "n") else False
        
        if (not validInput):
            print("Valid commands: y, n")
            continue
        else:
            break
        
    if(printLog == "y"):
        printable = True
    else:
        printable = False

# Stops after one image. Must enter. Debugging purposes
def enableDebug():
    global debugMode
    validInput = False
    
    print("Pause after every image? (Debugging) y/n")
    
    while (not validInput):
        printLog = str(input("> ")).lower()        
        validInput = True if (printLog == "y" or printLog == "n") else False
        
        if (not validInput):
            print("Valid commands: y, n")
            continue
        else:
            break
        
    if(printLog == "y"):
        debugMode = True
    else:
        debugMode = False

class Folder:
    def __init__(self, folderName, fileArray, noFiles):
        self.folderName = folderName
        self.fileArray = fileArray;
        self.noFiles = noFiles;

class Date:
    def __init__(self,year = 0,month = 0):
        self.year = year
        self.month = month

# Ask user for relative directory 
def getRelativeDirectory():
    validFolder = False
    
    print("Enter relative directory of folder to be sorted")
    while (not validFolder):
        folderName = str(input("> "))        
        validFolder = os.path.isdir(folderName)
        
        if (not validFolder):
            print(f"'{folderName}' does not exist within the folder")
            continue
        break
    
    fileArray = os.listdir(folderName)
    noFiles = len(fileArray)
    return Folder(folderName, fileArray, noFiles)

def getEXIFdata(path):
    exif = Image.open(path)._getexif()
    if not exif:
        raise Exception('Image {0} does not have EXIF data.'.format(path))
    return exif[36867]

def existEXIFdata(path):
    try:
        existDate = getEXIFdata(path)
        return True
    except:
        return False

def getFileDate(fileName, fileNameFull):
    # variable initializer
    fileDate = None
    # location of extension, from the end.
    indexdot = fileName.rindex('.') - len(fileName) + 1
    fileExtension = fileName[indexdot:].lower()

    if(printable): print(f"File Extension      : {fileExtension}")    
    containsEXIFdata = existEXIFdata(fileNameFull)
    
    # png, jpg, heic CAN contain EXIF data
    # If exist, use those, if not, use oldest file modification / creation date
    
    if(printable): print(f"Image      : {fileName}")
    if fileExtension == "png" or fileExtension == "jpg" or fileExtension == "heic" or fileExtension == "mov":
        if containsEXIFdata:
            if(printable): print("EXIF data? : Yes")
            date = getEXIFdata(fileNameFull)
            
            return Date(date.split(":")[0], calendar.month_name[int(date.split(":")[1])])

    # If no exif data (png,jpg,heic) or other files

    if (not containsEXIFdata):
        if(printable): print("EXIF data? : None")
        # Created may be later than modified.
        oldestDate = None
        lastModified = datetime.datetime.fromtimestamp(os.path.getmtime(fileNameFull)).date()
        lastCreated = datetime.datetime.fromtimestamp(os.path.getctime(fileNameFull)).date()
        
        if(lastModified.year < lastCreated.year):
            # Store last modified date
            oldestDate = lastModified
        else:
            # Same or later, sort by month
            if lastModified.month < lastCreated.month:
                oldestDate = lastModified
            else:
                oldestDate = lastCreated
        return Date(str(oldestDate.year), oldestDate.strftime("%B"))

def doesFolderExist(directory):
    return True if os.path.exists(directory) else False

# Creates a directory if not present
def directoryManager(yearDirectory, monthDirectory):
    yearFolderExist = doesFolderExist(yearDirectory)
    if(printable): print(f'Year folder exist?  : {yearFolderExist}')
    
    monthFolderExist = doesFolderExist(monthDirectory)
    if(printable): print(f'Month folder exist? : {monthFolderExist}')
    
    # If folder does not exist, create new directory
    if( not yearFolderExist):
        print(f"Creating a new directory: '{yearDirectory}'")
        os.makedirs(yearDirectory)

    if( not monthFolderExist):
        print(f"Creating a new directory: '{monthDirectory}'")
        os.makedirs(monthDirectory)

# Moves file locaton to specified folder
# New folder name, file name and old name
def moveFile(folderName, fileName, fileNameFull):
    newLocation = os.path.join(folderName, fileName)
    
    os.rename(fileNameFull, newLocation)

def lookThroughDirectory(folderObject):

    noFiles = folderObject.noFiles
    for fileName in folderObject.fileArray:
        fileNameFull = os.path.join(folderObject.folderName, fileName)
        
        if not os.path.isfile(fileNameFull): # Check if file exists
            continue

        fileDate = getFileDate(fileName, fileNameFull)
        if(printable): print(f'File date  : {fileDate.month}, {fileDate.year}')
        
        yearDirectory = os.path.join(folderObject.folderName, fileDate.year)
        monthDirectory = os.path.join(yearDirectory, fileDate.month)
        
        directoryManager(yearDirectory, monthDirectory);
        moveFile(monthDirectory, fileName, fileNameFull)

        noFiles -= 1
        print(f'Images remaining    : {noFiles}')

        global debugMode
        if(debugMode): input()

if __name__ == "__main__":
    enablePrint()
    enableDebug()
    mainDirectory = getRelativeDirectory();
    lookThroughDirectory(mainDirectory)

    print("Files Sorted")
    print("Enter to exit program")
    input("> ")
