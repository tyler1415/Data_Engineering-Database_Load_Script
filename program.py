from xml.etree import ElementTree
from File import File
from datetime import datetime
import os
import pymongo
import shutil
import glob

# password = "m15C4pst0n3"
# myClient = pymongo.MongoClient("mongodb+srv://OpenAdmin:" + password + "@cluster0-z4nqv.azure.mongodb.net/test?retryWrites=true&w=majority")
# myDB = myClient["TestUAOpen"]
# myCol = myDB["tests"]


# change IP address to server address as needed
myClient = pymongo.MongoClient("mongodb://127.0.0.1:27017")
# connect to database
myDB = myClient["UAOpen"]
# connect to the collection
myCol = myDB["expenditures"]
# inputList gets the file paths from the user
inputList = list()
# fileList derives some attributes from the file name and stores them in the file class
fileList = list()
# Save working directory so we can move files over to archive later in the program
projectRoot = os.path.abspath(os.curdir)


# This method is to get the list of files from the user to upload to the database
def GetUserInput(inputList):
    # change directory to get all files in import folder
    os.chdir(r"" + projectRoot + r"\import")

    # get all files in folder by there file type (xml)
    for x in glob.glob("*.xml"):
        inputList.append(os.path.abspath(x))

    return inputList


# This method is to get info from the file name in the inputList and then upload that information to fileList.
# fileList is just a list of file objects to be loaded into the database.
def GetDataFromFileName(inputList, fileList):
    # iterate through all files in the input list to get attributes from them
    for i in inputList:
        # Find "FILE_" because the year and month will always follow it.
        findYearAndMonth = i.find('opn')

        # get substring from the given file path to get year and month.
        startOfQuery = findYearAndMonth - 7
        endOfQuery = findYearAndMonth - 1
        fullQuery = i[startOfQuery:endOfQuery]

        # separate out substring into fYEAR and the month.
        fYear = fullQuery[0:4]
        month = fullQuery[4:6]

        # get period from month
        intMonth = int(month)
        if intMonth >= 1 and intMonth <= 9:
            fPeriod = intMonth + 3
        else:
            fPeriod = intMonth - 9

        # get funding source
        find = i.find('opn')
        fundingSourceQuery = find + 4
        fundingSourceQueryEnd = find + 7
        fundingSourceQueryFull = i[fundingSourceQuery:fundingSourceQueryEnd]

        # define funding source
        if fundingSourceQueryFull == "ala":
            funding = "The University of Alabama"
        else:
            funding = "UA System Office"

        # get the folder path from where you want to extract data from.
        folderPath = i.find("opn")
        folderQuery = i[0:folderPath - 7]

        # set all of the previous information to an instance of a class
        file = File()
        file.set_fYear(fYear)
        file.set_fPeriod(fPeriod)
        file.set_funding(funding)
        file.set_folderQuery(folderQuery)
        file.set_fileName(i)

        fileList.append(file)

    return fileList


# This method is to purge the database of the last time the file`s info was loaded into  the database
def PurgeDatabase(fileList):
    # query to delete. Delete based on fYear, fPeriod, and funding source
    for i in fileList:
        myQuery = {"FYEAR": i.get_fYear(),
                   "FPERIOD": i.get_fPeriod(),
                   "FUNDING": i.get_funding()}

        myCol.delete_many(myQuery)


# This method is to populate the database with the XML file that was given by the user
def PopulateDatabase(fileList):
    for i in fileList:
        # change directory so you can grab xml file from outside this program.
        # Also get the root so you can then access the elements of XML document.
        os.chdir(r"" + i.get_folderQuery())
        tree = ElementTree.parse(r"" + i.get_fileName().replace('"', ''))
        root = tree.getroot()

        # add in data from xml file
        for entry in root.findall('ROW'):
            stringDate = entry.find('DATE').text
            DATE = datetime.strptime(stringDate, '%d-%b-%y')
            PAYEE = entry.find('PAYEE').text
            CATEGORY = entry.find("CATEGORY").text
            AGENCY = entry.find("AGENCY").text
            FUNDING = entry.find("FUNDING").text
            TRAN_NO = entry.find("TRAN_NO").text
            PO_NO = entry.find("PO_NO").text
            CHECK_NO = entry.find("CHECK_NO").text
            CANCEL_IND = entry.find("CANCEL_IND").text
            TRANS_AMT = entry.find("TRANS_AMT").text
            RANDOM = ""
            importDateString = datetime.now().strftime('%Y-%m-%d')
            IMPORT_DATE = datetime.strptime(importDateString, '%Y-%m-%d')
            FYEAR = i.get_fYear()
            FPERIOD = i.get_fPeriod()
            SOURCE = ""

            # We have to hard code these in as strings so they can be passed to the front end easily.
            if PO_NO is None:
                PO_NO = "null"
            if CHECK_NO is None:
                CHECK_NO = "null"

            # connects a data model to our data from above
            myDict = {"DATE": DATE,
                      "PAYEE": PAYEE,
                      "CATEGORY": CATEGORY,
                      "AGENCY": AGENCY,
                      "FUNDING": FUNDING,
                      "TRAN_NO": TRAN_NO,
                      "PO_NO": PO_NO,
                      "CHECK_NO": CHECK_NO,
                      "CANCEL_IND": CANCEL_IND,
                      "TRANS_AMT": TRANS_AMT,
                      "RANDOM": RANDOM,
                      "IMPORT_DATE": IMPORT_DATE,
                      "FYEAR": FYEAR,
                      "FPERIOD": FPERIOD,
                      "SOURCE": SOURCE}

            # add to collection
            myCol.insert_one(myDict)


def ExportToArchive(fileList, projectRoot):
    # change directory to that of this PyCharm project
    os.chdir(r"" + projectRoot + r"\archive")
    archiveRoot = os.path.abspath(os.curdir).replace('"','')

    for i in fileList:
        #parse through the file path and add date time and naming convention stuff
        query = i.get_fileName().find("opn")

        startOfQuery = query - 7
        endOfQuery = query + 18
        fullQuery = i.get_fileName()[startOfQuery:endOfQuery]
        x = datetime.now().strftime('%Y%m%d%M%S')
        fullQueryFinal = x + "_FILE_" + fullQuery

        # move files from import folder to archive folder with appropriate naming convention
        shutil.move(i.get_fileName().replace('"',''), os.path.join(archiveRoot, fullQueryFinal.replace('"','')))


GetUserInput(inputList)

GetDataFromFileName(inputList, fileList)

PurgeDatabase(fileList)

PopulateDatabase(fileList)

ExportToArchive(fileList, projectRoot)
