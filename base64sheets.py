import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sys import argv, exit
from os import remove


# AUTH
# -------------------------------------------------------
# Authentication files & configuration.
# Be sure to replace your own json file name here.
# -------------------------------------------------------


json_file = '[your file here].json'
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scope)


def chunk_str(bigchunk, chunk_size):
    return [bigchunk[i:i + chunk_size] for i in range(0, len(bigchunk), chunk_size)]


# UPLOAD

def sheetpost_put(sheet_id, filename):
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

    print ("Writing the chunks to the sheet. This'll take a while. Get some coffee or something.")
    for part in chunk:
        if cell == 1000:
            print ("Ran out of rows, adding a column.")
            cell = 1
            column += 1
        # Add a ' to each line to avoid it being interpreted as a formula
        part = "'" + part
        wks.update_cell(cell, column, part)
        cell += 1

    # Delete the base64-encoded file
    remove(filename + ".out")
    print ("All done! " + str(cell) + " cells filled in Sheets.")
