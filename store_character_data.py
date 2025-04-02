import sqlite3
import requests
from datetime import datetime
import time

db_path = r"c:\Users\Student\Desktop\wynn programs\raiddays\public_uuids.db"
character_api_url = "https://api.wynncraft.com/v3/player/{primary_uuid}/characters/{character_uuid}"
abilities_api_url = "https://api.wynncraft.com/v3/player/{primary_uuid}/characters/{character_uuid}/abilities"
archetype_nodes = {
    "helicopter": "Boltslinger",  # archer
    "manaTrap": "Trapper",        # archer
    "concentration": "Sharpshooter",  # archer
    "nightcloakKnives": "Shadestepper",  # assassin
    "darkArts": "Trickster",      # assassin
    "lacerate": "Acrobat",        # assassin
    "timeDilation": "Riftwalker",  # mage
    "ophanim": "Lightbender",     # mage
    "arcaneTransfer": "Arcanist",  # mage
    "jungleSlayer": "Summoner",   # shaman
    "maskOfTheAwakened": "Ritualist",  # shaman
    "bloodPool": "Acolyte",       # shaman
    "betterEnragedBlow": "Fallen",  # warrior
    "roundabout": "Battle Monk",  # warrior
    "heavenlyTrumpet": "Paladin"  # warrior
}

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS character_data (
    character_uuid TEXT PRIMARY KEY,
    primary_uuid TEXT NOT NULL,
    strength INTEGER,
    dexterity INTEGER,
    intelligence INTEGER,
    defense INTEGER,
    agility INTEGER,
    archetype TEXT,
    delta_nest_of_the_grootslangs INTEGER,
    delta_the_canyon_colossus INTEGER,
    delta_orphions_nexus_of_light INTEGER,
    delta_the_nameless_anomaly INTEGER,
    class_type TEXT,
    timestamp TEXT
)
""")
conn.commit()

cursor.execute("""
SELECT character_uuid, primary_uuid,
       delta_nest_of_the_grootslangs,
       delta_the_canyon_colossus,
       delta_orphions_nexus_of_light,
       delta_the_nameless_anomaly
FROM character_raids
WHERE delta_nest_of_the_grootslangs != 0
   OR delta_the_canyon_colossus != 0
   OR delta_orphions_nexus_of_light != 0
   OR delta_the_nameless_anomaly != 0
""")
changed_characters = cursor.fetchall()

request_count = 0
rate_limit = 100

for character_uuid, primary_uuid, delta_nest, delta_canyon, delta_orphion, delta_nameless in changed_characters:
    if request_count >= rate_limit:
        print("Rate limit reached. Sleeping for 60 seconds...")
        time.sleep(60)
        request_count = 0

    response = requests.get(character_api_url.format(primary_uuid=primary_uuid, character_uuid=character_uuid))
    request_count += 1
    if response.status_code != 200:
        print(f"Failed to fetch skill points for character {character_uuid}. Status code: {response.status_code}")
        continue

    character_data = response.json()
    skill_points = character_data.get("skillPoints", {})
    strength = skill_points.get("strength", 0)
    dexterity = skill_points.get("dexterity", 0)
    intelligence = skill_points.get("intelligence", 0)
    defense = skill_points.get("defense", 0)
    agility = skill_points.get("agility", 0)
    class_type = character_data.get("type", "Unknown")


    response = requests.get(abilities_api_url.format(primary_uuid=primary_uuid, character_uuid=character_uuid))
    request_count += 1 
    if response.status_code != 200:
        print(f"Failed to fetch abilities for character {character_uuid}. Status code: {response.status_code}")
        continue

    abilities_data = response.json()
    archetype = "N/A"

    if isinstance(abilities_data, list):
        for ability in abilities_data:
            if ability.get("type") == "ability":
                ability_id = ability.get("id")
                if ability_id in archetype_nodes:
                    archetype = archetype_nodes[ability_id]
                    break
                family = ability.get("family", [])
                for family_id in family:
                    if family_id in archetype_nodes:
                        archetype = archetype_nodes[family_id]
                        break
    else:
        print(f"Unexpected abilities data format for character {character_uuid}: {abilities_data}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        cursor.execute("""
        INSERT OR REPLACE INTO character_data (
            character_uuid,
            primary_uuid,
            strength,
            dexterity,
            intelligence,
            defense,
            agility,
            archetype,
            delta_nest_of_the_grootslangs,
            delta_the_canyon_colossus,
            delta_orphions_nexus_of_light,
            delta_the_nameless_anomaly,
            class_type,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            character_uuid,
            primary_uuid,
            strength,
            dexterity,
            intelligence,
            defense,
            agility,
            archetype,
            delta_nest,
            delta_canyon,
            delta_orphion,
            delta_nameless,
            class_type,
            timestamp
        ))
        conn.commit()
        print(f"Stored data for character {character_uuid} (Primary UUID: {primary_uuid}).")
    except sqlite3.Error as e:
        print(f"Error storing data for character {character_uuid}: {e}")

conn.close()
print("Character data processing complete.")