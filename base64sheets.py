"""
File Name     :: base64sheets.py
Description   :: Base64 encodes given file and saves it to Google Sheets or downloads and decodes file from Sheets
License       :: MIT
Contributors  :: Marijan Stoicic [GH: mstoicic]
"""

import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sys import argv, exit
from os import remove


# AUTH
# Authentication files & configuration.
# Be sure to replace your own json file name here.


json_file = '[your file here].json'
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)


def chunk_str(bigchunk, chunk_size):
    return [bigchunk[i:i + chunk_size] for i in range(0, len(bigchunk), chunk_size)]


# UPLOAD FUNCTION
def sheetpost_put(sheet_id, filename):
    '''File upload process for 'put'.'''
    try:
        gc = gspread.authorize(credentials)
        wks = gc.open_by_key(sheet_id).sheet1
        print ("Logged into Sheets!")
    except Exception:
        exit("Error logging into Google Sheets. Check your authentication.")

    # base64-encode the source file
    with open(filename, "rb") as uploadfile:
        encoded = base64.b64encode(uploadfile.read())
    print ("Encoded file into base64 format!")
    
    # Wipe the sheet
    print ("Wiping the existing data from the sheet.")
    row_sweep = 1
    column_sweep = 1
    while wks.cell(row_sweep, column_sweep).value != "":
        if row_sweep == 1000:
            row_sweep = 1
            column_sweep += 1
        wks.update_cell(row_sweep, column_sweep, "")
        row_sweep += 1

    # Write the chunks to Drive
    cell = 1
    column = 1
    chunk = chunk_str(encoded, 49500)

    print ("Writing the chunks to the sheet. This may take some time.")
    for part in chunk:
        if cell == 1000:
            print ("Ran out of rows, adding a column.")
            cell = 1
            column += 1
        
        # Add a ' to each line to avoid starting with = (prevents being interpreted as a formula)
        part = "'" + part
        wks.update_cell(cell, column, part)
        cell += 1

    # Delete the base64-encoded file
    remove(filename)
    print ("All done! " + str(cell) + " cells filled in Sheets.")

# DOWNLOAD FUNCTION
def sheetpost_get(sheet_id, filename):
    '''File download process for 'get'.'''

    try:
        gc = gspread.authorize(credentials)
        wks = gc.open_by_key(sheet_id).sheet1
        print ("Logged into Sheets! Downloading the base64 code. This might take some time.")
    except Exception:
        exit("Error logging into Google Sheets.\n Check your authentication and make sure you have  a "
             "sheet to work with.")

    row_sweep = 1
    column_sweep = 1
    values_list = []
    values_final = []

    # Trim out the extra single quotes
    while wks.cell(row_sweep, column_sweep).value != "":
        values_list = wks.col_values(column_sweep)
        for value in values_list:
            if row_sweep > 1:
                value = value[1:]
            values_final += value
            column_sweep += 1
        values_final = "".join(values_final)

    # Saves downloaded thing to file
    with open(filename, "wb") as recoverfile:
        recoverfile.write(values_final)

    #Decoding
    print ("Saved Sheets data to decode! Decoding now. Beep boop.")
    with open(filename, "rb+") as downfile:
        decoded = base64.b64decode(downfile.read())
        downfile.write(decoded)
    print ("Data decoded! All done!")


# HELP
# The help message that displays if none or too
# few arguments are given to properly execute.
help_message = '''To upload a sheetpost:
\t base64sheets.py put [GSheets key from URL] [Input filename]"
To retrieve a base64sheets:
\t base64sheets.py get [GSheets key from URL] [Output filename]"'''


# MAIN PART
if __name__ == "__main__":
    if len(argv) < 4:
        print ("Too few arguments!")
        exit(help_message)

    sheet_id = str(argv[2])
    filename = str(argv[3])

    if argv[1] == "put":
        sheetpost_put(sheet_id, filename)

    elif argv[1] == "get":
        sheetpost_get(sheet_id, filename)

    else:
        print ("Unknown operation (accepts either 'get' or 'put')")
    exit(help_message)