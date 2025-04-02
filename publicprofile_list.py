import os
import csv
import time
import requests
import sqlite3

directory = r"c:\Users\Student\Desktop\wynn programs\raiddays"
file_name = "day2.csv"  # Taken from valor's tables
file_path = os.path.join(directory, file_name)
db_path = os.path.join(directory, "public_uuids.db")
api_url = "https://api.wynncraft.com/v3/player/{uuid}"
rate_limit = 100

if not os.path.exists(file_path):
    print(f"File '{file_name}' does not exist in the directory: {directory}")
    exit()

with open(file_path, mode='r') as csv_file:
    reader = csv.DictReader(csv_file)
    uuids = set(row['uuid'] for row in reader if 'uuid' in row)

print(f"Found {len(uuids)} unique UUIDs in today's list.")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS public_uuids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL
)
""")
conn.commit()

cursor.execute("DELETE FROM public_uuids WHERE uuid NOT IN ({})".format(",".join("?" for _ in uuids)), tuple(uuids))
conn.commit()
print("Removed rows for UUIDs not in today's list.")

for index, uuid in enumerate(uuids):
    cursor.execute("SELECT 1 FROM public_uuids WHERE uuid = ?", (uuid,))
    row = cursor.fetchone()
    if row:
        print(f"UUID {uuid} already exists in the database. Skipping API request.")
        continue
    response = requests.get(api_url.format(uuid=uuid))
    if response.status_code != 200:
        print(f"Failed to fetch data for UUID: {uuid}. Status code: {response.status_code}")
        continue

    data = response.json()
    public_profile = data.get('publicProfile', False)

    if public_profile:
        try:
            cursor.execute("""
            INSERT INTO public_uuids (uuid)
            VALUES (?)
            """, (uuid,))
            conn.commit()
            print(f"UUID {uuid} has a public profile and was added to the database.")
        except sqlite3.Error as e:
            print(f"Error inserting UUID {uuid} into database: {e}")
    else:
        print(f"UUID {uuid} does not have a public profile. Skipping.")

    if (index + 1) % rate_limit == 0:
        print("Rate limit reached. Sleeping for 60 seconds...")
        time.sleep(60)

conn.close()
print(f"Public UUIDs saved to the database at {db_path}.")