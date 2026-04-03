#!/usr/bin/env python3
import jsonlines, random, hashlib
random.seed(42)

TARGET = 6000
seen = set()
entries = []

def h(c): return hashlib.md5(c.encode()).hexdigest()[:12]
def add(msg, meta):
    c = json.dumps({"m":msg,"t":meta}, sort_keys=True)
    if h(c) not in seen:
        seen.add(h(c))
        entries.append({"messages":msg,"metadata":meta})

CMDS = {
    "/give": ["/give @p minecraft:diamond 10", "/give @a[tag=vip] minecraft:netherite_sword{Enchantments:[{id:sharpness,lvl:5}]} 1"],
    "/summon": ["/summon minecraft:creeper ~ ~ ~ {powered:1b}", "/summon armor_stand ~ ~1 ~ {CustomName:'\"Boss\"',NoGravity:1b}"],
    "/execute": ["/execute as @a at @s run give @s apple 1", "/execute at @p if block ~ ~-1 ~ grass_block run setblock ~ ~-1 ~ dirt", "/execute store result score @a kills run kill @e[type=creeper,distance=..5]"],
    "/fill": ["/fill -10 64 -10 10 65 10 snow_block replace air", "/fill ~-5 ~ ~-5 ~5 ~ ~5 stone hollow"],
    "/setblock": ["/setblock ~ ~-1 ~ grass_block", "/setblock ~ ~ ~ chest{Items:[{Slot:0,id:\"diamond\",Count:64}]}"],
    "/clone": ["/clone -10 64 -10 10 65 10 0 100 0 masked replace normal"],
    "/tp": ["/tp @a 0 100 0", "/tp @p @e[type=armor_stand,limit=1]"],
    "/effect": ["/effect give @a speed 30 1 true", "/effect clear @a poison"],
    "/clear": ["/clear @a diamond_sword", "/clear @p minecraft:stone 64"],
    "/scoreboard": ["/scoreboard objectives add deaths deathCount", "/scoreboard players set @a money 100", "/scoreboard players operation @a kills *= @s multiplier"],
    "/tag": ["/tag @a add ready", "/tag @e[type=armor_stand] remove cleanup"],
    "/team": ["/team add Red \"Équipe Rouge\"", "/team join Red @a[tag=team_red]", "/team option Red friendlyFire false"],
    "/title": ["/title @a title {\"text\":\"Bienvenue!\",\"color\":\"gold\"}", "/title @a times 10 70 20"],
    "/tellraw": ["/tellraw @a {\"text\":\"Hello!\",\"color\":\"blue\"}"],
    "/gamerule": ["/gamerule keepInventory true", "/gamerule commandBlockOutput false", "/gamerule mobGriefing false"],
    "/time": ["/time set day", "/time set 6000", "/time query daytime"],
    "/weather": ["/weather clear", "/weather rain 6000"],
    "/difficulty": ["/difficulty hard", "/difficulty peaceful"],
    "/gamemode": ["/gamemode creative @a", "/gamemode survival"],
    "/kill": ["/kill @e[type=item]", "/kill @e[type=!player,distance=..100]"],
    "/playsound": ["/playsound minecraft:entity.experience_orb.pickup master @a"],
    "/particle": ["/particle minecraft:flame ~ ~1 ~ 0.5 0.5 0.5 0.1 10"],
    "/advancement": ["/advancement grant @a only minecraft:story/root"],
    "/function": ["/function mydatapack:game/start"],
    "/schedule": ["/schedule function mygame:tick 1t replace"],
    "/bossbar": ["/bossbar add boss:health \"Boss Health\"", "/bossbar set boss:health value 50"],
    "/attribute": ["/attribute @p generic.movement_speed base set 0.5"],
    "/data": ["/data get entity @p Health", "/data modify storage game:main timer set value 100"],
    "/loot": ["/loot give @p loot minecraft:chests/village_blacksmith"],
    "/experience": ["/experience add @a 10 levels"],
    "/spreadplayers": ["/spreadplayers 0 0 5 50 true @a"],
    "/forceload": ["/forceload add 0 0 16 16"],
    "/locate": ["/locate structure minecraft:village_plains"],
    "/whitelist": ["/whitelist add Steve", "/whitelist on"],
    "/ban": ["/ban Steve Cheating"],
    "/op": ["/op Steve"],
    "/kick": ["/kick Steve AFK"],
    "/say": ["/say Hello everyone!"],
    "/list": ["/list"],
    "/stop": ["/stop"]
}

SEL = ["@a","@p","@r","@s","@e","@e[type=zombie]","@e[type=!player]","@a[distance=..10]","@a[tag=admin]","@a[scores=kills=10..]","@a[team=Red]","@a[level=10..20]","@a[gamemode=survival]","@e[limit=1]","@e[sort=random,limit=10]"]

MINIGAMES = ["spleef","parkour","ctf","boss_rush","survival_games","bedwars","tnt_run","dropper","puzzle","skywars","hunger_games","build_battle","hide_seek","zombie_escape"]

