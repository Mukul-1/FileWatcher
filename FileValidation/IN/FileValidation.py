import csv
import os
import xml.etree.ElementTree as ET
import GetIdentities
import pandas as pd
from pandasql import sqldf
import shutil
import os
import re
import GetIdentities
import time

# Parse the XML file

def getIdentities():
    token = GetIdentities.get_token()
    identities = GetIdentities.getIdentities(token)
    return(identities)
# Define a function to validate data against validation rules
def validate_data(column_name, data,csvFileNames,customObjectFiles,file):
    if "accounts.csv" in file:
        tree = ET.parse(customObjectFiles["accountsFilePath"])
    else:
        tree = ET.parse(customObjectFiles["entitlementsFilePath"])
    root = tree.getroot()
    error_messages = []
    for element in root:
        #print(element.tag,column_name)
        if element. tag== column_name:
            for validation in element:
                validation_type = validation.attrib['key']
                validation_value = validation.attrib['value']
                error_message = validation.attrib['ErrorMessage']

                # Performing Validation on DataType
                if validation_type == 'DataType':
                    data_type, length = validation_value.split('(')
                    length = int(length[:-1])
                    if data_type == 'String' and len(data) > length:
                        error_messages.append(error_message)

                # Performing Validation on Mandatory Column
                elif validation_type == 'Mandatory':
                    if validation_value == 'Y' and not data:
                        error_messages.append(error_message)
                
                # Performing Validation on format
                elif validation_type == "format_regex":
                    print("Validating in the basis of regex............")
                    if len(validation_value)>0:
                       print(validation_value,data)
                       print(re.match(validation_value,data))
                       if not (re.match(validation_value,data)):
                            error_messages.append(error_message)

                elif validation_type == "API":
                    if len(validation_value)>0:
                        print("Validatin Email using API Call......")
                        validation_value = validation_value.replace('$emailId$',data)
                        validation_value = validation_value.replace('$matchCondition$',validation.attrib['matchCondition'])
                        print("URL to be called : ",validation_value,error_message)
                        token = GetIdentities.get_token()
                        apiResponse = GetIdentities.getIdentities(token,validation_value)
                        # print(len(apiResponse.json()),int(validation.attrib['matchValue']))
                        # print(" if len(apiResponse.json())==int(validation.attrib['matchValue']):",len(apiResponse.json())==int(validation.attrib['matchValue']))
                        if len(apiResponse.json())!=int(validation.attrib['matchValue']):
                            print("Error message for API call: ",error_message)
                            error_messages.append(error_message)

                # Add more validation types as needed
                
    if error_messages:
        return "Failed", "; ".join(error_messages)
    else:
        return "Success", ""

def fileSqlValidations(filePath,customObjectFiles,csvFileNames,files):
    fileSqlResult = ""
    match = ""
    matchValue = ""
    PassMessage = ""
    failMessage = ""
    testRessultPass = ""
    accountsFileName = ""
    entitlementsFileName = ""
    validationMessage =""
    validationFlag = True
    for file in files:
        # print("FileName: "+file)
        filename = os.path.basename(file)
        if "accounts" in filename:
            accountsFileName = filename
        else:
            entitlementsFileName = filename
        
    tree = ET.parse(filePath)
    root = tree.getroot()
    for element in root:
        # print(element.tag)
        for validation in element:
            validation_type = validation.attrib['key']
            validation_value = validation.attrib['value']
            # print(validation.attrib)
            if validation_type == "FileSQL.SQL":
                fileSQL = validation_value
                # Read the first CSV file into a pandas DataFrame
                dfaccounts = pd.read_csv(csvFileNames[0])

                # Read the second CSV file into a pandas DataFrame
                dfentitlements = pd.read_csv(csvFileNames[1])

                fileSQL = fileSQL.replace("[$accountsFileName$]", 'dfaccounts')
                fileSQL = fileSQL.replace("[$entitlementsFileName$]", "dfentitlements")
                #print("Accounts file.......",dfaccounts)
                #print("Entilement file.......",dfentitlements)
                #print(dfentitlements)
                print(fileSQL)
                # Execute the SQL query on the DataFrame
                result_df = sqldf(fileSQL,locals())

                #print(result_df)
                # Print the result DataFrame
                fileSqlResult = str(result_df.iloc[0, 0])  # Assuming the first value is in the first row and first column
                # print("File Sql Result:", fileSqlResult)
            elif validation_type == "FileSQL.PassMessage":
                PassMessage = validation_value
            elif validation_type == "FileSQL.failMessage":
                failMessage = validation_value
            elif validation_type == "FileSQL.match":
                match = validation_value
            elif validation_type == "FileSQL.matchValue":
                matchValue = validation_value
            elif validation_type == "FileSQL.testResultPass":
                testRessultPass = validation_value
            
        if match == "eq":
            if matchValue == fileSqlResult:
                validationMessage += PassMessage+","
            else:
                validationFlag = False
                testRessultPass = "False"
                validationMessage += failMessage+","

    return validationFlag , validationMessage

# Method to create and write fileSql Validations Messages
def fileSqlValidationWriter(validationMessage, filePath,customObjectFiles,csvFileNames):
    print("FilePath : " +filePath)

    fileName = ""
    if "Within" in filePath:
        # Find the index of the last backslash
        last_backslash_index = csvFileNames[0].rfind("\\")

        # Extract the substring till the last index of the backslash
        substring = csvFileNames[0][:last_backslash_index+1]
        fileName = substring+"fileWithinValidation.txt"
    elif "Between" in filePath:
        last_backslash_index = csvFileNames[0].rfind("\\")

        # Extract the substring till the last index of the backslash
        substring = csvFileNames[0][:last_backslash_index+1]
        fileName = substring+"fileBetweenValidation.txt"

    print("Text FileName: " +fileName)
    with open(fileName, 'w') as file:
        messageList = validationMessage.split(',')
        for message in messageList:
            # Write content to the file
            file.write(message+"\n")


