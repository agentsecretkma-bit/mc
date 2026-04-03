#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de Dataset Massif Minecraft (100K+ lignes)
Couverture : 1.7 - 1.21+, Java & Bedrock, Command Blocks, Predicates, Loot Tables, Minigames.
"""

import json
import random
import itertools

OUTPUT_FILE = "minecraft_ultimate_dataset.jsonl"

# --- CONFIGURATION & DONNÉES DE BASE ---

VERSIONS_JAVA = [
    {"id": "1.7.10", "era": "pre-flattening", "type": "java"},
    {"id": "1.8.9", "era": "pre-flattening", "type": "java"},
    {"id": "1.9.4", "era": "combat-update", "type": "java"},
    {"id": "1.12.2", "era": "pre-flattening", "type": "java"},
    {"id": "1.13.2", "era": "flattening", "type": "java"},
    {"id": "1.14.4", "era": "village-update", "type": "java"},
    {"id": "1.16.5", "era": "nether-update", "type": "java"},
    {"id": "1.17.1", "era": "caves-cliffs-1", "type": "java"},
    {"id": "1.18.2", "era": "caves-cliffs-2", "type": "java"},
    {"id": "1.19.4", "era": "execute-improvements", "type": "java"},
    {"id": "1.20.4", "era": "pre-components", "type": "java"},
    {"id": "1.20.5", "era": "components", "type": "java"},
    {"id": "1.21",   "era": "tricky-trials", "type": "java"},
]

VERSIONS_BEDROCK = [
    {"id": "1.12", "era": "legacy", "type": "bedrock"},
    {"id": "1.16", "era": "nether", "type": "bedrock"},
    {"id": "1.19", "era": "wild", "type": "bedrock"},
    {"id": "1.20", "era": "trails", "type": "bedrock"},
    {"id": "1.21", "era": "latest", "type": "bedrock"},
]

ALL_VERSIONS = VERSIONS_JAVA + VERSIONS_BEDROCK

BLOCKS_OLD = ["1", "2", "3", "4", "5", "41", "42", "57", "98", "133"] # Stone, Sand, etc.
BLOCKS_NEW = ["minecraft:stone", "minecraft:sand", "minecraft:diamond_block", "minecraft:obsidian", "minecraft:bedrock", "minecraft:command_block", "minecraft:repeating_command_block", "minecraft:chain_command_block", "minecraft:structure_block", "minecraft:barrier", "minecraft:light", "minecraft:tnt", "minecraft:water", "minecraft:lava", "minecraft:chest", "minecraft:ender_chest", "minecraft:shulker_box", "minecraft:beacon", "minecraft:anvil", "minecraft:enchanting_table", "minecraft:crafting_table", "minecraft:furnace", "minecraft:dispenser", "minecraft:dropper", "minecraft:hopper", "minecraft:observer", "minecraft:piston", "minecraft:sticky_piston", "minecraft:slime_block", "minecraft:honey_block", "minecraft:target", "minecraft:lodestone", "minecraft:respawn_anchor", "minecraft:amethyst_block", "minecraft:copper_block", "minecraft:raw_iron_block", "minecraft:deepslate", "minecraft:tuff", "minecraft:dripstone_block", "minecraft:moss_block", "minecraft:powder_snow", "minecraft:glow_lichen", "minecraft:sculk_sensor", "minecraft:calibrated_sculk_sensor", "minecraft:sculk_catalyst", "minecraft:sculk_shrieker", "minecraft:reinforced_deepslate", "minecraft:chiseled_bookshelf", "minecraft:decorated_pot", "minecraft:suspicious_sand", "minecraft:suspicious_gravel", "minecraft:sniffer_egg", "minecraft:pitcher_pod", "minecraft:torchflower", "minecraft:pitcher_plant", "minecraft:cherry_leaves", "minecraft:cherry_log", "minecraft:bamboo_block", "minecraft:netherite_block"]

ITEMS_OLD = ["264", "276", "277", "278", "279", "298", "299", "300", "301", "340", "367", "383"]
ITEMS_NEW = ["minecraft:diamond", "minecraft:netherite_ingot", "minecraft:stick", "minecraft:stone_sword", "minecraft:iron_pickaxe", "minecraft:golden_axe", "minecraft:diamond_hoe", "minecraft:netherite_helmet", "minecraft:leather_chestplate", "minecraft:iron_leggings", "minecraft:chainmail_boots", "minecraft:bow", "minecraft:arrow", "minecraft:spectral_arrow", "minecraft:tipped_arrow", "minecraft:trident", "minecraft:crossbow", "minecraft:shield", "minecraft:elytra", "minecraft:totem_of_undying", "minecraft:shulker_shell", "minecraft:dragon_egg", "minecraft:beacon", "minecraft:nether_star", "minecraft:enchanted_golden_apple", "minecraft:music_disc_13", "minecraft:compass", "minecraft:clock", "minecraft:map", "minecraft:filled_map", "minecraft:lead", "minecraft:name_tag", "minecraft:saddle", "minecraft:armor_stand", "minecraft:spawn_egg", "minecraft:experience_bottle", "minecraft:fire_charge", "minecraft:ender_pearl", "minecraft:blaze_rod", "minecraft:ghast_tear", "minecraft:gold_nugget", "minecraft:glass_bottle", "minecraft:spider_eye", "minecraft:fermented_spider_eye", "minecraft:blaze_powder", "minecraft:magma_cream", "minecraft:brewing_stand", "minecraft:cauldron", "minecraft:eye_of_ender", "minecraft:glistering_melon_slice", "minecraft:rabbit_foot", "minecraft:rabbit_hide", "minecraft:prismarine_shard", "minecraft:prismarine_crystals", "minecraft:chorus_fruit", "minecraft:popped_chorus_fruit", "minecraft:beetroot", "minecraft:beetroot_seeds", "minecraft:dragon_breath", "minecraft:elytra", "minecraft:end_crystal", "minecraft:spruce_boat", "minecraft:birch_boat", "minecraft:jungle_boat", "minecraft:acacia_boat", "minecraft:dark_oak_boat", "minecraft:turtle_helmet", "minecraft:phantom_membrane", "minecraft:nautilus_shell", "minecraft:heart_of_the_sea", "minecraft:conduit", "minecraft:turtle_scute", "minecraft:trident", "minecraft:crossbow", "minecraft:flower_banner_pattern", "minecraft:creeper_banner_pattern", "minecraft:skull_banner_pattern", "minecraft:mojang_banner_pattern", "minecraft:globe_banner_pattern", "minecraft:piglin_banner_pattern", "minecraft:campfire", "minecraft:soul_campfire", "minecraft:suspicious_stew", "minecraft:loom", "minecraft:cartography_table", "minecraft:fletching_table", "minecraft:smithing_table", "minecraft:grindstone", "minecraft:lectern", "minecraft:stonecutter", "minecraft:blast_furnace", "minecraft:smoker", "minecraft:lantern", "minecraft:soul_lantern", "minecraft:warped_stem", "minecraft:crimson_stem", "minecraft:warped_hyphae", "minecraft:crimson_hyphae", "minecraft:stripped_warped_stem", "minecraft:stripped_crimson_stem", "minecraft:shroomlight", "minecraft:weeping_vines", "minecraft:twisting_vines", "minecraft:netherite_scrap", "minecraft:ancient_debris", "minecraft:target", "minecraft:lodestone", "minecraft:blackstone", "minecraft:basalt", "minecraft:soul_soil", "minecraft:hoglin_spawn_egg", "minecraft:piglin_spawn_egg", "minecraft:strider_spawn_egg", "minecraft:zoglin_spawn_egg", "minecraft:piglin_brute_spawn_egg", "minecraft:axolotl_spawn_egg", "minecraft:goat_spawn_egg", "minecraft:glow_squid_spawn_egg", "minecraft:allay_spawn_egg", "minecraft:warden_spawn_egg", "minecraft:frog_spawn_egg", "minecraft:tadpole_spawn_egg", "minecraft:camel_spawn_egg", "minecraft:sniffer_spawn_egg", "minecraft:armadillo_spawn_egg", "minecraft:breeze_spawn_egg", "minecraft:bogged_spawn_egg"]

ENTITIES_OLD = ["Zombie", "Skeleton", "Creeper", "Spider", "Pig", "Cow", "Sheep", "Chicken", "Squid", "Villager", "Enderman", "Ghast", "PigZombie", "Blaze", "MagmaCube", "Slime", "Silverfish", "EnderDragon", "Wither", "Bat", "Witch", "Endermite", "Guardian", "Rabbit", "Horse", "Donkey", "Mule", "SkeletonHorse", "ZombieHorse"]
ENTITIES_NEW = ["minecraft:zombie", "minecraft:skeleton", "minecraft:creeper", "minecraft:spider", "minecraft:pig", "minecraft:cow", "minecraft:sheep", "minecraft:chicken", "minecraft:squid", "minecraft:villager", "minecraft:enderman", "minecraft:ghast", "minecraft:zombified_piglin", "minecraft:blaze", "minecraft:magma_cube", "minecraft:slime", "minecraft:silverfish", "minecraft:ender_dragon", "minecraft:wither", "minecraft:bat", "minecraft:witch", "minecraft:endermite", "minecraft:guardian", "minecraft:rabbit", "minecraft:horse", "minecraft:donkey", "minecraft:mule", "minecraft:skeleton_horse", "minecraft:zombie_horse", "minecraft:stray", "minecraft:husk", "minecraft:wither_skeleton", "minecraft:drowned", "minecraft:phantom", "minecraft:turtle", "minecraft:cod", "minecraft:salmon", "minecraft:pufferfish", "minecraft:tropical_fish", "minecraft:dolphin", "minecraft:ocelot", "minecraft:cat", "minecraft:wolf", "minecraft:fox", "minecraft:panda", "minecraft:llama", "minecraft:trader_llama", "minecraft:parrot", "minecraft:vindicator", "minecraft:evoker", "minecraft:illusioner", "minecraft:invocation", "minecraft:vex", "minecraft:pillager", "minecraft:ravager", "minecraft:wandering_trader", "minecraft:hoglin", "minecraft:piglin", "minecraft:strider", "minecraft:zoglin", "minecraft:piglin_brute", "minecraft:axolotl", "minecraft:goat", "minecraft:glow_squid", "minecraft:allay", "minecraft:warden", "minecraft:frog", "minecraft:tadpole", "minecraft:camel", "minecraft:sniffer", "minecraft:armadillo", "minecraft:breeze", "minecraft:bogged", "minecraft:item", "minecraft:falling_block", "minecraft:area_effect_cloud", "minecraft:armor_stand", "minecraft:arrow", "minecraft:spectral_arrow", "minecraft:tipped_arrow", "minecraft:egg", "minecraft:snowball", "minecraft:fireball", "minecraft:small_fireball", "minecraft:ender_pearl", "minecraft:eye_of_ender", "minecraft:potion", "minecraft:experience_bottle", "minecraft:minecart", "minecraft:chest_minecart", "minecraft:furnace_minecart", "minecraft:tnt_minecart", "minecraft:hopper_minecart", "minecraft:command_block_minecart", "minecraft:boat", "minecraft:chest_boat", "minecraft:fishing_bobber", "minecraft:lightning_bolt", "minecraft:marker", "minecraft:text_display", "minecraft:block_display", "minecraft:item_display", "minecraft:interaction", "minecraft:player"]

SELECTORS = ["@p", "@a", "@r", "@s", "@e"]
SELECTOR_FILTERS = [
    "", "x=0,y=0,z=0", "distance=..10", "distance=10..20", "level=1..5", "gamemode=survival", "team=Red", "tag=player1", "type=!player", "limit=1", "sort=nearest", "sort=furthest", "sort=random", "sort=arbitrary", "nbt={Health:1f}", "scores={obj=1..}", "x_rotation=10..20", "y_rotation=-10..10"
]

TEAMS = ["Red", "Blue", "Green", "Yellow", "Spectator", "Alive", "Dead", "TeamA", "TeamB"]
OBJECTIVES = ["health", "score", "kills", "deaths", "money", "time", "level", "custom"]
OPERATIONS = ["=", "+=", "-=", "*=", "/=", "%=", "<", ">", "><"]

COMMAND_BLOCKS_TYPES = ["impulse", "repeating", "chain"]
CB_CONDITIONS = ["conditional", "unconditional"]
CB_MODES = ["redstone", "auto"]

# --- GÉNÉRATEURS DE COMMANDES ---

def get_block(version):
    if version["era"] == "pre-flattening":
        return random.choice(BLOCKS_OLD)
    return random.choice(BLOCKS_NEW)

def get_item(version):
    if version["era"] == "pre-flattening":
        return random.choice(ITEMS_OLD)
    return random.choice(ITEMS_NEW)

def get_entity(version):
    if version["era"] == "pre-flattening":
        return random.choice(ENTITIES_OLD)
    return random.choice(ENTITIES_NEW)

def generate_selector():
    base = random.choice(SELECTORS)
    filters = random.sample(SELECTOR_FILTERS, k=random.randint(0, 3))
    if not filters:
        return base
    return f"{base}[{','.join(filters)}]"

def generate_scoreboard_cmd(version):
    obj = random.choice(OBJECTIVES)
    team = random.choice(TEAMS)
    op = random.choice(OPERATIONS)
    val = random.randint(1, 100)
    sel = generate_selector()
    
    cmds = []
    # Create objective
    if version["era"] == "pre-flattening":
        cmds.append(f"/scoreboard objectives add {obj} dummy")
    else:
        cmds.append(f"/scoreboard objectives add {obj} dummy")
    
    # Set/Modify score
    cmds.append(f"/scoreboard players set {sel} {obj} {val}")
    cmds.append(f"/scoreboard players operation {sel} {obj} {op} @r {obj}")
    
    # Team commands
    cmds.append(f"/team add {team}")
    cmds.append(f"/team join {team} {sel}")
    
    return cmds

def generate_give_cmd(version):
    sel = generate_selector()
    item = get_item(version)
    count = random.randint(1, 64)
    
    if version["era"] == "pre-flattening":
        # Old syntax: /give <player> <id> <amount> <data>
        data = random.randint(0, 15)
        return [f"/give {sel} {item} {count} {data}"]
    elif version["id"] in ["1.20.5", "1.21"]:
        # Components syntax
        components = []
        if random.random() > 0.5:
            components.append(f'custom_name=\'{{"text":"Magic Item"}}\'')
        if random.random() > 0.5:
            components.append(f'unbreakable={{}}')
        if random.random() > 0.5:
            components.append(f'enchantments={{levels:{{"minecraft:sharpness":{random.randint(1,5)}}}}}')
        
        comp_str = ""
        if components:
            comp_str = f"[{','.join(components)}]"
        return [f"/give {sel} {item}{comp_str} {count}"]
    else:
        # NBT syntax (1.13 - 1.20.4)
        nbt_parts = []
        if random.random() > 0.5:
            nbt_parts.append(f'display:{{Name:\'{{"text":"Magic Item"}}\'}}')
        if random.random() > 0.5:
            nbt_parts.append(f'Unbreakable:1b')
        if random.random() > 0.5:
            nbt_parts.append(f'Enchantments:[{{id:"minecraft:sharpness",lvl:{random.randint(1,5)}}}]')
        
        nbt = ""
        if nbt_parts:
            nbt = "{" + ",".join(nbt_parts) + "}"
        return [f"/give {sel} {item} {count} {nbt}"]

def generate_execute_chain(version):
    # Génère une chaîne complexe de /execute
    cmds = []
    sub_cmd = f"say Hello from {generate_selector()}"
    
    if version["era"] == "pre-flattening":
        # 1.12 and below: Very limited execute
        cmds.append(f"/execute {generate_selector()} ~ ~ ~ {sub_cmd}")
    elif version["id"] in ["1.13.2", "1.14.4", "1.15.2", "1.16.5"]:
        # 1.13+ new syntax but before some additions
        cmds.append(f"/execute as {generate_selector()} at @s run {sub_cmd}")
        cmds.append(f"/execute positioned ^ ^ ^1 as {generate_selector()} run {sub_cmd}")
        cmds.append(f"/execute if entity {generate_selector()} run {sub_cmd}")
        cmds.append(f"/execute unless block ~ ~-1 ~ minecraft:air run {sub_cmd}")
    elif version["id"] in ["1.17.1", "1.18.2", "1.19.4", "1.20.4"]:
        # Advanced execute
        cmds.append(f"/execute as {generate_selector()} at @s aligned ~ ~ ~ run {sub_cmd}")
        cmds.append(f"/execute on ground run {sub_cmd}")
        cmds.append(f"/execute facing entity {generate_selector()} eyes run {sub_cmd}")
        cmds.append(f"/execute store result score {random.choice(OBJECTIVES)} {random.choice(OBJECTIVES)} run data get entity @s Health")
    else: 
        # 1.20.5+ (syntax stable but strict)
        cmds.append(f"/execute as {generate_selector()} at @s run {sub_cmd}")
        # In 1.20.5+, some subcommands changed slightly or became more strict, but core remains
        
    return cmds

def generate_attribute_cmd(version):
    if version["era"] in ["pre-flattening", "flattening", "village-update", "nether-update"]:
        return [] # Attribute command introduced/changed later significantly
    
    entity = generate_selector()
    attr = random.choice(["generic.max_health", "generic.movement_speed", "generic.attack_damage", "generic.knockback_resistance", "generic.luck"])
    op = random.choice(["base set", "base add", "modifier add", "modifier remove"])
    uuid = "12345678-1234-1234-1234-1234567890ab"
    val = random.uniform(0.1, 10.0)
    
    if version["id"] in ["1.20.5", "1.21"]:
        # Syntax changed in 1.20.5 to be more consistent
        return [f"/attribute {entity} {attr} {op} {uuid} name {val}"] # Simplified for generation
    else:
        return [f"/attribute {entity} {attr} {op} {uuid} {val}"]

def generate_random_cmd(version):
    if version["id"] not in ["1.21"]:
        return []
    
    range_min = random.randint(1, 10)
    range_max = range_min + random.randint(5, 20)
    return [f"/random value set {random.choice(OBJECTIVES)} {range_min}..{range_max}"]

def generate_tick_cmd(version):
    if version["id"] not in ["1.20.2", "1.20.4", "1.20.5", "1.21"]: # Tick command added around 1.20.2 experimentally/stable later
        return []
    rate = random.choice([1, 2, 5, 10, 20])
    return [f"/tick rate {rate}", f"/tick step freeze", f"/tick step unstep"]

def generate_place_cmd(version):
    if version["id"] not in ["1.19.4", "1.20.4", "1.20.5", "1.21"]:
        return []
    structure = random.choice(["minecraft:village/plains", "minecraft:pillager_outpost", "minecraft:mineshaft", "minecraft:temple/desert"])
    return [f"/place structure {structure} ~ ~ ~"]

def generate_ride_damage_enchant(version):
    cmds = []
    target = generate_selector()
    
    # /damage
    if version["id"] in ["1.19.4", "1.20.4", "1.20.5", "1.21"]:
        amount = random.randint(1, 20)
        source = random.choice(["magic", "explosion", "fall", "fire", "mob_attack"])
        cmds.append(f"/damage {target} {amount} {source}")
    
    # /ride
    if version["id"] in ["1.20.5", "1.21"]:
        mount = get_entity(version)
        cmds.append(f"/ride {target} start_riding {mount}")
        cmds.append(f"/ride {target} stop_riding")
        cmds.append(f"/ride {target} summon_mount {mount}")
        
    # /enchant
    slot = random.choice(["weapon", "head", "chest", "legs", "feet", "mainhand", "offhand"])
    ench = random.choice(["sharpness", "protection", "efficiency", "fortune", "looting"])
    level = random.randint(1, 5)
    cmds.append(f"/enchant {target} {ench} {level}") # Basic syntax works across most modern versions
    
    return cmds

def generate_function_cmd(version):
    ns = random.choice(["mydatapack", "custom_game", "system"])
    func = random.choice(["init", "tick", "reset", "score_update", "lobby_loop"])
    
    cmds = []
    if version["id"] in ["1.20.5", "1.21"]:
        # With arguments
        args = f"arg1={random.randint(1,10)} arg2=test"
        cmds.append(f"/function {ns}:{func} with {args}")
        cmds.append(f"/function {ns}:{func} if entity {generate_selector()}")
        cmds.append(f"/function {ns}:{func} unless entity {generate_selector()}")
    else:
        cmds.append(f"/function {ns}:{func}")
        
    return cmds

def generate_data_storage(version):
    cmds = []
    target = random.choice(["entity @s", "block ~ ~ ~", "storage myns:mys"])
    
    if version["era"] != "pre-flattening":
        cmds.append(f"/data modify {target} CustomData set value {{Hello:\"World\"}}")
        cmds.append(f"/data get {target}")
        cmds.append(f"/data merge {target} {{NewKey:1b}}")
        if version["id"] not in ["1.13.2", "1.14.4"]: # Remove existed for a bit then came back or changed
             cmds.append(f"/data remove {target} CustomData")
    return cmds

def generate_predicates_json():
    # Generate JSON string for predicate
    pred = {
        "condition": random.choice(["minecraft:entity_properties", "minecraft:block_state_property", "minecraft:random_chance"]),
        "predicate": {}
    }
    if pred["condition"] == "minecraft:entity_properties":
        pred["predicate"] = {"flags": {"is_on_fire": True}, "equipment": {"mainhand": {"items": ["minecraft:diamond_sword"]}}}
        pred["entity"] = "this"
    elif pred["condition"] == "minecraft:block_state_property":
        pred["block"] = "minecraft:redstone_wire"
        pred["properties"] = {"power": "15"}
    elif pred["condition"] == "minecraft:random_chance":
        pred["chance"] = random.uniform(0.1, 0.9)
    
    return json.dumps(pred)

def generate_loot_table_json():
    pool = {
        "pools": [
            {
                "rolls": random.randint(1, 5),
                "entries": [
                    {
                        "type": "item",
                        "name": get_item({"era": "modern"}), # Force new name
                        "functions": [
                            {"function": "set_count", "count": random.randint(1, 64)},
                            {"function": "enchant_randomly"}
                        ]
                    }
                ],
                "conditions": [
                    {"condition": "random_chance", "chance": 0.5}
                ]
            }
        ]
    }
    return json.dumps(pool)

def generate_command_block_setup(task_type, version):
    """Génère une configuration complète de Command Blocks pour une tâche donnée"""
    lines = []
    cb_type = "repeating" if task_type == "timer" else "chain"
    condition = "conditional" if random.random() > 0.5 else "unconditional"
    mode = "auto"
    
    # Header comment
    lines.append(f"# Task: {task_type} | Version: {version['id']} | Type: {cb_type}")
    
    base_cmds = []
    if task_type == "timer":
        # Timer logic
        interval = random.choice([20, 60, 100, 600])
        base_cmds = [
            f"scoreboard players add global_time time 1",
            f"execute if score global_time time matches {interval}.. run scoreboard players set global_time time 0",
            f"execute if score global_time time matches 0 run say Timer Tick!"
        ]
    elif task_type == "shop":
        base_cmds = [
            f"execute as @a[scores={{money=10..}}] run scoreboard players remove @s money 10",
            f"execute as @a[scores={{money=10..}}] run give @s diamond 1",
            f"title @a title \"Purchase Successful\""
        ]
    elif task_type == "detection":
        base_cmds = [
            f"execute if entity @e[type=minecraft:creeper,distance=..5] run effect give @s slowness 2 1 true",
            f"execute unless entity @e[type=minecraft:creeper,distance=..5] run effect clear @s slowness"
        ]
    elif task_type == "teleport":
        base_cmds = [
            f"tp @a[tag=lobby] 0 100 0",
            f"execute as @a rotated ~ ~ run tp @s ^ ^ ^-5"
        ]
    
    for cmd in base_cmds:
        lines.append(f"/execute as @s at @s run {cmd}") # Wrapped for CB context often
        
    return lines

def generate_minigame_architecture(game_type, version):
    """Génère l'architecture complète d'un minigame"""
    content = []
    
    phases = ["lobby", "countdown", "playing", "ending", "reset"]
    teams = ["Red", "Blue"] if game_type in ["ctf", "bedwars"] else []
    
    content.append(f"# Minigame: {game_type} | Version: {version['id']}")
    
    # Init
    content.append(f"/gamerule doDaylightCycle false")
    content.append(f"/gamerule keepInventory true")
    content.append(f"/scoreboard objectives add lobby dummy")
    content.append(f"/scoreboard objectives add game_state dummy")
    
    if game_type == "spleef":
        content.append(f"/fill ~-10 ~ ~-10 ~10 ~ ~10 minecraft:air replace minecraft:snow_block")
        content.append(f"/execute if block ~ ~-1 ~ minecraft:air run kill @a")
    elif game_type == "parkour":
        content.append(f"/execute if entity @a[x=~5, y=~, z=~, distance=..2] run tp @s ~ ~20 ~")
        content.append(f"/advancement grant @a only custom_game.parkour.win")
    elif game_type == "ctf":
        for t in teams:
            content.append(f"/team add {t}")
            content.append(f"/scoreboard objectives add {t.lower()}_flag dummy")
        content.append(f"/execute if entity @a[team=Red, tag=has_blue_flag] at @s positioned ~ ~1 ~ run kill @s") # Simple capture logic
        
    # Loop simulation
    content.append(f"/function custom:{game_type}:tick")
    
    return content

def generate_error_correction_example(version):
    """Génère des paires Erreur -> Correction"""
    errors = []
    
    if version["era"] == "pre-flattening":
        errors.append({
            "prompt": f"Correction commande: /give @p 264 1 0",
            "response": f"Cette commande est valide pour la version {version['id']}. En 1.13+, utilisez: /give @p minecraft:diamond 1"
        })
    else:
        errors.append({
            "prompt": f"Erreur: /give @p diamond 1 (ID invalide en {version['id']})",
            "response": f"La commande correcte est: /give @p minecraft:diamond 1. Les IDs doivent être namespacées depuis la 1.13."
        })
        
    if version["id"] in ["1.20.5", "1.21"]:
        errors.append({
            "prompt": f"Erreur: /give @p minecraft:diamond_sword{{Enchantments:...}} 1",
            "response": f"Depuis la 1.20.5, les NBT sont remplacés par des components. Utilisez: /give @p minecraft:diamond_sword[enchantments={{levels:{{\"minecraft:sharpness\":1}}}}] 1"
        })
        
    return errors

# --- BOUCLE PRINCIPALE DE GÉNÉRATION ---

def main():
    print(f"Démarrage de la génération du dataset vers {OUTPUT_FILE}...")
    
    total_lines = 0
    target_lines = 150000 # Vise large
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        
        # 1. Commandes de base massives (Give, Effect, TP, Summon, etc.)
        print("Génération des commandes de base...")
        for _ in range(20000):
            ver = random.choice(ALL_VERSIONS)
            cmd_type = random.choice(["give", "summon", "effect", "tp", "clear", "kill", "xp", "gamemode"])
            
            cmds = []
            if cmd_type == "give": cmds = generate_give_cmd(ver)
            elif cmd_type == "summon": cmds = [f"/summon {get_entity(ver)} ~ ~ ~ {{CustomName:'\"Test\"'}}"] if ver["era"] != "components" else [f"/summon {get_entity(ver)} ~ ~ ~ {{custom_name:'{{\"text\":\"Test\"}}'}}"]
            elif cmd_type == "effect": cmds = [f"/effect give {generate_selector()} speed 10 1 true"]
            elif cmd_type == "tp": cmds = [f"/tp {generate_selector()} ~ ~10 ~"]
            elif cmd_type == "clear": cmds = [f"/clear {generate_selector()} {get_item(ver)}"]
            elif cmd_type == "kill": cmds = [f"/kill {generate_selector()}"]
            elif cmd_type == "xp": cmds = [f"/experience add {generate_selector()} {random.randint(1,100)} levels"]
            elif cmd_type == "gamemode": cmds = [f"/gamemode {random.choice(['survival', 'creative', 'spectator', 'adventure'])} {generate_selector()}"]
            
            if cmds:
                entry = {
                    "messages": [
                        {"role": "system", "content": f"You are a Minecraft expert for version {ver['id']} ({ver['type']})."},
                        {"role": "user", "content": f"Génère une commande {cmd_type} pour {ver['id']}."},
                        {"role": "assistant", "content": "\n".join(cmds)}
                    ],
                    "metadata": {"version": ver["id"], "category": "basic", "command": cmd_type}
                }
                f.write(json.dumps(entry) + "\n")
                total_lines += 1

        # 2. Execute Chains & Complex Logic
        print("Génération des chaînes /execute...")
        for _ in range(15000):
            ver = random.choice([v for v in ALL_VERSIONS if v["era"] != "pre-flattening"])
            cmds = generate_execute_chain(ver)
            if cmds:
                entry = {
                    "messages": [
                        {"role": "system", "content": f"Expert Minecraft {ver['id']}."},
                        {"role": "user", "content": "Crée une logique complexe avec /execute."},
                        {"role": "assistant", "content": "\n".join(cmds)}
                    ],
                    "metadata": {"version": ver["id"], "category": "execute_complex"}
                }
                f.write(json.dumps(entry) + "\n")
                total_lines += 1

        # 3. Scoreboard & Teams
        print("Génération Scoreboard/Teams...")
        for _ in range(10000):
            ver = random.choice(ALL_VERSIONS)
            cmds = generate_scoreboard_cmd(ver)
            entry = {
                "messages": [
                    {"role": "system", "content": f"Expert Minecraft {ver['id']}."},
                    {"role": "user", "content": "Gère des scores et des équipes."},
                    {"role": "assistant", "content": "\n".join(cmds)}
                ],
                "metadata": {"version": ver["id"], "category": "scoreboard"}
            }
            f.write(json.dumps(entry) + "\n")
            total_lines += 1

        # 4. Nouvelles Commandes (Attribute, Random, Tick, Place, Ride, Damage)
        print("Génération nouvelles commandes (1.19-1.21)...")
        for _ in range(10000):
            ver = random.choice([v for v in ALL_VERSIONS if v["id"] in ["1.19.4", "1.20.4", "1.20.5", "1.21"]])
            cmds = []
            cmds.extend(generate_attribute_cmd(ver))
            cmds.extend(generate_random_cmd(ver))
            cmds.extend(generate_tick_cmd(ver))
            cmds.extend(generate_place_cmd(ver))
            cmds.extend(generate_ride_damage_enchant(ver))
            cmds.extend(generate_function_cmd(ver))
            cmds.extend(generate_data_storage(ver))
            
            if cmds:
                entry = {
                    "messages": [
                        {"role": "system", "content": f"Expert Minecraft {ver['id']} (Features récentes)."},
                        {"role": "user", "content": "Utilise les commandes avancées récentes."},
                        {"role": "assistant", "content": "\n".join(cmds)}
                    ],
                    "metadata": {"version": ver["id"], "category": "advanced_new"}
                }
                f.write(json.dumps(entry) + "\n")
                total_lines += 1

        # 5. Command Blocks Configurations
        print("Génération configurations Command Blocks...")
        tasks = ["timer", "shop", "detection", "teleport", "boss_phase", "parkour_check", "door_lock", "wave_spawner"]
        for _ in range(15000):
            ver = random.choice(ALL_VERSIONS)
            task = random.choice(tasks)
            lines = generate_command_block_setup(task, ver)
            
            entry = {
                "messages": [
                    {"role": "system", "content": f"Architecte Command Block {ver['id']}."},
                    {"role": "user", "content": f"Configure des Command Blocks pour un système de {task}."},
                    {"role": "assistant", "content": "\n".join(lines)}
                ],
                "metadata": {"version": ver["id"], "category": "command_blocks", "task": task}
            }
            f.write(json.dumps(entry) + "\n")
            total_lines += 1

        # 6. Architectures de Minigames Complets
        print("Génération architectures Minigames...")
        games = ["spleef", "parkour", "ctf", "bedwars", "skywars", "survival_games", "tnf_run", "dropper", "puzzle", "hide_and_seek", "build_battle", "egg_wars", "murder_mystery", "duels", "quake", "tnt_tag", "bow_spleef", "bridge", "uhc", "speed_builders"]
        for _ in range(15000):
            ver = random.choice([v for v in ALL_VERSIONS if v["era"] != "pre-flattening"]) # Minigames complexes surtout post-1.13
            game = random.choice(games)
            lines = generate_minigame_architecture(game, ver)
            
            entry = {
                "messages": [
                    {"role": "system", "content": f"Développeur de Minigame {ver['id']}."},
                    {"role": "user", "content": f"Crée l'architecture complète pour un minigame {game}."},
                    {"role": "assistant", "content": "\n".join(lines)}
                ],
                "metadata": {"version": ver["id"], "category": "minigame_arch", "game": game}
            }
            f.write(json.dumps(entry) + "\n")
            total_lines += 1

        # 7. Predicates & Loot Tables (JSON inside JSONL)
        print("Génération Predicates & Loot Tables...")
        for _ in range(5000):
            ver = random.choice([v for v in ALL_VERSIONS if v["era"] != "pre-flattening"])
            p_json = generate_predicates_json()
            l_json = generate_loot_table_json()
            
            content = f"Predicate:\n{p_json}\n\nLoot Table:\n{l_json}"
            entry = {
                "messages": [
                    {"role": "system", "content": f"Expert Data Packs {ver['id']}."},
                    {"role": "user", "content": "Génère un predicate et une loot table associés."},
                    {"role": "assistant", "content": content}
                ],
                "metadata": {"version": ver["id"], "category": "datapack_json"}
            }
            f.write(json.dumps(entry) + "\n")
            total_lines += 1

        # 8. Corrections d'erreurs & Migrations
        print("Génération corrections d'erreurs...")
        for _ in range(10000):
            ver = random.choice(ALL_VERSIONS)
            examples = generate_error_correction_example(ver)
            for ex in examples:
                entry = {
                    "messages": [
                        {"role": "system", "content": "Correcteur de commandes Minecraft."},
                        {"role": "user", "content": ex["prompt"]},
                        {"role": "assistant", "content": ex["response"]}
                    ],
                    "metadata": {"version": ver["id"], "category": "error_correction"}
                }
                f.write(json.dumps(entry) + "\n")
                total_lines += 1

        # 9. Bedrock Specifics
        print("Génération spécificités Bedrock...")
        for _ in range(10000):
            ver = random.choice(VERSIONS_BEDROCK)
            cmds = []
            # Commandes spécifiques Bedrock
            cmds.append(f"/event entity {generate_selector()} minecraft:become_angry")
            cmds.append(f"/mobevent minecraft:pillager_patrols_event true")
            cmds.append(f"/script event send my_custom_event")
            cmds.append(f"/camerashake add {generate_selector()} {random.uniform(0.1, 1.0)} {random.uniform(0.1, 1.0)} rotational")
            
            entry = {
                "messages": [
                    {"role": "system", "content": f"Expert Minecraft Bedrock {ver['id']}."},
                    {"role": "user", "content": "Commandes spécifiques Bedrock Edition."},
                    {"role": "assistant", "content": "\n".join(cmds)}
                ],
                "metadata": {"version": ver["id"], "category": "bedrock_specific"}
            }
            f.write(json.dumps(entry) + "\n")
            total_lines += 1
            
        # 10. Pre-Flattening Deep Dive (1.7-1.12)
        print("Génération approfondie Anciennes Versions (1.7-1.12)...")
        for _ in range(10000):
            ver = random.choice([v for v in ALL_VERSIONS if v["era"] == "pre-flattening"])
            # Syntaxe spécifique ancienne
            cmds = []
            cmds.append(f"/testfor {generate_selector()} {{CustomName:\"Test\"}}")
            cmds.append(f"/entitydata {generate_selector()} {{Health:100}}")
            cmds.append(f"/blockdata ~ ~ ~ {{Items:[{{Slot:0,id:1,Count:64}}]}}")
            cmds.append(f"/trigger obj set {random.randint(1,10)}") # Trigger existed but limited
            
            entry = {
                "messages": [
                    {"role": "system", "content": f"Expert Legacy Minecraft {ver['id']}."},
                    {"role": "user", "content": "Commandes pour version pré-1.13."},
                    {"role": "assistant", "content": "\n".join(cmds)}
                ],
                "metadata": {"version": ver["id"], "category": "legacy_pre_flattening"}
            }
            f.write(json.dumps(entry) + "\n")
            total_lines += 1

    print(f"Génération terminée ! Total de lignes écrites : {total_lines}")
    print(f"Fichier sauvegardé sous : {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
