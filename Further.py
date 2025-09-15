import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime

db_path = r"c:\Users\Student\Desktop\wynn programs\raiddays\public_uuids.db"
reskin_mapping = {
    "HUNTER": "ARCHER",
    "KNIGHT": "WARRIOR",
    "DARKWIZARD": "MAGE",
    "NINJA": "ASSASSIN",
    "SKYSEER": "SHAMAN"
}
patches = {
    "2.1.X": "2025-04-18",
    "2.1.1": "2025-05-02",
    "2.1.2": "2025-05-16"
}
archetype_colors = {
    "Boltslinger": "#ffcc00", #archer
    "Trapper": "#006400",    #archer  
    "Sharpshooter": "#ff00ff",#archer
    "Riftwalker": "#add8e6",#mage
    "Lightbender": "#808080",  #mage
    "Arcanist": "#8a2be2",     #mage
    "Shadestepper": "#000000", #assassin
    "Trickster": "#4b0082",    #assassin
    "Acrobat": "#c0c0c0",      #assassin
    "Fallen": "#ff0000",       #warrior
    "Battle Monk": "#f1fd8d", #warrior
    "Paladin": "#00008b",      #warrior
    "Summoner": "#ffa500",     #shaman
    "Ritualist": "#90ee90",    #shaman
    "Acolyte": "#ff4500",     #shaman
    "N/A": "#c7c7c7" 
}
raids = [
    "delta_nest_of_the_grootslangs",
    "delta_the_canyon_colossus",
    "delta_orphions_nexus_of_light",
    "delta_the_nameless_anomaly"
]
raid_label_mapping = {
    "delta_nest_of_the_grootslangs": "g_Nest of the Grootslangs",
    "delta_the_canyon_colossus": "g_The Canyon Colossus",
    "delta_orphions_nexus_of_light": "g_Orphion's Nexus of Light",
    "delta_the_nameless_anomaly": "g_The Nameless Anomaly"
}
raid_shorthand_mapping = {
    "nol": "delta_orphions_nexus_of_light",
    "notg": "delta_nest_of_the_grootslangs",
    "tna": "delta_the_nameless_anomaly",
    "tcc": "delta_the_canyon_colossus"
}
skill_colors = {
    "avg_strength": "#00aa00",
    "avg_dexterity": "#ffa500",
    "avg_defense": "#FF5555",
    "avg_intelligence": "#3c789e",
    "avg_agility": "#80a7ab"
}

class_archetypes = {
    "archer": ["Boltslinger", "Trapper", "Sharpshooter"],
    "mage": ["Riftwalker", "Lightbender", "Arcanist"],
    "assassin": ["Shadestepper", "Trickster", "Acrobat"],
    "warrior": ["Fallen", "Battle Monk", "Paladin"],
    "shaman": ["Summoner", "Ritualist", "Acolyte"]
}

mythic_colors = {
    #Mage
    "Monster": "#B41F1F",      
    "Warp": "#776B8E",         
    "Gaia": "#326028",         
    "Fatal": "#C5B012", 
    "Lament": "#4682B4", 
    "Trance": "#EC674F",
    "Singularity": "#DA70D6",  
    
    #Archer
    "Ignis": "#B41F1F",
    "Strati": "#776B8E",
    "Grandmother": "#326028",
    "Divzer": "#C5B012",
    "Spring": "#4682B4",
    "Laby": "#B3EC37",
    "Freedom": "#DA70D6",
    "Epoch": "#B78103",

    #Assassin
    "Inferno": "#B41F1F",
    "Weathered": "#776B8E",
    "Grimtrap": "#326028",
    "Cataclysm": "#C5B012",
    "Nirvana": "#4682B4",
    "Nullification": "#DA70D6",
    "Oblivion": "#5A5AE9",
    "Hana": "#FF2E97",

    #Warrior
    "Guardian": "#B41F1F",
    "Hero": "#776B8E",
    "Alka": "#326028",
    "Tcrack": "#C5B012",
    "Idol": "#4682B4",
    "Collapse": "#DA70D6",
    "Convergence": "#483D8B",
    "Apoc": "#800000",
    "Bloodbath": "#75E74F",

    #Shaman
    "Absolution": "#B41F1F",
    "Olympic": "#776B8E",
    "Toxo": "#326028",
    "Sunstar": "#C5B012",
    "Hadal": "#4682B4",
    "Fantasia": "#DA70D6",
    "Reso": "#51E64A",
    "Aftershock": "#325B06",
    "Immolation": "#D1667B",


    "N/A": "#808080"
}

mythic_guess_patterns = {
    "mage": {
        "Monster": [
            {"stat": "defense", "min": 75},
            {"stat": "dexterity", "max": 40}
        ],
        "Warp": [
            {"stat": "agility", "min": 65},
            {"stat": "defense", "max": 20}
        ],
        "Gaia": [
            {"stat": "strength", "min": 80}
        ],
        "Fatal": [
            {"stat": "dexterity", "min": 80},
            {"stat": "defense", "min": 20}
        ],
        "Lament": [
            {"stat": "intelligence", "min": 70},
            {"stat": "dexterity", "max": 60},
            {"stat": "defense", "max": 50},
            {"stat": "agility", "max": 50}
        ],
        "Trance": [
            {"stat": "defense", "min": 60},
            {"stat": "dexterity", "min": 40}
        ],
        "Singularity": [
            {"stat": "intelligence", "min": 40},
            {"stat": "defense", "min": 30},
            {"stat": "dexterity", "min": 30},
            {"stat": "agility", "min": 30}
        ]
    },
    "archer": {
        "Ignis": [
            {"stat": "defense", "min": 80}
        ],
        "Strati": [
            {"stat": "agility", "min": 80}
        ],
        "Grandmother": [
            {"stat": "strength", "min": 80},
            {"stat": "defense", "max": 60}
        ],
        "Divzer": [
            {"stat": "dexterity", "min": 80},
            {"stat": "agility", "max": 10},
            {"stat": "defense", "max": 50}
        ],
        "Spring": [
            {"stat": "intelligence", "min": 75},
            {"stat": "dexterity", "max": 10}
        ],
        "Laby": [
            {"stat": "strength", "min": 60},
            {"stat": "defense", "min": 60}
        ],
        "Freedom": [
            {"stat": "strength", "min": 40},
            {"stat": "defense", "min": 30},
            {"stat": "agility", "min": 30},
            {"stat": "intelligence", "min": 30}
        ],
        "Epoch": [
            {"stat": "agility", "min": 40},
            {"stat": "dexterity", "min": 60},
            {"stat": "strength", "min": 40}
        ]
    },
    "assassin": {
        "Inferno": [
            {"stat": "defense", "min": 80}
        ],
        "Weathered": [
            {"stat": "agility", "min": 80}
        ],
        "Grimtrap": [
            {"stat": "strength", "min": 80},
            {"stat": "dexterity", "max": 79}
        ],
        "Cataclysm": [
            {"stat": "dexterity", "min": 80},
            {"stat": "strength", "max": 79}
        ],
        "Nirvana": [
            {"stat": "intelligence", "min": 80},
            {"stat": "dexterity", "max": 50},
            {"stat": "strength", "max": 50}
        ],
        "Nullification": [
            {"stat": "strength", "min": 40},
            {"stat": "agility", "min": 30},
            {"stat": "intelligence", "min": 30}
        ],
        "Oblivion": [
            {"stat": "dexterity", "min": 55},
            {"stat": "intelligence", "min": 55},
            {"stat": "dexterity", "max": 85},
            {"stat": "strength", "max": 50}
        ],
        "Hana": [
            {"stat": "agility", "min": 60},
            {"stat": "dexterity", "max": 60},
            {"stat": "intelligence", "min": 60}
        ]
    },
    "warrior": {
        "Guardian": [
            {"stat": "strength", "max": 60},
            {"stat": "defense", "min": 75},
            {"stat": "intelligence", "max": 60}
        ],
        "Hero": [
            {"stat": "agility", "min": 60},
            {"stat": "defense", "max": 40},
            {"stat": "dexterity", "max": 70}
        ],
        "Alka": [
            {"stat": "strength", "min": 85}
        ],
        "Tcrack": [
            {"stat": "dexterity", "min": 70},
            {"stat": "defense", "max": 50},
            {"stat": "intelligence", "max": 80}
        ],
        "Idol": [
            {"stat": "intelligence", "min": 85},
            {"stat": "agility", "max": 45}
        ],
        "Collapse": [
            {"stat": "defense", "min": 30},
            {"stat": "agility", "min": 30},
            {"stat": "intelligence", "min": 40},
            {"stat": "strength", "min": 30}
        ],
        "Convergence": [
            {"stat": "intelligence", "min": 65},
            {"stat": "defense", "min": 65},
            {"stat": "dexterity", "max": 20}
        ],
        "Apoc": [
            {"stat": "defense", "min": 60},
            {"stat": "strength", "min": 40},
            {"stat": "intelligence", "max": 20},
            {"stat": "defense", "max": 80}
        ],
        "Bloodbath": [
            {"stat": "strength", "min": 75},
            {"stat": "dexterity", "min": 75},
            {"stat": "agility", "max": 30}
        ]
    },
    "shaman": {
        "Absolution": [
            {"stat": "defense", "min": 75},
            {"stat": "agility", "max": 70}
        ],
        "Olympic": [
            {"stat": "agility", "min": 80},
            {"stat": "defense", "max": 40}
        ],
        "Toxo": [
            {"stat": "strength", "min": 85},
            {"stat": "intelligence", "max": 20}
        ],
        "Sunstar": [
            {"stat": "defense", "max": 60},
            {"stat": "dexterity", "min": 80}
        ],
        "Hadal": [
            {"stat": "defense", "max": 40},
            {"stat": "intelligence", "min": 80}
        ],
        "Fantasia": [
            {"stat": "strength", "min": 40},
            {"stat": "defense", "min": 30},
            {"stat": "agility", "min": 30},
            {"stat": "intelligence", "min": 30}
        ],
        "Reso": [
            {"stat": "strength", "min": 60},
            {"stat": "intelligence", "min": 60},
            {"stat": "defense", "max": 40}
        ],
        "Aftershock": [
            {"stat": "strength", "min": 70},
            {"stat": "agility", "min": 30},
            {"stat": "intelligence", "max": 5}
        ],
        "Immolation": [
            {"stat": "defense", "min": 70},
            {"stat": "agility", "min": 70}
        ]
    }
}