def copy_files(source_folder, destination_folder):
    # Check if source folder exists
    if not os.path.exists(source_folder):
        print("Source folder does not exist.")
        return
    
    # Check if destination folder exists, if not, create it
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Iterate through files in the source folder
    for filename in os.listdir(source_folder):
        print(filename)
        if filename.endswith("-accounts.csv") or filename.endswith("-entitlements.csv"):
            source_file = os.path.join(source_folder, filename)
            destination_file = os.path.join(destination_folder, filename)
            
            # Copy file from source to destination
            shutil.copy(source_file, destination_file)
            print(f"File '{filename}' copied successfully.")


def validate(folder_path):
    time.sleep(1)
    print(folder_path)
    stagingFolderPath = "C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Staging"
    actualFolderPath = "C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Actual"
    # accounts_filePath = "C:\|Users\\mukul\Downloads\Demo1stApril (2)\Demo1stApril\IN\Staging\App1\appName-accounts.csv"
    # entitlements_filePath = "C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\appName-entitlements.csv"

    customObjectFiles = {}
    customObjectFiles["withInFileXMLPath"] = "C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Custom Object\\fileWithinValidation.xml"
    customObjectFiles["betweenFileXMLPath"] = "C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Custom Object\\fileBetweenValidation.xml"
    customObjectFiles["accountsFilePath"] = "C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Custom Object\\accountsFileValidation.xml"
    customObjectFiles["entitlementsFilePath"] = "C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Custom Object\\entitlementsFileValidation.xml"


    #for folder_name in os.listdir(stagingFolderPath):
    print("*******************************************************")
    print("Validation Running on ->",folder_path)
    isCsvFilesValidated = True
    #folder_path = os.path.join(stagingFolderPath, folder_name)
    #print(folder_path)
    # Check if it's a folder
    if os.path.isdir(folder_path):
        print(f"Files in folder '{folder_path}':")
            
        # List files inside the folder
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        # Print the names of the files
        csvFileNames = []
        for file_name in files:
            if file_name.endswith("-accounts.csv") or file_name.endswith("-entitlements.csv"):
                csvFileNames.append(os.path.join(folder_path, file_name))
                #print("Files in Folder : " +file_name)

    print("Files in "+folder_path+": ",csvFileNames)
    # Read CSV file, validate each row, and write validated data to a new file
    for file in csvFileNames:
        print("Validating: "+file)
        filename = os.path.basename(file)
        #print(filename)
        with open(file, newline='') as infile, open(file[:-4]+'.validated'+'.csv', 'w', newline='') as outfile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['Validation_Result','Validation_Message']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                validated_row = {}
                validated_row['Validation_Result']=""
                validationFailed_message = ""
                
                for column_name, data in row.items():
                    print("Validating....................",column_name,data)
                    #print(column_name,data)
                    validation_result, error_message = validate_data(column_name, data,csvFileNames,customObjectFiles,file)
                    validated_row[column_name] = data
                    print(validation_result,error_message)
                    if validated_row['Validation_Result'] != "Failed":
                        validated_row['Validation_Result'] = validation_result
                    print("Validation Failed : " +error_message)
                    if len(error_message)>0:
                        print("Validation Flag is changed to False because of error")
                        isCsvFilesValidated = False
                        validationFailed_message = validationFailed_message+error_message+";"
                    validated_row['Validation_Message'] = validationFailed_message
                print("Messages written in files",validated_row)
                writer.writerow(validated_row)
            
    #Calling Methods to Perform fileSqlValidation (i.e. fileWithinValidations and FileBetweenValidations)
    validationFlag1 , validationMessage = fileSqlValidations(customObjectFiles["withInFileXMLPath"],customObjectFiles,csvFileNames,files)
    fileSqlValidationWriter(validationMessage, customObjectFiles["withInFileXMLPath"],customObjectFiles,csvFileNames)
    validationFlag2 , validationMessage = fileSqlValidations(customObjectFiles["betweenFileXMLPath"],customObjectFiles,csvFileNames,files)
    fileSqlValidationWriter(validationMessage, customObjectFiles["betweenFileXMLPath"],customObjectFiles,csvFileNames)
    print(isCsvFilesValidated,validationFlag1,validationFlag2)
    if isCsvFilesValidated and validationFlag1 and validationFlag2:
        print("Validation Passed")
        print("Copying Files to Actual folder......")

        last_backslash_index = csvFileNames[0].rfind("\\")

        # Extract the substring till the last index of the backslash
        AppilcationFolderName = csvFileNames[0][:last_backslash_index+1]
        print(AppilcationFolderName)

        print("Copying files to Actual Folder..................")
        source_folder = AppilcationFolderName
        destination_folder = AppilcationFolderName.replace("Staging","Actual")

        copy_files(source_folder, destination_folder)

        print("Copying files to Archival Folder..................")
        source_folder = AppilcationFolderName
        destination_folder = AppilcationFolderName.replace("Staging","Archival")

        copy_files(source_folder, destination_folder)


        token = GetIdentities.get_token()
        #triggerAggregationResponse = GetIdentities.triggerAggregation(token)

        #print(triggerAggregationResponse.json())

    else:
        print("Validation Failed")

#validate("C:\\Users\\mukul\\Downloads\\Demo1stApril (2)\\Demo1stApril\\IN\\Staging\\App1")




