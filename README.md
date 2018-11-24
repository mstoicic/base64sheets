# base64sheets

## What
Upload & download base64-encoded data with Google Sheets.

This abomination uses base64 and [gspread](https://github.com/burnash/gspread) to post single files to Google Sheets.
It can encode pictures,videos, music and more in a highly inefficient way that won't count towards your Google Drive storage. The size limit is determined by Google Sheet's hard cap of 2 million cells, which is ~99 GB of encoded data at 49,500 characters (or bytes) per cell. The ratio of output bytes to input bytes is 4:3 (33% overhead).

Uploading takes forever, but downloading is faster.


## Setup
Gspread requires valid Drive API credentials for use in OAuth2. [See here](https://gspread.readthedocs.io/en/latest/oauth2.html).

In base64sheets.py, edit the following value:
```
json_file = '[your file here].json'
```

Additionally, you'll need to spoonfeed it a Google Sheet to start off with (via key, which is found in the URL when opening the spreadsheet in a browser), and that blank sheet must be "shared" with the service account you created (so the program can write to it).

You'll need gspread and oauth2client installed.
```
pip install gspread oauth2client
```
or
```
pip install requirements.txt
```


## Usage

To upload:
```
base64sheets.py put [GSheets key from URL] [Input filename]
```
This will delete all previously existing content in the target sheet.

To download:
```
base64sheets.py get [GSheets key from URL] [Output filename]
```

Example:

```
base64sheets.py put 1cagGaHFBk5rFjJ6klMRwdVsUvTgslWtg9x8B-rz5C-I "C:\image\image.png"

base64sheets.py get 1cagGaHFBk5rFjJ6klMRwdVsUvTgslWtg9x8B-rz5C-I "C:\image\reassembled_image.png"
```

Note that Sheets have no idea what format uploaded files actually are, so you'll have to remember what each sheetpost contains.

## Quirks
- Uploading is slow. A 5MB file takes roughly ~3 minutes. Download is a lot faster!
- It doesn't support multiple files, but you can use a .rar or .7z archive.
- Google Sheets has a hardcoded character limit of 50,000 per cell. Sheetpost utilizes 49,500 character per cell, just to be safe. You can probably tweak this and gain some more "performance".
- Sheets interprets a cell starting with "=" as a formula. To combat this, Sheetpost prepends every single line with a single quote (').
This is stupid, but it works. The `get` mode consequently trims out the first single quote per cell when reassembling the file.
