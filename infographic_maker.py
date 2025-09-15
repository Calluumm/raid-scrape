import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

if len(sys.argv) < 2:
    print("csv from pipeline")
    exit()
file_name = sys.argv[1]
directory = r"c:\..."
file_name = os.path.join(directory, file_name)

db_path = r"c:\...\public_uuids.db"

reskin_mapping = {
    "HUNTER": "ARCHER",
    "KNIGHT": "WARRIOR",
    "DARKWIZARD": "MAGE",
    "NINJA": "ASSASSIN",
    "SKYSEER": "SHAMAN"
}
archetype_colors = {
    "Boltslinger": "#ffcc00",  
    "Trapper": "#006400",      
    "Sharpshooter": "#ff00ff",

    "Riftwalker": "#add8e6",
    "Lightbender": "#808080",  
    "Arcanist": "#8a2be2",     

    "Shadestepper": "#000000", 
    "Trickster": "#4b0082",    
    "Acrobat": "#c0c0c0",      

    "Fallen": "#ff0000",       
    "Battle Monk": "#fffd8d", 
    "Paladin": "#00008b",      

    "Summoner": "#ffa500",     
    "Ritualist": "#90ee90",    
    "Acolyte": "#ff4500",     

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

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
today = datetime.now().strftime("%Y-%m-%d")
#today = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d") #For use when i accidently go over the day mark
cursor.execute("""
SELECT 
    SUM(delta_nest_of_the_grootslangs) AS nest_total,
    SUM(delta_the_canyon_colossus) AS canyon_total,
    SUM(delta_orphions_nexus_of_light) AS orphion_total,
    SUM(delta_the_nameless_anomaly) AS nameless_total
FROM character_raids
""")
totals = cursor.fetchone()

MOVING_AVG_WINDOW = 3  

for raid in raids:
    cursor.execute(f"""
    SELECT class_type, archetype, strength, dexterity, intelligence, defense, agility, {raid}, timestamp
    FROM character_data
    WHERE {raid} > 0 AND {raid} <= 200 AND DATE(timestamp) = ? AND archetype != 'N/A'
    """, (today,))
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=["class_type", "archetype", "strength", "dexterity", "intelligence", "defense", "agility", "raid_count", "timestamp"])
    df["class_type"] = df["class_type"].replace(reskin_mapping)
    class_share = df.groupby("class_type")["raid_count"].sum()
    class_share_percentage = (class_share / class_share.sum()) * 100
    skill_points_avg = df.groupby("class_type")[["strength", "dexterity", "intelligence", "defense", "agility"]].mean()
    archetype_tallies = df["archetype"].value_counts()
    archetype_tally_today = df["archetype"].value_counts()
    archetype_share_today_percentage = (archetype_tally_today / archetype_tally_today.sum()) * 100
    archetype_share_today = df.groupby("archetype")["raid_count"].sum()
    archetype_share_today_percentage = (archetype_share_today / archetype_share_today.sum()) * 100

    cursor.execute(f"""
    SELECT DATE(timestamp) as date, 
           AVG(strength) as avg_strength, 
           AVG(dexterity) as avg_dexterity,
           AVG(intelligence) as avg_intelligence, 
           AVG(defense) as avg_defense, 
           AVG(agility) as avg_agility, 
           archetype, 
           COUNT(*) as archetype_tally
    FROM character_data
    WHERE {raid} > 0 AND archetype != 'N/A'
    GROUP BY date, archetype
    """)
    overtime_data = pd.DataFrame(cursor.fetchall(), columns=[
        "date", "avg_strength", "avg_dexterity", "avg_intelligence", "avg_defense", "avg_agility", "archetype", "archetype_tally"
    ])

    overtime_data = overtime_data[overtime_data["date"] >= "2025-04-03"].copy() #cut day1
    overtime_data["archetype_share"] = overtime_data.groupby("date")["archetype_tally"].transform(lambda x: (x / x.sum()) * 100)

    current_day = datetime.now().strftime("%Y-%m-%d")
    if current_day in overtime_data["date"].values:
        current_day_tallies = archetype_tallies / archetype_tallies.sum() * 100
        for archetype in current_day_tallies.index:
            overtime_data.loc[
                (overtime_data["date"] == current_day) & (overtime_data["archetype"] == archetype),
                "archetype_share"
            ] = current_day_tallies[archetype]

    skill_point_data = overtime_data.copy()  # keep sp data
    archetype_data = overtime_data[overtime_data["date"] != "2025-04-02"].copy()  # omite day1 archetypes
    archetype_data["archetype_share"] = archetype_data.groupby("date")["archetype_tally"].transform(lambda x: (x / x.sum()) * 100)

    archetype_share = (
        overtime_data.groupby(["date", "archetype"])["archetype_tally"].sum()
        / overtime_data.groupby("date")["archetype_tally"].sum()
    ).reset_index(name="archetype_share")
    archetype_share["archetype_share"] *= 100

    fig = plt.figure(figsize=(12, 15))  

    grid = fig.add_gridspec(3, 2, height_ratios=[2, 1, 2])  

    ax_pie = fig.add_subplot(grid[0, 0])
    ax_pie.pie(class_share_percentage, labels=class_share_percentage.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    ax_pie.set_title("Class % Share of Raid Completions")

    ax_table = fig.add_subplot(grid[0, 1])
    ax_table.axis("tight")
    ax_table.axis("off")
    table = ax_table.table(cellText=skill_points_avg.round(2).values,
                           colLabels=skill_points_avg.columns,
                           rowLabels=skill_points_avg.index,
                           loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(skill_points_avg.columns))))
    ax_table.set_title("Skill Point Distribution")
    ax_bar = fig.add_subplot(grid[1, :]) 
    ax_bar.bar(
        archetype_tallies.index,
        archetype_tallies.values,
        color=[archetype_colors.get(archetype, "#c7c7c7") for archetype in archetype_tallies.index]
    )
    ax_bar.set_title("Archetype Tallies for Today")
    ax_bar.set_ylabel("Count")
    ax_bar.set_xlabel("Archetype")
    ax_bar.tick_params(axis='x', rotation=45)
    ax_skill = fig.add_subplot(grid[2, 0])
    skill_colors = {
    "avg_strength": "#00aa00",
    "avg_dexterity": "#ffa500",
    "avg_defense": "#FF5555",
    "avg_intelligence": "#3c789e",
    "avg_agility": "#80a7ab"
    }
    for skill, color in skill_colors.items():
        skill_means = skill_point_data.groupby("date")[skill].mean()
        skill_means_ma = skill_means.rolling(window=MOVING_AVG_WINDOW, min_periods=1).mean()
        ax_skill.plot(
            skill_means.index,
            skill_means_ma,
            label=f"{skill.replace('avg_', '').capitalize()} (MA{MOVING_AVG_WINDOW})",
            color=color
        )
    ax_skill.set_title(f"Skill Point Averages Over Time (MA{MOVING_AVG_WINDOW})")
    ax_skill.set_xlabel("Date")
    ax_skill.set_ylabel("Average Skill Points")
    ax_skill.legend()
    ax_skill.set_xticks(skill_point_data["date"].unique()[::8])  # Date integer
    ax_skill.tick_params(axis='x', rotation=45) 

    ax_archetype = fig.add_subplot(grid[2, 1])
    # Archetype Share Over Time with Moving Average
    for archetype in overtime_data["archetype"].unique():
        if archetype == "N/A":  # Skip N/A archetype
            continue
        archetype_data_filtered = overtime_data[overtime_data["archetype"] == archetype]
        # Calculate moving average
        archetype_share_ma = archetype_data_filtered.set_index("date")["archetype_share"].rolling(window=MOVING_AVG_WINDOW, min_periods=1).mean()
        ax_archetype.plot(
            archetype_share_ma.index, 
            archetype_share_ma.values, 
            label=f"{archetype} (MA{MOVING_AVG_WINDOW})", 
            color=archetype_colors.get(archetype, "#c7c7c7")
        )
    ax_archetype.set_title(f"Archetype Share Over Time (MA{MOVING_AVG_WINDOW})")
    ax_archetype.set_xlabel("Date")
    ax_archetype.set_ylabel("Archetype Share (%)")
    ax_archetype.set_xticks(overtime_data["date"].unique()[::8])  # date integer #2
    ax_archetype.tick_params(axis='x', rotation=45)

    fig.suptitle(f"Raid Analysis: {raid.replace('delta_', '').replace('_', ' ').title()}", fontsize=16)
    df_csv = pd.read_csv(file_name)
    raid_label = raid_label_mapping.get(raid, None)
    total_completions = df_csv[df_csv["label"] == raid_label]["delta"].sum()
    print(f"Total raid completions for today: {total_completions}")
    fig.text(0.5, 0.95, f"Total Completions: {total_completions} | Date: {datetime.now().strftime('%Y-%m-%d')}", ha="center", fontsize=12)

    plt.tight_layout(rect=[0, 0, 1, 0.92]) 
    plt.savefig(f"{raid}_analysis_today.png")
    plt.close()
conn.close()
print("Infographics generated for today's data and overtime analysis.")
print("Pipeline subprocesses over, clearing deltas then finishing.")