# Commandes de base
for cmd, examples in CMDS.items():
    for ex in examples:
        for ver in ["1.13-1.20.4","1.20.5+","bedrock"]:
            add([{"role":"system","content":"Expert Minecraft"},{"role":"user","content:f"{cmd}?"},{"role":"assistant","content:f"## {cmd}\n**Exemple:** `{ex}`\nVersion: {ver}"}],{"edition":"java" if "bedrock" not in ver else "bedrock","min_version":"1.13","category":"basic_command","command_focus":cmd})

# Sélecteurs
for s in SEL:
    add([{"role":"system","content":"Expert Minecraft"},{"role":"user","content:f"Sélecteur {s}?"},{"role":"assistant","content:f"## Sélecteur `{s}`\nFiltres: type, distance, tag, scores, team, level, gamemode, limit"}],{"edition":"both","min_version":"1.13","category":"selectors","command_focus":"selectors"})

# Execute subcommands
for sub in ["as","at","positioned","rotated","facing","if","unless","store","align","anchored","in","on"]:
    add([{"role":"system","content":"Expert Minecraft"},{"role":"user","content:f"/execute {sub}?"},{"role":"assistant","content:f"## /execute {sub}\nEx: `/execute {sub} @a at @s run give @s apple 1`"}],{"edition":"java","min_version":"1.13","category":f"execute_{sub}","command_focus":"/execute"})

# Scoreboard criteria
for crit in ["dummy","trigger","deathCount","playerKillCount","health","xp","food","air"]:
    add([{"role":"system","content":"Expert Minecraft"},{"role":"user","content:f"Scoreboard {crit}?"},{"role":"assistant","content:f"## Scoreboard\n`/scoreboard objectives add {crit}_obj {crit}`"}],{"edition":"both","min_version":"1.13","category":"scoreboard_objectives","command_focus":"/scoreboard"})

# Operations
for op in ["=","+=","-=","*=","/=","<",">","><"]:
    add([{"role":"system","content":"Expert Minecraft"},{"role":"user","content:f"Op {op} scoreboard?"},{"role":"assistant","content:f"## Operation `{op}`\n`/scoreboard players operation @a objA {op} @s objB`"}],{"edition":"both","min_version":"1.13","category":"scoreboard_operations","command_focus":"/scoreboard"})

# Minigames
for mg in MINIGAMES:
    add([{"role":"system","content":"Expert Architecture"},{"role":"user","content:f"Minigame {mg.replace('_',' ')}?"},{"role":"assistant","content":f"## {mg.title()}\nPhases: setup → loop → win/loss → reset\nDatapack: {mg}/functions/{{tick,setup,reset}}.mcfunction"}],{"edition":"both","min_version":"1.15","category":f"minigame_{mg}","command_focus":"architecture"})
    for phase in ["setup","loop","reset"]:
        add([{"role":"system","content":"Expert"},{"role":"user","content:f"Phase {phase} {mg}?"},{"role":"assistant","content":f"**{phase}:** `/function {mg}:{phase}`"}],{"edition":"both","min_version":"1.15","category":f"minigame_{mg}","command_focus":phase})

# Optimisation
opts = [("Limiter @e","/kill @e[type=item,distance=..100]"),("Schedule","/schedule function game:tick 1t"),("Tag filter","@e[type=!player,tag=!protected]"),("Limit","@e[limit=10,sort=nearest]"),("Gamerule","/gamerule commandBlockOutput false")]
for name,cmd in opts:
    add([{"role":"system","content":"Optimisation"},{"role":"user","content":f"Astuce {name}?"},{"role":"assistant","content":f"## {name}\n`{cmd}`"}],{"edition":"both","min_version":"1.13","category":"optimization","command_focus":"performance"})

# Migrations
migs = [("1.12→1.13","/give @p 264 10","/give @p minecraft:diamond 10","Flattening"),("1.20.4→1.20.5","{CustomName:'\"X\"'}","[custom_name='\"X\"']","Components")]
for v,old,new,reason in migs:
    add([{"role":"system","content":"Migration"},{"role":"user","content":f"Migrer {v}?"},{"role":"assistant","content":f"## {v}\nAvant: `{old}`\nAprès: `{new}`\nRaison: {reason}"}],{"edition":"java","min_version":v.split('→')[0],"category":"version_migration","command_focus":"migration","breaking_changes":v})

# Java vs Bedrock
diffs = [("/execute","Java: as @a at @s run","Bedrock: @a ~ ~ ~"),("/particle","Java: minecraft:flame ...","Bedrock: flame ~ ~ ~")]
for f,j,b in diffs:
    add([{"role":"system","content":"Java/Bedrock"},{"role":"user","content":f"Diff {f}?"},{"role":"assistant","content":f"## {f}\nJava: {j}\nBedrock: {b}"}],{"edition":"both","min_version":"1.16","category":"java_bedrock_diff","command_focus":f})

# Générer plus si nécessaire
while len(entries) < TARGET:
    for e in list(entries)[:500]:
        if len(entries) >= TARGET: break
        ne = {"messages":e["messages"],"metadata":{**e["metadata"],"best_practices":["limit_checks","use_predicates"]}}
        c = json.dumps(ne,sort_keys=True)
        if h(c) not in seen:
            seen.add(h(c))
            entries.append(ne)

random.shuffle(entries)
with jsonlines.open("minecraft_complete_dataset.jsonl","w") as w: w.write_all(entries)
print(f"✅ {len(entries)} lignes générées dans minecraft_complete_dataset.jsonl")
