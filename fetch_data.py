import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1E6u3Eyx_GHFpIbWGmEc6b00KoiWD0DsSSJwHZx686EA'
RANGE_NAME = 'Sheet1!A:L'
CREDENTIALS_FILE = '/app/credentials.json'

def get_google_sheets_service():
    try:
        print("Loading credentials...")
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        print("Credentials loaded successfully")
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        print(f"Error loading credentials: {str(e)}")
        raise

def parse_nmea(gga_sentence):
    try:
        if "Ntrip-GGA: " in gga_sentence:
            gga_sentence = gga_sentence.split("Ntrip-GGA: ")[1].strip()
        parts = gga_sentence.split(",")
        if len(parts) < 10:
            print(f"Invalid GGA sentence (too few fields): {gga_sentence}")
            return None, None
        lat_str = parts[2]
        lon_str = parts[4]
        if not lat_str or not lon_str:
            print(f"Empty lat/lon fields: {gga_sentence}")
            return None, None
        if lat_str in ['0000.0000', '0.0000', '0.0', '0'] or lon_str in ['00000.0000', '0000.0000', '0.0000', '0.0', '0']:
            print(f"Zero lat/lon (no fix): {gga_sentence}")
            return None, None
        lat = float(lat_str) / 100
        lon = float(lon_str) / 100
        lat = int(lat) + (lat % 1) * 100 / 60
        lon = int(lon) + (lon % 1) * 100 / 60
        if parts[3] == "S":
            lat = -lat
        if parts[5] == "W":
            lon = -lon
        return lat, lon
    except Exception as e:
        print(f"Error parsing NMEA: {e} - Sentence: {gga_sentence}")
        return None, None

def fetch_and_save_data():
    try:
        print("Fetching data from Google Sheets...")
        service = get_google_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()
        values = result.get('values', [])
        if not values:
            print("No data found in Google Sheet.")
            return

        headers = values[0]
        print(f"Headers: {headers}")
        data = []
        for row in values[1:]:
            if len(row) >= 12:  # Ensure row has enough columns (up to latest nmea)
                try:
                    nmea = row[11] if len(row) > 11 else ''
                    lat, lon = parse_nmea(nmea) if nmea else (None, None)
                    data.append({
                        "name": row[0] or '',
                        "latitude": lat,
                        "longitude": lon,
                        "timestamp": row[8] or '',
                        "request": row[10] or ''
                    })
                except ValueError as e:
                    print(f"Error parsing row {row}: {e}")
                    continue

        # Filter out invalid entries
        data = [entry for entry in data if entry["latitude"] is not None and entry["longitude"] is not None]
        print(f"Parsed {len(data)} valid entries")

        # Save to JSON
        print("Saving to data.json...")
        with open("/app/data.json", "w") as f:
            json.dump(data, f)
        print("Data fetched and saved to data.json")

    except Exception as e:
        print(f"Error fetching data: {str(e)}")

if __name__ == "__main__":
    fetch_and_save_data()