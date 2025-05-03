import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

def parse_nmea(nmea_str):
    # Check if NMEA string is valid and starts with $GPGGA
    if not nmea_str or not nmea_str.startswith('$GPGGA'):
        return 0, 0

    # Split the NMEA string
    parts = nmea_str.split(',')
    if len(parts) < 10:
        return 0, 0

    # Extract latitude
    lat = parts[2]
    lat_dir = parts[3]
    if not lat or not lat_dir:
        return 0, 0
    lat_deg = float(lat[:2])
    lat_min = float(lat[2:])
    latitude = lat_deg + (lat_min / 60)
    if lat_dir == 'S':
        latitude = -latitude

    # Extract longitude
    lon = parts[4]
    lon_dir = parts[5]
    if not lon or not lon_dir:
        return 0, 0
    lon_deg = float(lon[:3])
    lon_min = float(lon[3:])
    longitude = lon_deg + (lon_min / 60)
    if lon_dir == 'W':
        longitude = -longitude

    return latitude, longitude

def fetch_data():
    print("Fetching data from Google Sheets...")
    
    # Set up Google Sheets API credentials
    print("Loading credentials...")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    print("Credentials loaded successfully")
    client = gspread.authorize(creds)

    # Open the Google Sheet using the spreadsheet ID
    spreadsheet_id = "1E6u3Eyx_GHFpIbWGmEc6b00KoiWD0DsSSJwHZx686EA"
    sheet = client.open_by_key(spreadsheet_id).sheet1

    # Get all records from the sheet
    records = sheet.get_all_records()
    headers = sheet.row_values(1)
    print(f"Headers: {headers}")

    # Process the data
    data = []
    valid_entries = 0
    for record in records:
        name = record.get('username', '')
        timestamp = record.get('Sign in time (GPS Time)', '')
        request = record.get('request', '')
        nmea = record.get('latest nmea', '')

        # Parse latitude and longitude from NMEA string
        latitude, longitude = parse_nmea(nmea)

        # Skip entries with invalid coordinates (latitude or longitude = 0)
        if latitude == 0 or longitude == 0:
            continue

        # Create entry
        entry = {
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': timestamp,
            'request': request
        }
        data.append(entry)
        valid_entries += 1

    print(f"Parsed {valid_entries} valid entries")

    # Save to data.json
    print("Saving to data.json...")
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Data fetched and saved to data.json")

if __name__ == "__main__":
    fetch_data()