def analyze_skillpoints(archetype, tolerance, start_date=None, end_date=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if start_date and end_date:
        cursor.execute("""
        SELECT strength, dexterity, intelligence, defense, agility
        FROM character_data
        WHERE LOWER(archetype) = ? AND DATE(timestamp) BETWEEN ? AND ?
        """, (archetype.lower(), start_date, end_date))
        print(f"\nAnalyzing skillpoints for '{archetype}' between {start_date} and {end_date}")
    else:
        cursor.execute("""
        SELECT strength, dexterity, intelligence, defense, agility
        FROM character_data
        WHERE LOWER(archetype) = ?
        """, (archetype.lower(),))
        print(f"\nAnalyzing all-time skillpoints for '{archetype}'")
    
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No data found for archetype '{archetype}' in the specified timeframe.")
        return

    df = pd.DataFrame(rows, columns=["strength", "dexterity", "intelligence", "defense", "agility"])

    grouped = df.groupby(["strength", "dexterity", "intelligence", "defense", "agility"]).size().reset_index(name="count")
    grouped = grouped.sort_values(by="count", ascending=False)

    filtered = grouped[
        (grouped["strength"].between(grouped["strength"].min() - tolerance, grouped["strength"].max() + tolerance)) &
        (grouped["dexterity"].between(grouped["dexterity"].min() - tolerance, grouped["dexterity"].max() + tolerance)) &
        (grouped["intelligence"].between(grouped["intelligence"].min() - tolerance, grouped["intelligence"].max() + tolerance)) &
        (grouped["defense"].between(grouped["defense"].min() - tolerance, grouped["defense"].max() + tolerance)) &
        (grouped["agility"].between(grouped["agility"].min() - tolerance, grouped["agility"].max() + tolerance))
    ]

    print(f"Most Common Skillpoint Configurations for Archetype '{archetype}' (±{tolerance}):")
    print(filtered.head(10))

def plot_patch_intercepts(ax, patches):
    for patch, date_str in patches.items():
        date = pd.to_datetime(date_str)
        ax.axvline(date, color='red', linestyle='--', alpha=0.7)
        ax.text(date, ax.get_ylim()[1], patch, rotation=90, verticalalignment='bottom', color='red', fontsize=8)

def graph_archetype_overtime(archetype, raid, start_date, end_date, show_patches=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if raid == "all":
        raid_columns = " + ".join(raids)
        cursor.execute(f"""
        SELECT DATE(timestamp) as date, COUNT(*) as total_count,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count
        FROM character_data
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (archetype.lower(), start_date, end_date))
    else:
        cursor.execute(f"""
        SELECT DATE(timestamp) as date, COUNT(*) as total_count,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count
        FROM character_data
        WHERE {raid} > 0 AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (archetype.lower(), start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["date", "total_count", "archetype_count"])
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d") 
    if df.empty:
        print(f"No data found for archetype '{archetype}' and raid '{raid}' in the given timeframe.")
        return
    df["usage_share_percentage"] = (df["archetype_count"] / df["total_count"]) * 100
    plt.figure(figsize=(12, 6))
    ax = plt.gca()
    plt.plot(df["date"], df["usage_share_percentage"], label=f"{archetype} ({raid})", color=archetype_colors.get(archetype, "#c7c7c7"))
    if show_patches:
        plot_patch_intercepts(ax, patches)
    plt.title(f"Overtime Usage Share% for Archetype '{archetype}' ({raid_label_mapping.get(raid, 'All Raids')})")
    plt.xlabel("Date")
    plt.ylabel("Usage Share (%)")
    plt.legend(title="Archetype")
    plt.tight_layout()
    plt.show()

def graph_average_skillpoints_overtime(entity_type, entity_name, start_date, end_date):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if entity_type.lower() == "class":
        cursor.execute(f"""
        SELECT DATE(timestamp) as date,
               AVG(strength) as avg_strength,
               AVG(dexterity) as avg_dexterity,
               AVG(intelligence) as avg_intelligence,
               AVG(defense) as avg_defense,
               AVG(agility) as avg_agility
        FROM character_data
        WHERE LOWER(class_type) = ?
          AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (entity_name.lower(), start_date, end_date))
    elif entity_type.lower() == "archetype":
        cursor.execute(f"""
        SELECT DATE(timestamp) as date,
               AVG(strength) as avg_strength,
               AVG(dexterity) as avg_dexterity,
               AVG(intelligence) as avg_intelligence,
               AVG(defense) as avg_defense,
               AVG(agility) as avg_agility
        FROM character_data
        WHERE LOWER(archetype) = ?
          AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (entity_name.lower(), start_date, end_date))
    else:
        print("Invalid entity type. Please specify 'class' or 'archetype'.")
        conn.close()
        return

    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["date", "avg_strength", "avg_dexterity", "avg_intelligence", "avg_defense", "avg_agility"])
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    if df.empty:
        print(f"No data found for {entity_type} '{entity_name}' in the given timeframe.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(df["date"], df["avg_strength"], label="Strength", color=skill_colors["avg_strength"])
    plt.plot(df["date"], df["avg_dexterity"], label="Dexterity", color=skill_colors["avg_dexterity"])
    plt.plot(df["date"], df["avg_intelligence"], label="Intelligence", color=skill_colors["avg_intelligence"])
    plt.plot(df["date"], df["avg_defense"], label="Defense", color=skill_colors["avg_defense"])
    plt.plot(df["date"], df["avg_agility"], label="Agility", color=skill_colors["avg_agility"])
    plt.title(f"Average Skillpoints Overtime for {entity_type.capitalize()} '{entity_name}'")
    plt.xlabel("Date")
    plt.ylabel("Average Skillpoints")
    plt.legend(title="Skillpoints")
    plt.tight_layout()
    plt.show()

def print_character_uuids_for_archetype(archetype, date):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT primary_uuid, character_uuid
    FROM character_data
    WHERE LOWER(archetype) = ? AND DATE(timestamp) = ?
    """, (archetype.lower(), date))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print(f"No characters found for archetype '{archetype}' on {date}.")
        return
    print(f"Characters for Archetype '{archetype}' on {date}:")
    for primary_uuid, character_uuid in rows:
        print(f"Primary UUID: {primary_uuid}, Character UUID: {character_uuid}")

def graph_class_archetype_share_overtime(class_name, raid, start_date, end_date, show_patches=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    archetypes = get_archetypes_for_class(class_name)
    if not archetypes:
        print(f"Invalid class name '{class_name}'. Please choose from: Archer, Mage, Assassin, Warrior, Shaman.")
        return
    if raid == "all":
        cursor.execute(f"""
        SELECT DATE(timestamp) as date,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count_2,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count_3,
               COUNT(*) as total_class_count
        FROM character_data
        WHERE LOWER(class_type) = ?
          AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (archetypes[0].lower(), archetypes[1].lower(), archetypes[2].lower(), class_name.lower(), start_date, end_date))
    else:
        cursor.execute(f"""
        SELECT DATE(timestamp) as date,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count_2,
               SUM(CASE WHEN LOWER(archetype) = ? THEN 1 ELSE 0 END) as archetype_count_3,
               COUNT(*) as total_class_count
        FROM character_data
        WHERE {raid} > 0
          AND LOWER(class_type) = ?
          AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (archetypes[0].lower(), archetypes[1].lower(), archetypes[2].lower(), class_name.lower(), start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["date", "archetype_1", "archetype_2", "archetype_3", "total_class_count"])
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    if df.empty:
        print(f"No data found for class '{class_name}' and raid '{raid}' in the given timeframe.")
        return

    df["archetype_1_share"] = (df["archetype_1"] / df["total_class_count"]) * 100
    df["archetype_2_share"] = (df["archetype_2"] / df["total_class_count"]) * 100
    df["archetype_3_share"] = (df["archetype_3"] / df["total_class_count"]) * 100
    total_users_query = f"""
    SELECT DATE(timestamp) as date, COUNT(*) as total_users
    FROM character_data
    WHERE DATE(timestamp) BETWEEN ? AND ?
    GROUP BY date
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(total_users_query, (start_date, end_date))
    total_users_rows = cursor.fetchall()
    conn.close()

    total_users_df = pd.DataFrame(total_users_rows, columns=["date", "total_users"])
    total_users_df["date"] = pd.to_datetime(total_users_df["date"], format="%Y-%m-%d")

    df = pd.merge(df, total_users_df, on="date", how="left")
    df["class_usage_percentage"] = (df["total_class_count"] / df["total_users"]) * 100

    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(df["date"], df["archetype_1_share"], label=f"{archetypes[0]} Share", color=archetype_colors.get(archetypes[0], "#c7c7c7"))
    ax1.plot(df["date"], df["archetype_2_share"], label=f"{archetypes[1]} Share", color=archetype_colors.get(archetypes[1], "#c7c7c7"))
    ax1.plot(df["date"], df["archetype_3_share"], label=f"{archetypes[2]} Share", color=archetype_colors.get(archetypes[2], "#c7c7c7"))
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Archetype Share (%)")
    ax1.legend(loc="upper left")
    ax2 = ax1.twinx()
    ax2.plot(df["date"], df["class_usage_percentage"], label=f"{class_name} Usage %", color="#000000", linestyle="--")
    ax2.set_ylabel("Class Usage (%)")
    ax2.legend(loc="upper right")

    if show_patches:
        plot_patch_intercepts(ax1, patches)

    plt.title(f"Archetype Share and {class_name} Usage Overtime ({raid_label_mapping.get(raid, 'All Raids')})")
    plt.tight_layout()
    plt.show()

def graph_class_usage_share_overtime(raid, start_date, end_date):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    classes = list(set(reskin_mapping.values()))  
    class_reskin_mapping = {v.lower(): k.lower() for k, v in reskin_mapping.items()}
    if raid == "all":
        cursor.execute(f"""
        SELECT DATE(timestamp) as date,
               SUM(CASE WHEN LOWER(class_type) = 'archer' OR LOWER(class_type) = 'hunter' THEN 1 ELSE 0 END) as archer_count,
               SUM(CASE WHEN LOWER(class_type) = 'warrior' OR LOWER(class_type) = 'knight' THEN 1 ELSE 0 END) as warrior_count,
               SUM(CASE WHEN LOWER(class_type) = 'mage' OR LOWER(class_type) = 'darkwizard' THEN 1 ELSE 0 END) as mage_count,
               SUM(CASE WHEN LOWER(class_type) = 'assassin' OR LOWER(class_type) = 'ninja' THEN 1 ELSE 0 END) as assassin_count,
               SUM(CASE WHEN LOWER(class_type) = 'shaman' OR LOWER(class_type) = 'skyseer' THEN 1 ELSE 0 END) as shaman_count,
               COUNT(*) as total_count
        FROM character_data
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (start_date, end_date))
    else:
        cursor.execute(f"""
        SELECT DATE(timestamp) as date,
               SUM(CASE WHEN LOWER(class_type) = 'archer' OR LOWER(class_type) = 'hunter' THEN 1 ELSE 0 END) as archer_count,
               SUM(CASE WHEN LOWER(class_type) = 'warrior' OR LOWER(class_type) = 'knight' THEN 1 ELSE 0 END) as warrior_count,
               SUM(CASE WHEN LOWER(class_type) = 'mage' OR LOWER(class_type) = 'darkwizard' THEN 1 ELSE 0 END) as mage_count,
               SUM(CASE WHEN LOWER(class_type) = 'assassin' OR LOWER(class_type) = 'ninja' THEN 1 ELSE 0 END) as assassin_count,
               SUM(CASE WHEN LOWER(class_type) = 'shaman' OR LOWER(class_type) = 'skyseer' THEN 1 ELSE 0 END) as shaman_count,
               COUNT(*) as total_count
        FROM character_data
        WHERE {raid} > 0
          AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        """, (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(rows, columns=["date", "archer", "warrior", "mage", "assassin", "shaman", "total_count"])
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    if df.empty:
        print(f"No data found for raid '{raid}' in the given timeframe.")
        return
    for class_name in ["archer", "warrior", "mage", "assassin", "shaman"]:
        df[f"{class_name}_share"] = (df[class_name] / df["total_count"]) * 100

    plt.figure(figsize=(12, 6))
    plt.plot(df["date"], df["archer_share"], label="Archer (Hunter)", color="#ffcc00")
    plt.plot(df["date"], df["warrior_share"], label="Warrior (Knight)", color="#ff0000")
    plt.plot(df["date"], df["mage_share"], label="Mage (Dark Wizard)", color="#add8e6")
    plt.plot(df["date"], df["assassin_share"], label="Assassin (Ninja)", color="#000000")
    plt.plot(df["date"], df["shaman_share"], label="Shaman (Skyseer)", color="#ffa500")
    plt.title(f"Class Usage Share Overtime ({raid_label_mapping.get(raid, 'All Raids')})")
    plt.xlabel("Date")
    plt.ylabel("Usage Share (%)")
    plt.legend(title="Class")
    plt.tight_layout()
    plt.show()

def graph_archetype_share_pie_chart(raid, start_date, end_date):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if raid == "all":
        cursor.execute(f"""
        SELECT LOWER(archetype) as archetype, COUNT(*) as archetype_count
        FROM character_data
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY LOWER(archetype)
        """, (start_date, end_date))
    else:
        cursor.execute(f"""
        SELECT LOWER(archetype) as archetype, COUNT(*) as archetype_count
        FROM character_data
        WHERE {raid} > 0 AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY LOWER(archetype)
        """, (start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No data found for raid '{raid}' in the given timeframe.")
        return
    rows = [row for row in rows if row[0] != "n/a"]
    if not rows:
        print(f"No valid archetype data found for raid '{raid}' in the given timeframe.")
        return
    archetypes = [row[0].capitalize() for row in rows]
    counts = [row[1] for row in rows]
    colors = [archetype_colors.get(arch.capitalize(), "#c7c7c7") for arch in archetypes]

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=archetypes, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title(f"Archetype Share Percentage ({raid_label_mapping.get(raid, 'All Raids')})\n{start_date} to {end_date}")
    plt.tight_layout()
    plt.show()

def create_archetype_infographic(raid, start_date_1, end_date_1, start_date_2, end_date_2):
    def get_archetype_data(raid, start_date, end_date):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        if raid == "all":
            cursor.execute(f"""
            SELECT LOWER(archetype) as archetype, COUNT(*) as archetype_count
            FROM character_data
            WHERE DATE(timestamp) BETWEEN ? AND ?
            GROUP BY LOWER(archetype)
            """, (start_date, end_date))
        else:
            cursor.execute(f"""
            SELECT LOWER(archetype) as archetype, COUNT(*) as archetype_count
            FROM character_data
            WHERE {raid} > 0 AND DATE(timestamp) BETWEEN ? AND ?
            GROUP BY LOWER(archetype)
            """, (start_date, end_date))

        rows = cursor.fetchall()
        conn.close()

        rows = [row for row in rows if row[0] != "n/a"]

        total_count = sum(row[1] for row in rows)
        data = {row[0].capitalize(): (row[1] / total_count) * 100 for row in rows} if total_count > 0 else {}
        return data

    data_1 = get_archetype_data(raid, start_date_1, end_date_1)
    data_2 = get_archetype_data(raid, start_date_2, end_date_2)
    all_archetypes = set(data_1.keys()).union(data_2.keys())
    leaderboard_1 = sorted(data_1.items(), key=lambda x: x[1], reverse=True)
    leaderboard_2 = []
    usage_swings = []
    for archetype in all_archetypes:
        share_1 = data_1.get(archetype, 0)
        share_2 = data_2.get(archetype, 0)
        diff = share_2 - share_1
        arrow = "↑" if diff > 0 else "↓" if diff < 0 else "-"
        leaderboard_2.append((archetype, share_2, diff, arrow))
        usage_swings.append((archetype, diff))
    leaderboard_2 = sorted(leaderboard_2, key=lambda x: x[1], reverse=True)
    usage_swings = sorted(usage_swings, key=lambda x: x[1], reverse=True) 

    fig = plt.figure(figsize=(8.27, 11.69))  
    gs = GridSpec(6, 2, figure=fig, height_ratios=[2.5, 1.5, 1.5, 1, 1, 2.5])
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.pie(data_1.values(), labels=data_1.keys(), startangle=140,
            colors=[archetype_colors.get(arch, "#c7c7c7") for arch in data_1.keys()])
    ax1.set_title(f"({start_date_1} to {end_date_1})", fontsize=12)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.pie(data_2.values(), labels=data_2.keys(), startangle=140,
            colors=[archetype_colors.get(arch, "#c7c7c7") for arch in data_2.keys()])
    ax2.set_title(f"({start_date_2} to {end_date_2})", fontsize=12)
    ax3 = fig.add_subplot(gs[1:2, 0])
    ax3.axis("off")
    ax3.set_title("Leaderboard (Timeframe 1)", fontsize=10)
    for i, (archetype, share) in enumerate(leaderboard_1, start=1):
        ax3.text(0.5, 1 - i * 0.2, f"{i}. {archetype}: {share:.1f}%", fontsize=9, va="top", ha="center")
    ax4 = fig.add_subplot(gs[1:2, 1])
    ax4.axis("off")
    ax4.set_title("Leaderboard with Change (Timeframe 2)", fontsize=10)
    for i, (archetype, share, diff, arrow) in enumerate(leaderboard_2, start=1):
        color = "green" if arrow == "↑" else "red" if arrow == "↓" else "black"
        ax4.text(0.5, 1 - i * 0.2, f"{i}. {archetype}: {share:.1f}% ({arrow} {abs(diff):.1f}%)",
                 fontsize=9, va="top", ha="center", color=color)

    ax5 = fig.add_subplot(gs[5, :])
    archetypes = [item[0] for item in usage_swings]
    swings = [item[1] for item in usage_swings]
    bar_colors = ["green" if swing > 0 else "red" for swing in swings]
    ax5.bar(archetypes, swings, color=bar_colors)
    ax5.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax5.set_title("Usage Swing Between Timeframes", fontsize=12)
    ax5.set_ylabel("Percentage Swing (%)")
    ax5.set_xticks(range(len(archetypes)))
    ax5.set_xticklabels(archetypes, rotation=45, ha="right", fontsize=9)

    output_file = f"archetype_infographic_{start_date_1}_to_{end_date_2}.png"
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Infographic saved as {output_file}")

    plt.show()

def resolve_raid_input(raid_input):
    """
    Resolves the raid input to the full raid name if a shorthand is provided.
    """
    if raid_input.lower() in raid_shorthand_mapping:
        return raid_shorthand_mapping[raid_input.lower()]
    elif raid_input.lower() == "all":
        return "all"
    elif raid_input in raids:
        return raid_input
    else:
        print(f"Invalid raid input: '{raid_input}'. Please use 'all', a full raid name, or a shorthand (nol, notg, tna, tcc).")
        return None

def get_archetypes_for_class(class_name):
    """
    Derives archetypes for a given class based on the comments in the archetype_colors dictionary.
    """
    class_archetypes = {
        "archer": ["Boltslinger", "Trapper", "Sharpshooter"],
        "mage": ["Riftwalker", "Lightbender", "Arcanist"],
        "assassin": ["Shadestepper", "Trickster", "Acrobat"],
        "warrior": ["Fallen", "Battle Monk", "Paladin"],
        "shaman": ["Summoner", "Ritualist", "Acolyte"]
    }
    return class_archetypes.get(class_name.lower(), [])

def graph_all_archetype_shares_overtime(start_date, end_date, raid="all", moving_average=False, ma_window=3):
    """
    Plots the share of all archetypes over time for a specified raid or all raids.
    Parameters:
        start_date (str): Start date in 'YYYY-MM-DD'
        end_date (str): End date in 'YYYY-MM-DD'
        raid (str): Raid name or 'all'
        moving_average (bool): Whether to plot a moving average
        ma_window (int): Window size for moving average
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if raid == "all":
        cursor.execute(f"""
        SELECT DATE(timestamp) as date, LOWER(archetype) as archetype, COUNT(*) as count
        FROM character_data
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date, archetype
        """, (start_date, end_date))
    else:
        cursor.execute(f"""
        SELECT DATE(timestamp) as date, LOWER(archetype) as archetype, COUNT(*) as count
        FROM character_data
        WHERE {raid} > 0 AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date, archetype
        """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(f"No data found for raid '{raid}' in the given timeframe.")
        return

    df = pd.DataFrame(rows, columns=["date", "archetype", "count"])
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df = df[df["archetype"] != "n/a"]

    pivot = df.pivot(index="date", columns="archetype", values="count").fillna(0)
    total = pivot.sum(axis=1)
    share = pivot.divide(total, axis=0) * 100

    plt.figure(figsize=(14, 7))
    for archetype in share.columns:
        data = share[archetype]
        if moving_average:
            data = data.rolling(window=ma_window, min_periods=1).mean()
            label = f"{archetype.capitalize()} (MA{ma_window})"
        else:
            label = archetype.capitalize()
        plt.plot(share.index, data, label=label, color=archetype_colors.get(archetype.capitalize(), "#c7c7c7"))
    plt.title(f"Archetype Share Over Time ({raid_label_mapping.get(raid, 'All Raids')})")
    plt.xlabel("Date")
    plt.ylabel("Share (%)")
    plt.legend(title="Archetype", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

def plot_archetype_sp_band_usage():
    archetype = input("Enter the archetype to analyze: ").strip()
    bands = []
    while True:
        print("\nEnter lower and upper bounds for each skill point (inclusive):")
        lb = {}
        ub = {}
        for sp in ["strength", "dexterity", "intelligence", "defense", "agility"]:
            lb[sp] = int(input(f"  Lower bound for {sp}: "))
            ub[sp] = int(input(f"  Upper bound for {sp}: "))
        bands.append((lb, ub))
        more = input("Add another skill point band? (yes/no): ").strip().lower()
        if more != "yes":
            break
    start_date = input("Enter the start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter the end date (YYYY-MM-DD): ").strip()

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT class_type, archetype, strength, dexterity, intelligence, defense, agility, timestamp FROM character_data",
        conn
    )
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[(df["archetype"].str.lower() == archetype.lower())]
    df = df[(df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)]
    df["date"] = df["timestamp"].dt.date
    total_per_day = df.groupby("date").size()
    band_counts = []
    for lb, ub in bands:
        mask = (
            (df["strength"].between(lb["strength"], ub["strength"])) &
            (df["dexterity"].between(lb["dexterity"], ub["dexterity"])) &
            (df["intelligence"].between(lb["intelligence"], ub["intelligence"])) &
            (df["defense"].between(lb["defense"], ub["defense"])) &
            (df["agility"].between(lb["agility"], ub["agility"]))
        )
        band_counts.append(df[mask].groupby("date").size())

    all_band_mask = pd.Series(False, index=df.index)
    for lb, ub in bands:
        all_band_mask |= (
            (df["strength"].between(lb["strength"], ub["strength"])) &
            (df["dexterity"].between(lb["dexterity"], ub["dexterity"])) &
            (df["intelligence"].between(lb["intelligence"], ub["intelligence"])) &
            (df["defense"].between(lb["defense"], ub["defense"])) &
            (df["agility"].between(lb["agility"], ub["agility"]))
        )
    remainder_counts = df[~all_band_mask].groupby("date").size()

    conn = sqlite3.connect(db_path)
    all_df = pd.read_sql_query(
        "SELECT archetype, timestamp FROM character_data",
        conn
    )
    conn.close()
    all_df["timestamp"] = pd.to_datetime(all_df["timestamp"])
    all_df = all_df[(all_df["timestamp"] >= start_date) & (all_df["timestamp"] <= end_date)]
    all_df["date"] = all_df["timestamp"].dt.date
    total_entries_per_day = all_df.groupby("date").size()
    archetype_entries_per_day = all_df[all_df["archetype"].str.lower() == archetype.lower()].groupby("date").size()
    archetype_share = (archetype_entries_per_day / total_entries_per_day * 100).fillna(0)

    #plot
    import matplotlib.pyplot as plt
    fig, ax1 = plt.subplots(figsize=(12, 6))
    dates = sorted(set(total_per_day.index) | set(archetype_share.index))
    for i, band_count in enumerate(band_counts):
        percent = (band_count / total_per_day * 100).reindex(dates, fill_value=0)
        ax1.plot(dates, percent, label=f"Band {i+1} usage %")
    remainder_percent = (remainder_counts / total_per_day * 100).reindex(dates, fill_value=0)
    ax1.plot(dates, remainder_percent, label="Remainder usage %", linestyle="--", color="gray")
    ax1.set_ylabel(f"% of {archetype} entries per day")
    ax1.set_xlabel("Date")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(dates, archetype_share.reindex(dates, fill_value=0), label=f"{archetype} share of all", color="red", linestyle=":")
    ax2.set_ylabel(f"% share of {archetype} among all entries")
    ax2.legend(loc="upper right")

    plt.title(f"Skill Point Band Usage for {archetype} ({start_date} to {end_date})")
    plt.tight_layout()
    plt.show()

def analyze_raid_frequency():
    """
    Analyzes raid frequency and percentages based on user-specified criteria.
    Shows archetype breakdown with frequency and percentages.
    """
    print("\nRaid Frequency Analysis")
    print("1. All raids")
    print("2. Specified raid(s)")
    raid_choice = input("Select option (1/2): ").strip()
    
    selected_raids = []
    if raid_choice == "2":
        print("Available raids:")
        for i, raid in enumerate(raids, 1):
            print(f"  {i}. {raid_label_mapping[raid]}")
        print("Available shorthands: nol, notg, tna, tcc")
        raid_input = input("Enter raid name(s) or shorthand(s) separated by commas: ").strip()
        raid_names = [name.strip() for name in raid_input.split(",")]
        
        for raid_name in raid_names:
            resolved = resolve_raid_input(raid_name)
            if resolved and resolved != "all":
                selected_raids.append(resolved)
            elif raid_name.lower() in [r.lower() for r in raids]:
                selected_raids.append(raid_name.lower())
        
        if not selected_raids:
            print("No valid raids specified. Exiting.")
            return
    
    print("\n1. Single date")
    print("2. Date range")
    date_choice = input("Select option (1/2): ").strip()
    
    if date_choice == "1":
        date_str = input("Enter date (YYYY-MM-DD): ").strip()
        start_date = end_date = date_str
        is_range = False
    else:
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        end_date = input("Enter end date (YYYY-MM-DD): ").strip()
        is_range = True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if raid_choice == "1":
        cursor.execute("""
        SELECT DATE(timestamp) as date, LOWER(archetype) as archetype, COUNT(*) as count
        FROM character_data
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date, archetype
        ORDER BY date, archetype
        """, (start_date, end_date))
    else:
        raid_conditions = " OR ".join([f"{raid} > 0" for raid in selected_raids])
        if is_range:
            cursor.execute(f"""
            SELECT DATE(timestamp) as date, LOWER(archetype) as archetype, COUNT(*) as count
            FROM character_data
            WHERE ({raid_conditions}) AND DATE(timestamp) BETWEEN ? AND ?
            GROUP BY date, archetype
            ORDER BY date, archetype
            """, (start_date, end_date))
        else:
            cursor.execute(f"""
            SELECT DATE(timestamp) as date, LOWER(archetype) as archetype, COUNT(*) as count
            FROM character_data
            WHERE ({raid_conditions}) AND DATE(timestamp) = ?
            GROUP BY date, archetype
            ORDER BY archetype
            """, (start_date,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No data found for the specified criteria.")
        return
    
    print(f"\nRaid Frequency Analysis Results")
    if raid_choice == "1":
        print(f"Raids: All raids")
    else:
        raid_labels = [raid_label_mapping.get(raid, raid) for raid in selected_raids]
        print(f"Raids: {', '.join(raid_labels)}")
    
    print(f"Date range: {start_date} to {end_date}")
    print("-" * 60)
    
    if is_range and len(set(row[0] for row in rows)) > 1:
        df = pd.DataFrame(rows, columns=["date", "archetype", "count"])
        df = df[df["archetype"] != "n/a"] 
        
        print("Daily breakdown:")
        for date in sorted(df["date"].unique()):
            day_data = df[df["date"] == date]
            day_total = day_data["count"].sum()
            print(f"\n  {date} (Total: {day_total} entries):")
            
            for _, row in day_data.sort_values("count", ascending=False).iterrows():
                archetype = row["archetype"].capitalize()
                count = row["count"]
                percentage = (count / day_total) * 100
                print(f"    {archetype}: {count} ({percentage:.1f}%)")
        
        print(f"\nOverall Summary ({start_date} to {end_date}):")
        total_summary = df.groupby("archetype")["count"].sum().sort_values(ascending=False)
        grand_total = total_summary.sum()
        
        for archetype, count in total_summary.items():
            percentage = (count / grand_total) * 100
            avg_per_day = count / len(df["date"].unique())
            print(f"  {archetype.capitalize()}: {count} total ({percentage:.1f}%, avg {avg_per_day:.1f}/day)")
        
        print(f"\nGrand Total: {grand_total} entries across {len(df['date'].unique())} days")
        print(f"Average per day: {grand_total / len(df['date'].unique()):.1f}")
        
    else:
        df = pd.DataFrame(rows, columns=["date", "archetype", "count"])
        df = df[df["archetype"] != "n/a"] 
        
        if not df.empty:
            date = df["date"].iloc[0]
            total_count = df["count"].sum()
            
            print(f"Date: {date}")
            print(f"Total entries: {total_count}")
            print("\nArchetype breakdown:")
            
            for _, row in df.sort_values("count", ascending=False).iterrows():
                archetype = row["archetype"].capitalize()
                count = row["count"]
                percentage = (count / total_count) * 100
                print(f"  {archetype}: {count} ({percentage:.1f}%)")
        else:
            print("No valid archetype data found for the specified criteria.")

def count_datapoints_between_dates():
    """
    Counts the number of datapoints between two specified dates.
    """
    print("\nDatapoint Count Analysis")
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    print("\n1. All raids")
    print("2. Specified raid(s)")
    raid_choice = input("Select option (1/2): ").strip()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if raid_choice == "1":
        cursor.execute("""
        SELECT COUNT(*) as total_count
        FROM character_data
        WHERE DATE(timestamp) BETWEEN ? AND ?
        """, (start_date, end_date))
        
        total_result = cursor.fetchone()
        
        cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as daily_count
        FROM character_data
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """, (start_date, end_date))
        
        daily_results = cursor.fetchall()
    else:
        print("Available raids:")
        for i, raid in enumerate(raids, 1):
            print(f"  {i}. {raid_label_mapping[raid]}")
        print("Available shorthands: nol, notg, tna, tcc")
        raid_input = input("Enter raid name(s) or shorthand(s) separated by commas: ").strip()
        raid_names = [name.strip() for name in raid_input.split(",")]
        
        selected_raids = []
        for raid_name in raid_names:
            resolved = resolve_raid_input(raid_name)
            if resolved and resolved != "all":
                selected_raids.append(resolved)
            elif raid_name.lower() in [r.lower() for r in raids]:
                selected_raids.append(raid_name.lower())
        
        if not selected_raids:
            print("No valid raids specified. Exiting.")
            conn.close()
            return
        
        raid_conditions = " OR ".join([f"{raid} > 0" for raid in selected_raids])
        
        cursor.execute(f"""
        SELECT COUNT(*) as total_count
        FROM character_data
        WHERE ({raid_conditions}) AND DATE(timestamp) BETWEEN ? AND ?
        """, (start_date, end_date))
        
        total_result = cursor.fetchone()
        
        cursor.execute(f"""
        SELECT DATE(timestamp) as date, COUNT(*) as daily_count
        FROM character_data
        WHERE ({raid_conditions}) AND DATE(timestamp) BETWEEN ? AND ?
        GROUP BY date
        ORDER BY date
        """, (start_date, end_date))
        
        daily_results = cursor.fetchall()
    
    conn.close()
    
    total_count = int(total_result[0]) if total_result and total_result[0] is not None else 0
    
    print(f"\nDatapoint Count Results")
    print(f"Date range: {start_date} to {end_date}")
    if raid_choice == "1":
        print(f"Raids: All raids")
    else:
        raid_labels = [raid_label_mapping.get(raid, raid) for raid in selected_raids]
        print(f"Raids: {', '.join(raid_labels)}")
    print("-" * 50)
    
    print(f"Total datapoints: {total_count}")
    
    if daily_results:
        num_days = len(daily_results)
        avg_per_day = total_count / num_days if num_days > 0 else 0
        print(f"Number of days with data: {num_days}")
        print(f"Average datapoints per day: {avg_per_day:.1f}")
    else:
        print("No datapoints found for the specified criteria.")

def analyze_mythic_usage_patterns():
    """
    Analyzes mythic usage patterns based on skill point allocations for a specific archetype.
    Creates a pie chart showing mythic distribution and prints detailed statistics.
    """
    print("\nMythic Usage Pattern Analysis")
    print("1. All raids")
    print("2. Specified raid(s)")
    raid_choice = input("Select option (1/2): ").strip()
    
    selected_raids = []
    if raid_choice == "2":
        print("Available raids:")
        for i, raid in enumerate(raids, 1):
            print(f"  {i}. {raid_label_mapping[raid]}")
        print("Available shorthands: nol, notg, tna, tcc")
        raid_input = input("Enter raid name(s) or shorthand(s) separated by commas: ").strip()
        raid_names = [name.strip() for name in raid_input.split(",")]
        
        for raid_name in raid_names:
            resolved = resolve_raid_input(raid_name)
            if resolved and resolved != "all":
                selected_raids.append(resolved)
            elif raid_name.lower() in [r.lower() for r in raids]:
                selected_raids.append(raid_name.lower())
        
        if not selected_raids:
            print("No valid raids specified. Exiting.")
            return
    
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    archetype = input("Enter archetype to analyze: ").strip()
    
    archetype_class = None
    for class_name, archetypes in class_archetypes.items():
        if archetype.lower() in [arch.lower() for arch in archetypes]:
            archetype_class = class_name
            break
    
    if not archetype_class:
        print(f"Could not determine class for archetype '{archetype}'. Available archetypes:")
        for class_name, archetypes in class_archetypes.items():
            print(f"  {class_name.capitalize()}: {', '.join(archetypes)}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if raid_choice == "1":
        cursor.execute("""
        SELECT strength, dexterity, intelligence, defense, agility
        FROM character_data
        WHERE LOWER(archetype) = ? AND DATE(timestamp) BETWEEN ? AND ?
        """, (archetype.lower(), start_date, end_date))
    else:
        raid_conditions = " OR ".join([f"{raid} > 0" for raid in selected_raids])
        cursor.execute(f"""
        SELECT strength, dexterity, intelligence, defense, agility
        FROM character_data
        WHERE LOWER(archetype) = ? AND ({raid_conditions}) AND DATE(timestamp) BETWEEN ? AND ?
        """, (archetype.lower(), start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No data found for archetype '{archetype}' in the specified criteria.")
        return
    
    print(f"\nAnalyzing {len(rows)} {archetype} entries from {start_date} to {end_date}")
    if raid_choice == "1":
        print("Raids: All raids")
    else:
        raid_labels = [raid_label_mapping.get(raid, raid) for raid in selected_raids]
        print(f"Raids: {', '.join(raid_labels)}")
    
    if archetype_class not in mythic_guess_patterns:
        print(f"No mythic patterns defined for class '{archetype_class}'")
        return
    
    patterns = mythic_guess_patterns[archetype_class]
    
    def matches_pattern(stats, pattern_conditions):
        str_val, dex_val, int_val, def_val, agi_val = stats
        stat_values = {
            "strength": str_val,
            "dexterity": dex_val, 
            "intelligence": int_val,
            "defense": def_val,
            "agility": agi_val
        }
        
        for condition in pattern_conditions:
            stat = condition["stat"]
            stat_value = stat_values[stat]
            
            if "min" in condition and stat_value < condition["min"]:
                return False
            if "max" in condition and stat_value > condition["max"]:
                return False
        
        return True
    
    mythic_matches = {mythic: 0 for mythic in patterns.keys()}
    mythic_matches["N/A"] = 0
    overlapping_matches = []
    total_overlaps = 0
    
    for stats in rows:
        matched_mythics = []
        
        for mythic_name, conditions in patterns.items():
            if matches_pattern(stats, conditions):
                mythic_matches[mythic_name] += 1
                matched_mythics.append(mythic_name)
        
        if len(matched_mythics) == 0:
            mythic_matches["N/A"] += 1
        elif len(matched_mythics) > 1:
            overlapping_matches.append((stats, matched_mythics))
            total_overlaps += 1
    
    # Print detailed statistics
    print(f"\n{'='*60}")
    print("MYTHIC USAGE ANALYSIS RESULTS")
    print(f"{'='*60}")
    
    total_entries = len(rows)
    print(f"Total entries analyzed: {total_entries}")
    print(f"Entries with overlapping matches: {total_overlaps}")
    print(f"Overlap percentage: {(total_overlaps/total_entries)*100:.1f}%")
    
    print(f"\nMythic Distribution:")
    print(f"{'Mythic':<20} {'Count':<8} {'Percentage'}")
    print("-" * 40)
    
    sorted_mythics = sorted(mythic_matches.items(), key=lambda x: x[1], reverse=True)
    
    for mythic, count in sorted_mythics:
        percentage = (count / total_entries) * 100
        print(f"{mythic:<20} {count:<8} {percentage:.1f}%")
    
    if overlapping_matches:
        print(f"\nOverlapping Matches Details:")
        print("-" * 50)
        overlap_summary = {}
        for stats, matched in overlapping_matches:
            key = " + ".join(sorted(matched))
            if key not in overlap_summary:
                overlap_summary[key] = 0
            overlap_summary[key] += 1
        
        for combination, count in sorted(overlap_summary.items(), key=lambda x: x[1], reverse=True):
            print(f"{combination}: {count} entries")
    
    plt.figure(figsize=(10, 8))
    pie_labels = []
    pie_values = []
    pie_colors = []
    
    for mythic, count in sorted_mythics:
        if count > 0:
            pie_labels.append(f"{mythic}\n({count})")
            pie_values.append(count)
            pie_colors.append(mythic_colors.get(mythic, "#cccccc"))
    
    plt.pie(pie_values, labels=pie_labels, colors=pie_colors, autopct='%1.1f%%', startangle=140)
    
    title = f"Mythic Usage Patterns - {archetype.capitalize()}\n"
    title += f"{start_date} to {end_date}"
    if raid_choice == "1":
        title += " (All Raids)"
    else:
        title += f" ({', '.join([raid_label_mapping.get(r, r) for r in selected_raids])})"
    
    plt.title(title, fontsize=12, pad=20)
    plt.tight_layout()
    plt.show()
    
    print(f"\n{'='*60}")

def graph_mythic_usage_overtime():
    """
    Graphs mythic usage patterns over time. Can analyze:
    1. All mythics for a specific class
    2. All mythics for a specific archetype  
    3. Share percentage of a single mythic over time
    """
    print("\nMythic Usage Over Time Analysis")
    print("1. All mythics for a specific class")
    print("2. All mythics for a specific archetype")
    print("3. Share percentage of a single mythic")
    analysis_type = input("Select option (1/2/3): ").strip()
    
    print("\n1. All raids")
    print("2. Specified raid(s)")
    raid_choice = input("Select option (1/2): ").strip()
    
    selected_raids = []
    if raid_choice == "2":
        print("Available raids:")
        for i, raid in enumerate(raids, 1):
            print(f"  {i}. {raid_label_mapping[raid]}")
        print("Available shorthands: nol, notg, tna, tcc")
        raid_input = input("Enter raid name(s) or shorthand(s) separated by commas: ").strip()
        raid_names = [name.strip() for name in raid_input.split(",")]
        
        for raid_name in raid_names:
            resolved = resolve_raid_input(raid_name)
            if resolved and resolved != "all":
                selected_raids.append(resolved)
            elif raid_name.lower() in [r.lower() for r in raids]:
                selected_raids.append(raid_name.lower())
        
        if not selected_raids:
            print("No valid raids specified. Exiting.")
            return
    
    start_date = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date = input("Enter end date (YYYY-MM-DD): ").strip()
    
    if analysis_type == "1":
        class_name = input("Enter class name (archer/mage/assassin/warrior/shaman): ").strip().lower()
        if class_name not in mythic_guess_patterns:
            print(f"Invalid class. Available: {', '.join(mythic_guess_patterns.keys())}")
            return
        archetypes = class_archetypes[class_name]
        patterns = mythic_guess_patterns[class_name]
        title_entity = f"{class_name.capitalize()}"
        
    elif analysis_type == "2":
        archetype = input("Enter archetype to analyze: ").strip()
        
        archetype_class = None
        for class_name, archetypes in class_archetypes.items():
            if archetype.lower() in [arch.lower() for arch in archetypes]:
                archetype_class = class_name
                break
        
        if not archetype_class:
            print(f"Could not determine class for archetype '{archetype}'. Available archetypes:")
            for class_name, archetypes in class_archetypes.items():
                print(f"  {class_name.capitalize()}: {', '.join(archetypes)}")
            return
        
        archetypes = [archetype]
        patterns = mythic_guess_patterns[archetype_class]
        title_entity = f"{archetype.capitalize()}"
        
    else:
        print("Available mythics by class:")
        for class_name, class_patterns in mythic_guess_patterns.items():
            print(f"  {class_name.capitalize()}: {', '.join(class_patterns.keys())}")
        
        mythic_name = input("Enter mythic name: ").strip()
        
        mythic_class = None
        for class_name, class_patterns in mythic_guess_patterns.items():
            if mythic_name in class_patterns:
                mythic_class = class_name
                break
        
        if not mythic_class:
            print(f"Mythic '{mythic_name}' not found in any class patterns.")
            return
        
        archetypes = class_archetypes[mythic_class]
        patterns = {mythic_name: mythic_guess_patterns[mythic_class][mythic_name]}
        title_entity = f"{mythic_name}"
    
    def matches_pattern(stats, pattern_conditions):
        str_val, dex_val, int_val, def_val, agi_val = stats
        stat_values = {
            "strength": str_val,
            "dexterity": dex_val, 
            "intelligence": int_val,
            "defense": def_val,
            "agility": agi_val
        }
        
        for condition in pattern_conditions:
            stat = condition["stat"]
            stat_value = stat_values[stat]
            
            if "min" in condition and stat_value < condition["min"]:
                return False
            if "max" in condition and stat_value > condition["max"]:
                return False
        
        return True
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    archetype_filter = " OR ".join([f"LOWER(archetype) = '{arch.lower()}'" for arch in archetypes])
    
    if raid_choice == "1":
        query = f"""
        SELECT DATE(timestamp) as date, strength, dexterity, intelligence, defense, agility
        FROM character_data
        WHERE ({archetype_filter}) AND DATE(timestamp) BETWEEN ? AND ?
        ORDER BY date
        """
        cursor.execute(query, (start_date, end_date))
    else:
        raid_conditions = " OR ".join([f"{raid} > 0" for raid in selected_raids])
        query = f"""
        SELECT DATE(timestamp) as date, strength, dexterity, intelligence, defense, agility
        FROM character_data
        WHERE ({archetype_filter}) AND ({raid_conditions}) AND DATE(timestamp) BETWEEN ? AND ?
        ORDER BY date
        """
        cursor.execute(query, (start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print(f"No data found for the specified criteria.")
        return
    
    print(f"\nAnalyzing {len(rows)} entries from {start_date} to {end_date}")
    
    daily_data = {}
    for row in rows:
        date = row[0]
        stats = row[1:6] 
        
        if date not in daily_data:
            daily_data[date] = {mythic: 0 for mythic in patterns.keys()}
            daily_data[date]["total"] = 0
        
        daily_data[date]["total"] += 1
        
        for mythic_name, conditions in patterns.items():
            if matches_pattern(stats, conditions):
                daily_data[date][mythic_name] += 1
    
    dates = sorted(daily_data.keys())
    df_data = []
    
    for date in dates:
        row_data = {"date": pd.to_datetime(date)}
        total = daily_data[date]["total"]
        
        for mythic in patterns.keys():
            count = daily_data[date][mythic]
            if analysis_type == "3":
                row_data[mythic] = (count / total * 100) if total > 0 else 0
            else:
                row_data[mythic] = count
        
        row_data["total"] = total
        df_data.append(row_data)
    
    df = pd.DataFrame(df_data)
    
    plt.figure(figsize=(12, 7))
    
    if analysis_type == "3":
        mythic_name = list(patterns.keys())[0]
        plt.plot(df["date"], df[mythic_name], label=f"{mythic_name} Usage %", 
                linewidth=2, marker='o', markersize=4)
        plt.ylabel("Usage Percentage (%)")
        plt.title(f"{mythic_name} Usage Share Over Time")
        
    else:
        mythic_names = list(patterns.keys())
        
        for i, mythic in enumerate(mythic_names):
            percentages = []
            for date in dates:
                total = daily_data[date]["total"]
                count = daily_data[date][mythic]
                percentage = (count / total * 100) if total > 0 else 0
                percentages.append(percentage)
            
            percentages_series = pd.Series(percentages)
            ma_percentages = percentages_series.rolling(window=3, min_periods=1, center=True).mean()
            
            color = mythic_colors.get(mythic, plt.cm.Set3(i / len(mythic_names)))
            
            plt.plot(df["date"], ma_percentages, label=mythic, 
                    linewidth=2, color=color)
        
        plt.ylabel("Usage Percentage (%)")
        plt.title(f"Mythic Usage Share Over Time - {title_entity} (3-day MA)")
    
    plt.xlabel("Date")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    
    subtitle = f"{start_date} to {end_date}"
    if raid_choice == "1":
        subtitle += " (All Raids)"
    else:
        subtitle += f" ({', '.join([raid_label_mapping.get(r, r) for r in selected_raids])})"
    
    plt.figtext(0.5, 0.02, subtitle, ha='center', fontsize=10, style='italic')
    
    plt.tight_layout()
    plt.show()
    
    print(f"\n{'='*60}")
    print("SUMMARY STATISTICS")
    print(f"{'='*60}")
    
    total_entries = df["total"].sum()
    print(f"Total entries across all dates: {total_entries}")
    print(f"Date range: {len(dates)} days")
    print(f"Average entries per day: {total_entries/len(dates):.1f}")
    
    if analysis_type == "3":
        mythic_name = list(patterns.keys())[0]
        avg_usage = df[mythic_name].mean()
        max_usage = df[mythic_name].max()
        min_usage = df[mythic_name].min()
        print(f"\n{mythic_name} Usage Statistics:")
        print(f"  Average usage: {avg_usage:.1f}%")
        print(f"  Maximum usage: {max_usage:.1f}%")
        print(f"  Minimum usage: {min_usage:.1f}%")
    else:
        print(f"\nMythic totals across all dates:")
        for mythic in patterns.keys():
            total_mythic = df[mythic].sum()
            percentage = (total_mythic / total_entries * 100) if total_entries > 0 else 0
            print(f"  {mythic}: {total_mythic} ({percentage:.1f}%)")

# If make a new feature remember to add it here and in the choice selection
if __name__ == "__main__":
    print("Select Analysis Type:")
    print("1. Most Common Skillpoint Configurations")
    print("2. Graph Archetype Usage Over Time")
    print("3. Graph Average Skillpoints Over Time")
    print("4. Print Character UUIDs for Archetype")
    print("5. Graph Class Archetype Share Overtime")  
    print("6. Graph Class Usage Share Overtime") 
    print("7. Graph Archetype Share Pie Chart") 
    print("8. Create Archetype Infographic")
    print("9. Graph All Archetype Shares Overtime") 
    print("10. Plot Archetype Skill Point Band Usage")
    print("11. Analyze Raid Frequency")
    print("12. Count Datapoints Between Dates")
    print("13. Analyze Mythic Usage Patterns")
    print("14. Graph Mythic Usage Over Time")
    choice = input("Enter the number of your choice: ")

    if choice == "1":
        archetype = input("Enter the archetype to analyze: ")
        tolerance = int(input("Enter the tolerance for skillpoint similarity (e.g., 2 or 5): "))
        use_dates = input("Filter by date range? (yes/no): ").lower() == "yes"
        if use_dates:
            start_date = input("Enter the start date (YYYY-MM-DD): ")
            end_date = input("Enter the end date (YYYY-MM-DD): ")
            analyze_skillpoints(archetype, tolerance, start_date, end_date)
        else:
            analyze_skillpoints(archetype, tolerance)
    elif choice == "2":
        archetype = input("Enter the archetype to graph: ")
        raid = input("Enter the raid to analyze (or 'all' for all raids): ")
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        show_patches = input("Show patch intercepts? (yes/no): ").lower() == "yes"
        graph_archetype_overtime(archetype, raid, start_date, end_date, show_patches)
    elif choice == "3":
        entity_type = input("Enter the entity type ('class' or 'archetype'): ")
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        entity_name = input("Enter the name of the entity: ")
        graph_average_skillpoints_overtime(entity_type, entity_name, start_date, end_date)
    elif choice == "4":
        archetype = input("Enter the archetype to analyze: ")
        date = input("Enter the date (YYYY-MM-DD): ")
        print_character_uuids_for_archetype(archetype, date)
    elif choice == "5":  
        class_name = input("Enter the class to analyze (e.g., 'Warrior', 'Mage'): ")
        raid = input("Enter the raid to analyze (or 'all' for all raids): ")
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        show_patches = input("Show patch intercepts? (yes/no): ").lower() == "yes"
        graph_class_archetype_share_overtime(class_name, raid, start_date, end_date, show_patches)
    elif choice == "6": 
        raid = input("Enter the raid to analyze (or 'all' for all raids): ")
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        graph_class_usage_share_overtime(raid, start_date, end_date)
    elif choice == "7":
        raid = input("Enter the raid to analyze (or 'all' for all raids): ")
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        graph_archetype_share_pie_chart(raid, start_date, end_date)
    elif choice == "8":
        raid_input = input("Enter the raid to analyze (or 'all' for all raids, or shorthand like 'nol', 'tcc'): ")
        raid = resolve_raid_input(raid_input)
        if raid is None:
            print("Exiting due to invalid raid input.")
        else:
            start_date_1 = input("Enter the start date for timeframe 1 (YYYY-MM-DD): ")
            end_date_1 = input("Enter the end date for timeframe 1 (YYYY-MM-DD): ")
            start_date_2 = input("Enter the start date for timeframe 2 (YYYY-MM-DD): ")
            end_date_2 = input("Enter the end date for timeframe 2 (YYYY-MM-DD): ")
            create_archetype_infographic(raid, start_date_1, end_date_1, start_date_2, end_date_2)
    elif choice == "9":
        raid = input("Enter the raid to analyze (or 'all' for all raids): ")
        start_date = input("Enter the start date (YYYY-MM-DD): ")
        end_date = input("Enter the end date (YYYY-MM-DD): ")
        moving_average = input("Apply moving average? (yes/no): ").lower() == "yes"
        ma_window = 3
        if moving_average:
            try:
                ma_window = int(input("Enter moving average window (integer): "))
            except ValueError:
                print("Invalid input, using default window of 3.")
        graph_all_archetype_shares_overtime(start_date, end_date, raid, moving_average, ma_window)
    elif choice == "10":
        plot_archetype_sp_band_usage()
    elif choice == "11":
        analyze_raid_frequency()
    elif choice == "12":
        count_datapoints_between_dates()
    elif choice == "13":
        analyze_mythic_usage_patterns()
    elif choice == "14":
        graph_mythic_usage_overtime()
    else:
        print("Invalid choice. Exiting.")