from pathlib import Path
import csv
import json
import re

reldir = str(Path.cwd())


def clean(fname):

    # try to open the NPI csv and read into a dictionary
    nFname = reldir + '\\npi_master_list.csv'
    npiDict = dict()
    try:
        with open(nFname, "r", encoding="utf8") as npifile:
            csvr = csv.reader(npifile, delimiter=',')
            # skip the header
            next(csvr)
            for line in csvr:
                rd = (line[0], line[23], line[25], line[39], line[40])
                if rd[1] == 'MD' or rd[1] == 'DC':
                    npiDict.setdefault(rd[0], (rd[1], rd[2], rd[3], rd[4]))

    except FileNotFoundError as e:
        print("Failed to open file")
        print(str(e))

    except Exception as e:
        print("Failed to read features from file")
        print(str(e))

    # try to open the doctor text, read the raw data, check validity, and write to a csv
    docList = []
    try:
        with open(fname, "r") as dfile:

            # open up a json to write to
            newfle = open(reldir + "\\carefirst_bluechoice_doctors.json", "w")
            # string tidying and formatting
            for line in dfile:
                line = line.replace("None", 'NULL')
                line = line.replace("'", '"')
                line = line.replace(": ", ': "')
                line = line.replace(', "', '", "')
                line = line.replace("[[{", "{")
                line = line.replace("}]]", "}")
                line = line.replace('"[{', "[{")
                line = line.replace('}]}"', "}]}")
                line = line.replace('""', '"')
                line = line.replace('"[', '["')
                line = line.replace(']"', '"]')
                line = line.replace('""', '"')
                line = line.replace(' ",', ' "NULL",')
                line = line.replace('}]}]', "}]}")
                line = line.replace('["]', '["NULL"]')
                line = re.sub(r'(\w+)(")(\s)*(\w+)', r"\1'\3\4", line)
                line = line.replace('[{"email"', '{"email"')
                line = "[" + line + "]"

                # try to load the tidy string as json into list
                try:
                    docList = json.loads(line)
                except Exception as e:
                    print("Failed to load features to json")
                    print(str(e))

                # loop through the list
                recordIdx = 0
                while recordIdx <= len(docList):
                    # check the npi dictionary for validity and delete items from the list that aren't valid
                    npis = docList[recordIdx]["npis"]
                    # check the deactivated status and reactivated status
                    for npi in npis:
                        if npi in npiDict:
                            if npiDict[npi][2] != '':
                                if npiDict[npi][3] == '':
                                    docList.pop(recordIdx)
                                    recordIdx -= 1
                    # if both npis fail the provider is thrown out
                    if all(npi not in npiDict for npi in npis):
                        docList.pop(recordIdx)
                        recordIdx -= 1
                    # if we deleted too much to continue then break out were done
                    if recordIdx >= len(docList)-1:
                        break
                    recordIdx += 1
                # write the update list to a json file
                json.dump(docList, newfle)
                newfle.close()

    except FileNotFoundError as e:
        print("Failed to open file")
        print(str(e))

    except KeyError as e:
        print("Requested key doesn't exist")
        print(str(e))

    except Exception as e:
        print("Failed to read features from file")
        print(str(e))


if __name__ == '__main__':
    clean(reldir + '\\carefirst_bluechoice_doctors.txt')
