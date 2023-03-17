import os,re,logging

from settings import settings




def renameFiles():
    #Start by parsing the new file format. The result is an array of tuples of the form (a,b), where a is either "string", "group", or "intgroup" and b is the content of the string or the number of the group. In case of "intgroup", b is a tuple (b_1,b_2), where b_1 is the number of the group and b_2 is a number that will be added/subtracted
    newNameFormat = []

    rawNameFormat = settings['NewFileFormat']
    if len(rawNameFormat) == 0:
        logging.error("The name format string defined in the settings is empty. Stopping program.")
        return

    lastPositionParsed = -1
    currentlyParsingGroup = False
    groupStartPosition = -1
    foundIntGroup = False
    positionOfIntGroupPlusMinus = -1
    skipUntilPosition = -1
    for i in range(0, len(rawNameFormat)):
        if i < skipUntilPosition:
            continue

        if not currentlyParsingGroup:
            #Found a group identifier
            if rawNameFormat[i] == "#":

                #Add previous string to parsed format
                if i > lastPositionParsed + 1:
                    newNameFormat.append(["string", rawNameFormat[lastPositionParsed + 1 : i]])
                lastPositionParsed = i-1

                #Check for the special case where "#()" has to be parsed as "#"
                if rawNameFormat[i:i+3] == "#()":
                    newNameFormat.append(["string", "#"])
                    lastPositionParsed = i + 2
                    skipUntilPosition = i + 3
                else:
                    #Continue by checking group
                    groupStartPosition = i
                    currentlyParsingGroup = True
        
        #Currently parsing group
        else:
            if i == groupStartPosition + 1:
                if rawNameFormat[i] != "(":
                    logging.error("The name format string contains a '#' (pos {groupStartPosition}) that is not followed by '('. Stopping program.")
                    return
            else:
                numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
                intgroupoperators = ["+", "-"]
                allowedChars = numbers + intgroupoperators +  [")"]
                if rawNameFormat[i] not in allowedChars:
                    logging.error(f"The name format string contains a '#' group (pos {groupStartPosition}) with non-number characters that are also not '+' or '-'. Stopping program.")
                    return
                
                #Handle group opening
                if i == groupStartPosition + 2 and rawNameFormat[i] not in numbers:
                    logging.error(f"The name format string contains a non-empty '#' group (pos {groupStartPosition}) that does not start with a number. Stopping program.")
                    return
                
                #Handle +/- special cases
                if rawNameFormat[i] in intgroupoperators:
                    if foundIntGroup:
                        logging.error(f"The name format string contains a '#' group (pos {groupStartPosition}) with more than one '+'/'-'. Stopping program.")
                        return
                    else:
                        foundIntGroup = True
                        positionOfIntGroupPlusMinus = i


                
                #Handle group closing:
                if rawNameFormat[i] == ")":

                    if not foundIntGroup:
                        newNameFormat.append(["group", int(rawNameFormat[groupStartPosition + 2 : i]) ])
                    else:
                        groupNumber = int(rawNameFormat[groupStartPosition + 2 : positionOfIntGroupPlusMinus])
                        intToBeAdded = int(rawNameFormat[positionOfIntGroupPlusMinus + 1 : i])
                        if rawNameFormat[positionOfIntGroupPlusMinus] == "-":
                            intToBeAdded = -1 * intToBeAdded
                        newNameFormat.append(["intgroup", [groupNumber, intToBeAdded]])

                    lastPositionParsed = i
                    currentlyParsingGroup = False
                    foundIntGroup = False
    
    #Finalize String parsing:
    if currentlyParsingGroup:
        logging.error(f"The name format string contains a '#' group (pos {groupStartPosition}) that is not closed. Stopping program.")
        return
    if not (lastPositionParsed == len(rawNameFormat) - 1):
        newNameFormat.append(["string", rawNameFormat[lastPositionParsed + 1 :]])



    logging.info("Parsed new name format:")
    logging.info(newNameFormat)

    

    #Look for the files and make a testrun

    print()
    print("Displaying files to be renamed:")
    print()

    filelist = os.listdir(settings['Path'])
    regex = re.compile(settings['FileRegex'])
    
    count = 0
    for file in filelist:
        if renameSingleFile(file, regex, newNameFormat, True):
            count += 1
    
    print()
    print(f"Found {count} matching files. Do you want to apply new names? If so, enter 'YES'. Enter any other string to abort.")

    rename = input()
    print()
    if rename == "YES":
        count = 0
        for file in filelist:
            if renameSingleFile(file, regex, newNameFormat, False):
                count += 1
        print()
        print(f"Successfully renamed {count} files.")
        
    else:
        print("Aborted renaming.")
        return



def renameSingleFile(file, regex, newNameFormat, testrun):
    match = regex.match(file)

    if match:
        newName = ""
        for part in newNameFormat:
            if part[0] == "string":
                newName += part[1]
            elif part[0] == "group":
                newName += match.group(part[1] % (len(match.groups()) + 1))
            elif part[0] == "intgroup":
                number = int(match.group(part[1][0] % (len(match.groups()) + 1)))
                number = number + part[1][1]
                newName += str(number)

        if testrun:
            print(f"{file}   -->   {newName}")
        else:
            os.rename(settings['Path'] +"\\"+ file, settings['Path'] +"\\"+ newName)
            print("Renamed file to:  " + newName)

    return match
        






if __name__ == '__main__':

    #Prepare Logging
    logginglevels = {
        "DEBUG" : logging.DEBUG,
        "INFO" : logging.INFO,
        "WARNING" : logging.WARNING,
        "ERROR" : logging.ERROR,
        "CRITICAL" : logging.CRITICAL,
    }
    logging.basicConfig(level=logginglevels.get(settings["LoggingLevel"], logging.ERROR), format = "LOGGING:%(levelname)s   %(message)s")

    renameFiles()


