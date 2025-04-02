import sqlite3
import requests

db_path = r"c:\Users\Student\Desktop\wynn programs\raiddays\public_uuids.db"
api_url = "https://api.wynncraft.com/v3/player/{uuid}?fullResult"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE character_raids ADD COLUMN delta_nest_of_the_grootslangs INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE character_raids ADD COLUMN delta_the_canyon_colossus INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE character_raids ADD COLUMN delta_orphions_nexus_of_light INTEGER DEFAULT 0")
    cursor.execute("ALTER TABLE character_raids ADD COLUMN delta_the_nameless_anomaly INTEGER DEFAULT 0")
    conn.commit()
    print("Added missing columns to character_raids table.")
except sqlite3.OperationalError as e:
    print(f"Columns may already exist: {e}")
cursor.execute("""
CREATE TABLE IF NOT EXISTS character_raids (
    character_uuid TEXT PRIMARY KEY,
    primary_uuid TEXT NOT NULL,
    nest_of_the_grootslangs INTEGER DEFAULT 0,
    the_canyon_colossus INTEGER DEFAULT 0,
    orphions_nexus_of_light INTEGER DEFAULT 0,
    the_nameless_anomaly INTEGER DEFAULT 0,
    delta_nest_of_the_grootslangs INTEGER DEFAULT 0,
    delta_the_canyon_colossus INTEGER DEFAULT 0,
    delta_orphions_nexus_of_light INTEGER DEFAULT 0,
    delta_the_nameless_anomaly INTEGER DEFAULT 0
)
""")
conn.commit()
cursor.execute("SELECT uuid FROM public_uuids")
public_uuids = [row[0] for row in cursor.fetchall()]

for primary_uuid in public_uuids:
    response = requests.get(api_url.format(uuid=primary_uuid))
    if response.status_code != 200:
        print(f"Failed to fetch data for UUID: {primary_uuid}. Status code: {response.status_code}")
        continue
    data = response.json()
    characters = data.get("characters", {})
    for char_uuid, char_data in characters.items():
        raids = char_data.get("raids", {}).get("list", {})
        nest_of_the_grootslangs = raids.get("Nest of the Grootslangs", 0)
        the_canyon_colossus = raids.get("The Canyon Colossus", 0)
        orphions_nexus_of_light = raids.get("Orphion's Nexus of Light", 0)
        the_nameless_anomaly = raids.get("The Nameless Anomaly", 0)

        cursor.execute("""
        SELECT nest_of_the_grootslangs, the_canyon_colossus, orphions_nexus_of_light, the_nameless_anomaly
        FROM character_raids
        WHERE character_uuid = ?
        """, (char_uuid,))
        row = cursor.fetchone()

        if row:
            prev_nest, prev_canyon, prev_orphion, prev_nameless = row
        else:
            prev_nest = prev_canyon = prev_orphion = prev_nameless = 0

        delta_nest = nest_of_the_grootslangs - prev_nest
        delta_canyon = the_canyon_colossus - prev_canyon
        delta_orphion = orphions_nexus_of_light - prev_orphion
        delta_nameless = the_nameless_anomaly - prev_nameless

        try:
            cursor.execute("""
            INSERT OR REPLACE INTO character_raids (
                character_uuid,
                primary_uuid,
                nest_of_the_grootslangs,
                the_canyon_colossus,
                orphions_nexus_of_light,
                the_nameless_anomaly,
                delta_nest_of_the_grootslangs,
                delta_the_canyon_colossus,
                delta_orphions_nexus_of_light,
                delta_the_nameless_anomaly
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                char_uuid,
                primary_uuid,
                nest_of_the_grootslangs,
                the_canyon_colossus,
                orphions_nexus_of_light,
                the_nameless_anomaly,
                delta_nest,
                delta_canyon,
                delta_orphion,
                delta_nameless
            ))
            conn.commit()
            print(f"Processed character {char_uuid} (Primary UUID: {primary_uuid}).")
        except sqlite3.Error as e:
            print(f"Error processing character {char_uuid}: {e}")

conn.close()
print("Raid counts processing complete.")