#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de dataset JSONL pour l'entraînement d'une IA spécialisée
dans les commandes Minecraft (Command Blocks) et l'architecture de jeux custom.

Couvre :
- Toutes les commandes de base avec leurs arguments (1.7 à 1.21+)
- Les sélecteurs et filtres avancés
- L'architecture de jeux (state machines, tick loops, reset)
- Les ruptures de versions (1.7→1.8, 1.9 combat, 1.13 Flattening, 1.16 Nether, 1.17 Caves, 1.19 Wild, 1.20 Trails, 1.20.5 Components, 1.21 Tricky Trials)
- Les différences Java/Bedrock
- Les bonnes pratiques anti-lag et optimisation
- Tous les minigames populaires
"""

import jsonlines
import random
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from itertools import product, combinations
from collections import defaultdict

# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

TARGET_LINES = 25000  # Objectif: 20K-25K lignes uniques
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

EDITIONS = ["java", "bedrock", "both"]

# Versions complètes avec ruptures majeures
JAVA_VERSIONS = [
    ("1.7.10", "pre-flattening", "IDs numériques"),
    ("1.8.9", "combat_update", "Boucliers, Elytra"),
    ("1.9", "combat_update", "Cooldown attaque, Boucliers"),
    ("1.10.2", "frostburn", "Magma blocks, Strays"),
    ("1.11.2", "exploration", "Illagers, Mansions"),
    ("1.12.2", "world_of_color", "Concrete, Parrots, last pre-flattening"),
    ("1.13", "flattening", "THE FLATTENING - IDs textuels, Water logging"),
    ("1.14", "village_pillage", "Villagers refactored, Crossbows"),
    ("1.15", "buzzing_buzzy", "Bees, Honey"),
    ("1.16", "nether_update", "Nether refactored, Piglins, Crying Obsidian"),
    ("1.17", "caves_cliffs_1", "Copper, Amethyst, Deepslate"),
    ("1.18", "caves_cliffs_2", "World height changed, New biomes"),
    ("1.19", "wild_update", "Deep Dark, Warden, Mangrove"),
    ("1.19.4", "execute_enhanced", "Execute amélioré"),
    ("1.20", "trails_tales", "Cherry Grove, Armor Trim, Camel"),
    ("1.20.2", "update_aquatic", "Fixes, Bamboo raft"),
    ("1.20.4", "stable_components", "Components stabilisés"),
    ("1.20.5", "components_major", "COMPONENTS MAJEURS - Remplacement NBT"),
    ("1.21", "tricky_trials", "Trial Chambers, Breeze, Copper Bulb"),
    ("1.21.2", "latest", "Dernière version stable")
]

BEDROCK_VERSIONS = [
    ("1.16.0", "nether_parity", "Parity Nether partielle"),
    ("1.17.0", "caves_parity", "Caves & Cliffs Pt1"),
    ("1.18.0", "caves_parity2", "Caves & Cliffs Pt2"),
    ("1.19.0", "wild_update", "Wild Update"),
    ("1.19.80", "beta_features", "Beta features"),
    ("1.20.0", "trails_tales", "Trails & Tales"),
    ("1.20.50", "components_beta", "Components en beta"),
    ("1.21.0", "tricky_trials", "Tricky Trials")
]

BREAKING_CHANGES = {
    "1.7_to_1.8": ["Nouveau système de bouclier", "Elytra ajouté"],
    "1.8_to_1.9": ["Cooldown d'attaque", "Bouclier fonctionnel", "End Cities"],
    "1.12_to_1.13": ["THE FLATTENING", "IDs numériques → textuels", "Refonte complète de /execute", "Water logging", "Block states"],
    "1.13_to_1.14": ["Villagers complètement refactorisés", "Crossbow", "Loom", "Cartography table"],
    "1.15_to_1.16": ["Nether completely redesigned", "Piglins, Hoglins", "New Nether blocks"],
    "1.16_to_1.17": ["Copper, Amethyst, Deepslate", "Goat, Axolotl", "New world generation prep"],
    "1.17_to_1.18": ["World height -64 to 320", "New cave generation", "Biome placement changed"],
    "1.18_to_1.19": ["Deep Dark biome", "Warden mob", "Mangrove swamp", "Frogs, Tadpoles"],
    "1.19_to_1.19.4": ["Execute if/unless block plus strict", "positioned as/rotated as ajoutés"],
    "1.19.4_to_1.20": ["Cherry Grove", "Armor Trim system", "Camel", "Sniffer"],
    "1.20.4_to_1.20.5": ["MAJOR COMPONENTS CHANGE", "NBT → Components transition", "custom_name au lieu de CustomName", "item components refactor"],
    "1.20.5_to_1.21": ["Trial Chambers", "Breeze mob", "Copper Bulb", "Mace weapon", "Vault block"]
}

CATEGORIES = [
    "basic_command",
    "selectors_basic",
    "selectors_advanced",
    "selectors_filters",
    "scoreboard_objectives",
    "scoreboard_players",
    "scoreboard_operations",
    "team_management",
    "tag_management",
    "entity_spawn",
    "entity_data",
    "entity_kill",
    "block_place",
    "block_fill",
    "block_clone",
    "block_set",
    "block_test",
    "item_give",
    "item_clear",
    "item_modify",
    "item_loot",
    "teleport_basic",
    "teleport_advanced",
    "effect_give",
    "effect_clear",
    "weather_time",
    "difficulty_gamemode",
    "player_input_trigger",
    "player_advancement",
    "player_title",
    "player_tellraw",
    "player_message",
    "data_get",
    "data_modify",
    "data_storage",
    "execute_as",
    "execute_at",
    "execute_positioned",
    "execute_rotated",
    "execute_facing",
    "execute_if_unless",
    "execute_store",
    "execute_complex",
    "function_call",
    "function_schedule",
    "function_reload",
    "predicate_define",
    "predicate_use",
    "bossbar_create",
    "bossbar_manage",
    "particle_spawn",
    "sound_play",
    "gamerule_set",
    "attribute_modify",
    "recipe_give",
    "experience_give",
    "spectator_teleport",
    "debug_profile",
    "server_ops",
    "server_whitelist",
    "server_ban",
    "server_save",
    "command_block_impulse",
    "command_block_repeat",
    "command_block_chain",
    "command_block_conditional",
    "command_block_always_active",
    "command_block_redstone_controlled",
    "command_block_combinations",
    "cb_timer_clock",
    "cb_detector_rail",
    "cb_pressure_plate",
    "cb_button_lever",
    "cb_observer_chain",
    "cb_fill_clock",
    "cb_entity_detection",
    "cb_block_detection",
    "cb_item_detection",
    "cb_player_proximity",
    "cb_scoreboard_trigger",
    "cb_multi_step_sequence",
    "cb_state_machine",
    "cb_event_system",
    "cb_broadcast_system",
    "cb_teleporter_network",
    "cb_shop_system",
    "cb_quest_system",
    "cb_dialogue_system",
    "cb_cutscene_system",
    "cb_minigame_controller",
    "cb_arena_manager",
    "cb_wave_spawner",
    "cb_loot_generator",
    "cb_randomizer",
    "cb_music_system",
    "cb_particle_effects",
    "cb_lighting_system",
    "cb_door_lock",
    "cb_password_system",
    "cb_elevator",
    "cb_hidden_door",
    "cb_trap_mechanism",
    "cb_shooting_range",
    "cb_parkour_checkpoint",
    "cb_race_timer",
    "cb_leaderboard_display",
    "cb_team_selector",
    "cb_kit_selector",
    "cb_inventory_manager",
    "cb_currency_system",
    "cb_stat_tracker",
    "cb_achievement_system",
    "cb_day_night_cycle",
    "cb_weather_control",
    "cb_mob_spawner_custom",
    "cb_boss_mechanic",
    "cb_puzzle_controller",
    "cb_maze_generator",
    "game_architecture_general",
    "minigame_spleef",
    "minigame_parkour",
    "minigame_ctf",
    "minigame_boss_rush",
    "minigame_survival_games",
    "minigame_bedwars",
    "minigame_tnt_run",
    "minigame_dropper",
    "minigame_puzzle",
    "minigame_skywars",
    "minigame_hunger_games",
    "minigame_build_battle",
    "minigame_hide_seek",
    "minigame_zombie_escape",
    "optimization_tick",
    "optimization_entity",
    "optimization_block",
    "optimization_scoreboard",
    "optimization_predicates",
    "version_migration",
    "java_bedrock_diff"
]

# Commandes de base avec leurs arguments
BASIC_COMMANDS = {
    "/give": {
        "syntax_java_1_13_1_20_4": "/give <target> <item> [count]",
        "syntax_java_1_20_5_plus": "/give <target> <item> [count] [components]",
        "syntax_bedrock": "/give <target: target> <itemName: Item> [amount: int] [data: int] [components: json]",
        "arguments": ["target", "item", "count", "components", "data"],
        "examples": [
            "/give @p minecraft:diamond 10",
            "/give @a[tag=vip] minecraft:netherite_sword 1 {Enchantments:[{id:sharpness,lvl:5}]}",
            "/give @s minecraft:stick{custom_model_data:1} 1"
        ]
    },
    "/summon": {
        "syntax_java_1_13_1_20_4": "/summon <entity> [x y z] [nbt]",
        "syntax_java_1_20_5_plus": "/summon <entity> [x y z] [components]",
        "syntax_bedrock": "/summon <entityType: string> [spawnPos: x y z] [spawnEvent: string] [nameTag: string]",
        "arguments": ["entity", "x", "y", "z", "nbt", "components", "spawnEvent", "nameTag"],
        "examples": [
            "/summon armor_stand ~ ~ ~ {CustomName:'\"Boss\"',NoGravity:1b}",
            "/summon creeper ~ ~1 ~ {powered:1b}",
            "/summon minecraft:villager ~ ~ ~ {VillagerData:{profession:farmer,level:5}}"
        ]
    },
    "/execute": {
        "syntax_java_1_13_plus": "/execute <subcommand> run <command>",
        "subcommands": ["as", "at", "positioned", "rotated", "facing", "if", "unless", "store", "align", "anchored", "in", "on"],
        "syntax_bedrock": "/execute <origin: target> <position: x y z> <command: command>",
        "arguments": ["subcommand", "target", "position", "command", "run"],
        "examples": [
            "/execute as @a at @s run give @s apple 1",
            "/execute at @p if block ~ ~-1 ~ grass_block run setblock ~ ~-1 ~ dirt",
            "/execute store result score @a kills run kill @e[type=creeper,distance=..5]"
        ]
    },
    "/fill": {
        "syntax": "/fill <x1 y1 z1> <x2 y2 z2> <block> [mode] [nbt|components]",
        "modes": ["replace", "destroy", "keep", "hollow", "outline"],
        "arguments": ["x1", "y1", "z1", "x2", "y2", "z2", "block", "mode", "nbt"],
        "examples": [
            "/fill -10 64 -10 10 65 10 snow_block replace air",
            "/fill ~-5 ~ ~-5 ~5 ~ ~5 stone hollow",
            "/fill 0 0 0 10 10 10 glass replace air"
        ]
    },
    "/setblock": {
        "syntax": "/setblock <x y z> <block> [mode] [nbt|components]",
        "modes": ["replace", "destroy", "keep"],
        "arguments": ["x", "y", "z", "block", "mode"],
        "examples": [
            "/setblock ~ ~-1 ~ grass_block",
            "/setblock 0 100 0 diamond_block keep",
            "/setblock ~ ~ ~ chest{Items:[{Slot:0,id:\"diamond\",Count:64}]}"
        ]
    },
    "/clone": {
        "syntax": "/clone <x1 y1 z1> <x2 y2 z2> <dest> [maskMode] [cloneMode]",
        "mask_modes": ["masked", "filtered"],
        "clone_modes": ["replace", "move", "normal", "force"],
        "arguments": ["x1", "y1", "z1", "x2", "y2", "z2", "dest", "maskMode", "cloneMode"],
        "examples": [
            "/clone -10 64 -10 10 65 10 0 100 0 masked replace normal",
            "/clone ~-5 ~ ~-5 ~5 ~ ~5 ~10 ~ ~ filtered move force"
        ]
    },
    "/tp": {
        "syntax_java": "/tp [target] <destination>",
        "syntax_bedrock": "/teleport <victim: target> <destination: target>|<destination: x y z> [checkForBlocks: boolean]",
        "arguments": ["target", "destination", "x", "y", "z", "entity"],
        "examples": [
            "/tp @a 0 100 0",
            "/tp @p @e[type=armor_stand,limit=1]",
            "/execute at @a run tp @s ~ ~5 ~"
        ]
    },
    "/effect": {
        "syntax_give": "/effect give <target> <effect> [seconds] [amplifier] [hideParticles]",
        "syntax_clear": "/effect clear <target> [effect]",
        "arguments": ["target", "effect", "seconds", "amplifier", "hideParticles"],
        "examples": [
            "/effect give @a speed 30 1 true",
            "/effect clear @a poison",
            "/effect give @p strength 60 2 false"
        ]
    },
    "/clear": {
        "syntax": "/clear [target] [item] [maxCount]",
        "arguments": ["target", "item", "maxCount"],
        "examples": [
            "/clear @a diamond_sword 0",
            "/clear @p minecraft:stone 64",
            "/execute store result score @a has_item run clear @s diamond 1"
        ]
    },
    "/scoreboard": {
        "subcommands_add": "/scoreboard objectives add <name> <criteria> [displayName]",
        "subcommands_set": "/scoreboard players set <target> <objective> <score>",
        "subcommands_add_score": "/scoreboard players add <target> <objective> <score>",
        "subcommands_operation": "/scoreboard players operation <targetA> <objA> <op> <targetB> <objB>",
        "operations": ["=", "+=", "-=", "*=", "/=", "%=", "<", ">", "><"],
        "arguments": ["name", "criteria", "displayName", "target", "objective", "score", "operation"],
        "examples": [
            "/scoreboard objectives add deaths deathCount",
            "/scoreboard players set @a money 100",
            "/scoreboard players operation @a kills *= @s multiplier"
        ]
    },
    "/tag": {
        "syntax_add": "/tag <target> add <tagName>",
        "syntax_remove": "/tag <target> remove <tagName>",
        "syntax_list": "/tag <target> list",
        "arguments": ["target", "tagName"],
        "examples": [
            "/tag @a add ready",
            "/tag @e[type=armor_stand] remove cleanup",
            "/execute if entity @a[tag=admin] run say Admin present!"
        ]
    },
    "/team": {
        "syntax_add": "/team add <team> [displayName]",
        "syntax_join": "/team join <team> [members]",
        "syntax_option": "/team option <team> <option> <value>",
        "options": ["color", "friendlyFire", "collisionRule", "deathMessageVisibility", "seeFriendlyInvisibles"],
        "arguments": ["team", "displayName", "members", "option", "value"],
        "examples": [
            "/team add Red \"Équipe Rouge\"",
            "/team join Red @a[tag=team_red]",
            "/team option Red friendlyFire false"
        ]
    },
    "/trigger": {
        "syntax_set": "/trigger <objective> set <value>",
        "syntax_add": "/trigger <objective> add <value>",
        "arguments": ["objective", "value"],
        "examples": [
            "/trigger vote set 1",
            "/trigger checkpoint add 1",
            "/execute if score @a vote matches 1 run function game:vote_yes"
        ]
    },
    "/data": {
        "syntax_get": "/data get <target> [<path>] [scale]",
        "syntax_modify": "/data modify <target> <path> <operation> <source>",
        "syntax_remove": "/data remove <target> <path>",
        "operations": ["set", "merge", "append", "prepend", "swap", "move"],
        "arguments": ["target", "path", "scale", "operation", "source"],
        "examples": [
            "/data get entity @p Health",
            "/data merge entity @e[type=armor_stand,limit=1] {CustomName:'\"Test\"'}",
            "/data modify storage mygame:main timer set from entity @s Health"
        ]
    },
    "/storage": {
        "syntax": "/data <operation> storage <id> <path> [value]",
        "arguments": ["id", "path", "operation"],
        "examples": [
            "/data modify storage mygame:config spawn_x set value 100",
            "/data get storage mygame:main timer"
        ]
    },
    "/title": {
        "syntax": "/title <target> times <fadeIn> <stay> <fadeOut>",
        "syntax_action": "/title <target> <action> <text>",
        "actions": ["title", "subtitle", "actionbar", "clear", "reset"],
        "arguments": ["target", "fadeIn", "stay", "fadeOut", "action", "text"],
        "examples": [
            "/title @a title {\"text\":\"Bienvenue!\",\"color\":\"gold\"}",
            "/title @a times 10 70 20",
            "/title @p actionbar {\"text\":\"Attention!\",\"color\":\"red\"}"
        ]
    },
    "/tellraw": {
        "syntax": "/tellraw <target> <message>",
        "arguments": ["target", "message"],
        "examples": [
            "/tellraw @a {\"text\":\"Hello World!\",\"color\":\"blue\"}",
            "/tellraw @p [{\"text\":\"Cliquez \",\"color\":\"green\"},{\"text\":\"ici\",\"color\":\"yellow\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/say Hi\"}}]"
        ]
    },
    "/gamerule": {
        "syntax": "/gamerule <rule> [value]",
        "rules": ["doDaylightCycle", "doWeatherCycle", "keepInventory", "mobGriefing", "commandBlockOutput", "doEntityDrops", "randomTickSpeed", "showDeathMessages"],
        "arguments": ["rule", "value"],
        "examples": [
            "/gamerule keepInventory true",
            "/gamerule commandBlockOutput false",
            "/gamerule randomTickSpeed 3"
        ]
    },
    "/time": {
        "syntax_set": "/time set <value>",
        "syntax_add": "/time add <value>",
        "syntax_query": "/time query <query>",
        "queries": ["daytime", "gametime", "day"],
        "arguments": ["value", "query"],
        "examples": [
            "/time set day",
            "/time set 6000",
            "/time query daytime"
        ]
    },
    "/weather": {
        "syntax": "/weather <type> [duration]",
        "types": ["clear", "rain", "thunder"],
        "arguments": ["type", "duration"],
        "examples": [
            "/weather clear",
            "/weather rain 6000",
            "/weather thunder"
        ]
    },
    "/difficulty": {
        "syntax": "/difficulty <difficulty>",
        "difficulties": ["peaceful", "easy", "normal", "hard"],
        "arguments": ["difficulty"],
        "examples": [
            "/difficulty hard",
            "/difficulty peaceful"
        ]
    },
    "/gamemode": {
        "syntax": "/gamemode <mode> [target]",
        "modes": ["survival", "creative", "adventure", "spectator"],
        "arguments": ["mode", "target"],
        "examples": [
            "/gamemode creative @a",
            "/gamemode survival",
            "/gamemode adventure @p"
        ]
    },
    "/kill": {
        "syntax": "/kill [target]",
        "arguments": ["target"],
        "examples": [
            "/kill @e[type=item]",
            "/kill @s",
            "/kill @e[type=!player,distance=..100]"
        ]
    },
    "/playsound": {
        "syntax": "/playsound <sound> <source> <target> [pos] [volume] [pitch] [minVolume]",
        "sources": ["master", "music", "record", "weather", "block", "hostile", "neutral", "player", "ambient", "voice"],
        "arguments": ["sound", "source", "target", "pos", "volume", "pitch", "minVolume"],
        "examples": [
            "/playsound minecraft:entity.experience_orb.pickup master @a ~ ~ ~ 1 1",
            "/playsound minecraft:music.creative music @a"
        ]
    },
    "/particle": {
        "syntax_java": "/particle <name> [pos] [delta] [speed] [count] [mode] [viewers]",
        "syntax_bedrock": "/particle <effectName: string> [position: x y z]",
        "arguments": ["name", "pos", "delta", "speed", "count", "mode"],
        "examples": [
            "/particle minecraft:flame ~ ~1 ~ 0.5 0.5 0.5 0.1 10",
            "/particle minecraft:soul ~ ~ ~ 0 0 0 0 100"
        ]
    },
    "/advancement": {
        "syntax_grant": "/advancement grant <target> everything|only|from|until|through|criteria",
        "syntax_revoke": "/advancement revoke <target> ...",
        "arguments": ["target", "advancement", "criteria"],
        "examples": [
            "/advancement grant @a only minecraft:story/root",
            "/advancement revoke @p everything"
        ]
    },
    "/function": {
        "syntax": "/function <name> [with <storage>]",
        "arguments": ["name", "storage"],
        "examples": [
            "/function mydatapack:game/start",
            "/function mydatapack:loop with storage mygame:main"
        ]
    },
    "/reload": {
        "syntax": "/reload",
        "arguments": [],
        "examples": ["/reload"]
    },
    "/schedule": {
        "syntax_function": "/schedule function <name> <time> [replace|append]",
        "syntax_clear": "/schedule clear <name>",
        "arguments": ["name", "time", "mode"],
        "examples": [
            "/schedule function mygame:tick 1t replace",
            "/schedule clear mygame:tick"
        ]
    },
    "/loot": {
        "syntax_give": "/loot give <lootTable> [stackModifier]",
        "syntax_spawn": "/loot spawn <pos> <lootTable>",
        "arguments": ["lootTable", "target", "pos", "stackModifier"],
        "examples": [
            "/loot give @p loot minecraft:chests/village_blacksmith",
            "/loot spawn ~ ~ ~ loot minecraft:entities/creeper"
        ]
    },
    "/item": {
        "syntax_modify": "/item modify <slot> [modifier]",
        "syntax_replace": "/item replace <slot> from <sourceSlot>",
        "arguments": ["slot", "modifier", "sourceSlot"],
        "examples": [
            "/item modify entity @p weapon.mainhand {Damage:0}",
            "/item replace block ~ ~-1 ~ container.0 from entity @s armor.head"
        ]
    },
    "/attribute": {
        "syntax": "/attribute <target> <attribute> <operation> [value]",
        "operations": ["base set", "base add", "base remove", "modifier add", "modifier remove", "modifier value"],
        "arguments": ["target", "attribute", "operation", "value"],
        "examples": [
            "/attribute @p generic.movement_speed base set 0.5",
            "/attribute @s generic.attack_damage modifier add test 1 0 add"
        ]
    },
    "/bossbar": {
        "syntax_add": "/bossbar add <id> <name>",
        "syntax_set": "/bossbar set <id> <property> <value>",
        "syntax_get": "/bossbar get <id> <property>",
        "syntax_remove": "/bossbar remove <id>",
        "syntax_list": "/bossbar list",
        "properties": ["name", "color", "style", "value", "max", "visible", "players"],
        "arguments": ["id", "name", "property", "value"],
        "examples": [
            "/bossbar add boss:health \"Boss Health\"",
            "/bossbar set boss:health value 50",
            "/bossbar set boss:health color red"
        ]
    },
    "/recipe": {
        "syntax_give": "/recipe give <target> everything|<recipe>",
        "syntax_take": "/recipe take <target> ...",
        "arguments": ["target", "recipe"],
        "examples": [
            "/recipe give @a minecraft:wooden_pickaxe",
            "/recipe take @p everything"
        ]
    },
    "/spreadplayers": {
        "syntax": "/spreadplayers <x> <z> <spreadDistance> <maxRange> <respectTeams> <targets>",
        "arguments": ["x", "z", "spreadDistance", "maxRange", "respectTeams", "targets"],
        "examples": [
            "/spreadplayers 0 0 5 50 true @a",
            "/spreadplayers 100 200 10 100 false @e[type=player]"
        ]
    },
    "/stopsound": {
        "syntax": "/stopsound <target> [source] [sound]",
        "arguments": ["target", "source", "sound"],
        "examples": [
            "/stopsound @a",
            "/stopsound @p music minecraft:music.creative"
        ]
    },
    "/ban": {
        "syntax": "/ban <player> [reason]",
        "arguments": ["player", "reason"],
        "examples": [
            "/ban PlayerName Cheating",
            "/ban Hacker123 X-Ray"
        ]
    },
    "/op": {
        "syntax": "/op <player>",
        "arguments": ["player"],
        "examples": ["/op AdminUser"]
    },
    "/deop": {
        "syntax": "/deop <player>",
        "arguments": ["player"],
        "examples": ["/deop FormerAdmin"]
    },
    "/whitelist": {
        "syntax": "/whitelist <add|remove|list|on|off>",
        "arguments": ["action", "player"],
        "examples": [
            "/whitelist add TrustedPlayer",
            "/whitelist on"
        ]
    }
}

# Sélecteurs avec leurs filtres
SELECTORS = {
    "@a": {"description": "Tous les joueurs", "filters": ["type", "distance", "tag", "scores", "limit", "sort", "gamemode", "team", "level", "x", "y", "z", "dx", "dy", "dz", "nbt", "predicate"]},
    "@p": {"description": "Joueur le plus proche", "filters": ["type", "distance", "tag", "scores", "limit", "gamemode", "team", "level", "x", "y", "z", "dx", "dy", "dz", "nbt", "predicate"]},
    "@e": {"description": "Toutes les entités", "filters": ["type", "distance", "tag", "scores", "limit", "sort", "x", "y", "z", "dx", "dy", "dz", "nbt", "predicate", "family"]},
    "@r": {"description": "Joueur aléatoire", "filters": ["type", "distance", "tag", "scores", "limit", "gamemode", "team", "level", "x", "y", "z", "dx", "dy", "dz", "nbt"]},
    "@s": {"description": "Entité exécutante", "filters": ["type", "tag", "scores", "nbt", "predicate"]}
}

# Types d'entités courantes
ENTITY_TYPES = [
    "player", "zombie", "skeleton", "creeper", "enderman", "spider", "pig", "cow",
    "sheep", "chicken", "villager", "armor_stand", "item", "arrow", "snowball",
    "egg", "experience_orb", "falling_block", "minecart", "boat", "horse", "donkey",
    "mule", "parrot", "wolf", "cat", "ocelot", "rabbit", "turtle", "dolphin",
    "phantom", "drowned", "husk", "stray", "blaze", "ghast", "magma_cube",
    "slime", "silverfish", "endermite", "shulker", "evoker", "vindicator", "illusioner",
    "witch", "wither", "ender_dragon", "iron_golem", "snow_golem", "guardian",
    "elder_guardian", "wandering_trader", "pillager", "ravager", "vex", "bee",
    "fox", "panda", "axolotl", "goat", "glow_squid", "allay", "frog", "tadpole",
    "warden", "camel", "sniffer", "armadillo", "bogged", "breeze", "wind_charge"
]

# Critères de scoreboard
SCOREBOARD_CRITERIA = [
    "dummy", "trigger", "deathCount", "playerKillCount", "totalKillCount", "health",
    "xp", "level", "food", "air", "armor", "teamkill.", "killedByTeam.",
    "minecraft.used:minecraft.air", "minecraft.used:minecraft.stone",
    "minecraft.broken:minecraft.diamond_pickaxe", "minecraft.crafted:minecraft.diamond_sword",
    "minecraft.picked_up:minecraft.diamond", "minecraft.dropped:minecraft.gold_ingot",
    "minecraft.killed:minecraft.zombie", "minecraft.killed_by:minecraft.creeper",
    "minecraft.custom:minecraft.mob_kills", "minecraft.custom:minecraft.sleep_in_bed",
    "minecraft.custom:minecraft.jump", "minecraft.custom:minecraft.sprint_one_cm"
]

# Templates de jeux
GAME_TEMPLATES = {
    "spleef": {
        "description": "Les joueurs doivent casser la plateforme sous les autres pour les faire tomber.",
        "phases": ["setup", "waiting", "playing", "ending", "reset"],
        "key_mechanics": ["block_break_detection", "fall_damage", "player_elimination", "last_man_standing"]
    },
    "parkour": {
        "description": "Course d'obstacles avec checkpoints et timer.",
        "phases": ["setup", "waiting", "playing", "finish", "reset"],
        "key_mechanics": ["checkpoint_system", "timer", "fail_detection", "leaderboard"]
    },
    "ctf": {
        "description": "Capture the Flag - deux équipes doivent voler le drapeau adverse.",
        "phases": ["setup", "waiting", "playing", "overtime", "ending", "reset"],
        "key_mechanics": ["team_system", "flag_capture", "respawn", "score_tracking", "overtime"]
    },
    "boss_rush": {
        "description": "Combat contre un boss avec phases et mécaniques spéciales.",
        "phases": ["setup", "phase1", "phase2", "phase3", "victory", "defeat", "reset"],
        "key_mechanics": ["boss_health_bar", "phase_transitions", "special_attacks", "reward_distribution"]
    },
    "survival_games": {
        "description": "Battle royale où le dernier survivant gagne.",
        "phases": ["setup", "grace_period", "playing", "shrinking_border", "ending", "reset"],
        "key_mechanics": ["chest_loot", "border_shrink", "player_elimination", "winner_declaration"]
    },
    "bedwars": {
        "description": "Protéger son lit tout en détruisant ceux des adversaires.",
        "phases": ["setup", "waiting", "playing", "bed_destroyed", "ending", "reset"],
        "key_mechanics": ["bed_protection", "resource_generators", "shop_system", "respawn_logic"]
    },
    "tnt_run": {
        "description": "Courir sur de la TNT qui s'active après un délai.",
        "phases": ["setup", "playing", "elimination", "ending", "reset"],
        "key_mechanics": ["tnt_activation", "fall_detection", "speed_boost", "last_player"]
    },
    "dropper": {
        "description": "Tomber dans un parcours sans mourir.",
        "phases": ["setup", "playing", "finish", "fail", "reset"],
        "key_mechanics": ["water_landing", "damage_prevention", "checkpoint", "timer"]
    },
    "puzzle": {
        "description": "Résoudre des énigmes avec des blocs et commandes.",
        "phases": ["setup", "hint1", "hint2", "solved", "reset"],
        "key_mechanics": ["block_detection", "item_requirement", "feedback_system", "progression"]
    }
}

# Ruptures de versions majeures
BREAKING_CHANGES = {
    "1.13": {
        "name": "The Flattening",
        "changes": [
            "IDs numériques remplacés par namespaced IDs (264 → minecraft:diamond)",
            "Réécriture complète de /execute",
            "NBT réorganisé",
            "Nouvelle syntaxe des sélecteurs"
        ]
    },
    "1.16": {
        "name": "Nether Update",
        "changes": [
            "Nouvelles entités et blocs",
            "Extension de /tag et /scoreboard",
            "Ajout de /locatebiome"
        ]
    },
    "1.17": {
        "name": "Caves & Cliffs Part 1",
        "changes": [
            "Ajout de /storage pour données temporaires",
            "Nouvelles entités axolotl, chèvre"
        ]
    },
    "1.19": {
        "name": "The Wild Update",
        "changes": [
            "Amélioration de execute if/unless block",
            "Ajout de positioned as/rotated as",
            "Bedrock aligné sur Java pour beaucoup de commandes"
        ]
    },
    "1.20.5": {
        "name": "Components System",
        "changes": [
            "Remplacement des NBT par components pour les items",
            "{CustomName:'...'} → {custom_name:'...'}",
            "Ancienne syntaxe NBT ignorée ou convertie"
        ]
    },
    "1.21": {
        "name": "Tricky Trials",
        "changes": [
            "Nouvelles entités bogged, breeze",
            "Amélioration des loot tables",
            "Nouveaux blocks et items"
        ]
    }
}

# Best practices
BEST_PRACTICES = [
    "always_use_namespaced_ids",
    "use_components_for_1_20_5+",
    "avoid_nbt_where_possible",
    "chain_as_then_at",
    "use_unless_for_negation",
    "prefer_predicates_over_block_checks",
    "always_use_type_filter",
    "limit_entity_targets",
    "avoid_sort_in_loops",
    "use_predicates_for_complex_logic",
    "use_components_1_20_5+",
    "validate_nbt_types",
    "avoid_complex_nbt_on_bedrock",
    "spawn_clean_then_modify",
    "use_replace_mode",
    "chunk_large_fills",
    "use_clone_for_reset",
    "avoid_fill_in_tick",
    "use_dummy_for_logic",
    "combine_with_tags",
    "limit_checks_per_tick",
    "use_for_binary_states",
    "clean_on_reset",
    "combine_with_scoreboard_for_values",
    "avoid_over_tagging",
    "disable_friendly_fire",
    "use_collision_rule_never",
    "reset_teams_on_round_end",
    "use_clear_0_for_detection",
    "hide_particles_for_clean_ui",
    "store_result_for_logic",
    "clear_effects_on_reset",
    "reset_score_after_use",
    "combine_with_advancements",
    "use_sidebar_for_menu",
    "validate_input_range",
    "align_before_teleport",
    "use_relative_coordinates_carefully",
    "test_in_target_version",
    "document_version_requirements",
    "use_functions_over_command_blocks",
    "implement_proper_reset",
    "provide_player_feedback",
    "optimize_selector_queries",
    "cache_frequent_lookups",
    "use_schedule_for_delayed_tasks",
    "avoid_entity_spam",
    "clean_up_markers",
    "handle_edge_cases",
    "graceful_degradation_bedrock"
]


@dataclass
class TrainingExample:
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]


def generate_system_message() -> str:
    """Génère un message système varié."""
    templates = [
        "Tu es un expert des commandes Minecraft. Réponds toujours en précisant l'édition (Java/Bedrock) et la version minimale. Fournis la syntaxe exacte, les arguments possibles, et les alternatives si obsolète.",
        "Expert commandes Minecraft. Détaille toujours la syntaxe, les arguments, et les différences entre versions.",
        "Tu es spécialisé dans les Command Blocks et l'architecture de jeux Minecraft. Explique clairement avec exemples versionnés.",
        "Assistant Minecraft expert. Pour chaque commande, précise l'édition, la version, et donne des exemples concrets.",
        "Spécialiste Minecraft Java & Bedrock. Réponds avec précision technique en incluant ruptures de versions et best practices."
    ]
    return random.choice(templates)


def generate_basic_command_example(cmd_name: str, cmd_data: Dict) -> TrainingExample:
    """Génère un exemple pour une commande de base."""
    
    edition = random.choice(["java", "bedrock", "both"])
    version = random.choice([v[0] for v in JAVA_VERSIONS]) if edition == "java" else random.choice([v[0] for v in BEDROCK_VERSIONS])
    
    # Question utilisateur
    question_templates = [
        f"Explique la commande {cmd_name} avec tous ses arguments",
        f"Comment utiliser {cmd_name} correctement ? Donne la syntaxe complète.",
        f"Détaille {cmd_name} et ses options pour {edition} {version}",
        f"Quelle est la syntaxe de {cmd_name} ? Quels sont les paramètres ?",
        f"Peux-tu m'expliquer {cmd_name} avec des exemples concrets ?"
    ]
    user_question = random.choice(question_templates)
    
    # Réponse assistant
    response_parts = [f"## {cmd_name}\n\n"]
    
    if "syntax" in cmd_data:
        response_parts.append(f"**Syntaxe :** `{cmd_data['syntax']}`\n\n")
    elif "syntax_java_1_13_1_20_4" in cmd_data:
        if edition == "java" and version in ["1.20.5", "1.21"]:
            response_parts.append(f"**Syntaxe Java {version}+ :** `{cmd_data.get('syntax_java_1_20_5_plus', cmd_data['syntax_java_1_13_1_20_4'])}`\n\n")
        else:
            response_parts.append(f"**Syntaxe :** `{cmd_data.get('syntax_java_1_13_1_20_4', '')}`\n\n")
    
    if "arguments" in cmd_data and cmd_data["arguments"]:
        args_sample = random.sample(cmd_data["arguments"], min(len(cmd_data["arguments"]), 4))
        response_parts.append(f"**Arguments :** {', '.join(f'`{a}`' for a in args_sample)}\n\n")
    
    if "examples" in cmd_data and cmd_data["examples"]:
        example = random.choice(cmd_data["examples"])
        response_parts.append(f"**Exemple :** `{example}`\n\n")
    
    if "subcommands" in cmd_data:
        subs = random.sample(cmd_data["subcommands"], min(len(cmd_data["subcommands"]), 5))
        response_parts.append(f"**Sous-commandes :** {', '.join(subs)}\n\n")
    
    if "modes" in cmd_data:
        response_parts.append(f"**Modes disponibles :** {', '.join(cmd_data['modes'])}\n\n")
    
    # Notes de version
    breaking_notes = []
    for ver, data in BREAKING_CHANGES.items():
        if ver <= version or ver in ["1.13", "1.20.5"]:
            breaking_notes.append(f"⚠️ **{ver} ({data['name']}) :** {random.choice(data['changes'])}")
    
    if breaking_notes:
        response_parts.append("\n".join(breaking_notes[:2]) + "\n\n")
    
    response_parts.append("**Best practices :** " + ", ".join(random.sample(BEST_PRACTICES, min(5, len(BEST_PRACTICES)))))
    
    assistant_response = "".join(response_parts)
    
    # Metadata
    category = "basic_command"
    tags = [cmd_name.replace("/", ""), "syntax", "arguments", edition]
    
    metadata = {
        "edition": edition,
        "min_version": version,
        "max_version": None,
        "category": category,
        "command_focus": cmd_name,
        "breaking_changes": ", ".join([bc for bc in BREAKING_CHANGES.keys()][:2]),
        "best_practices": random.sample(BEST_PRACTICES, 5),
        "tags": tags
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": assistant_response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_selector_example() -> TrainingExample:
    """Génère un exemple sur les sélecteurs."""
    
    selector = random.choice(list(SELECTORS.keys()))
    sel_data = SELECTORS[selector]
    filters_sample = random.sample(sel_data["filters"], min(len(sel_data["filters"]), 5))
    
    user_question = random.choice([
        f"Explique le sélecteur {selector} et ses filtres",
        f"Comment utiliser {selector} efficacement ? Liste les filtres disponibles.",
        f"Quels sont les filtres pour {selector} ? Donne des exemples.",
        f"Détaille {selector} ({sel_data['description']}) avec tous ses arguments de filtrage."
    ])
    
    response = f"## Sélecteur {selector}\n\n"
    response += f"**Description :** {sel_data['description']}\n\n"
    response += f"**Filtres disponibles :** {', '.join(f'`{f}`' for f in filters_sample)}\n\n"
    
    # Exemple concret
    filter_examples = []
    if "distance" in filters_sample:
        filter_examples.append("distance=..10")
    if "tag" in filters_sample:
        filter_examples.append("tag=ready")
    if "type" in filters_sample:
        filter_examples.append("type=!player")
    if "scores" in filters_sample:
        filter_examples.append("scores={kills=5..10}")
    if "limit" in filters_sample:
        filter_examples.append("limit=1")
    
    if filter_examples:
        full_selector = f"{selector}[{','.join(filter_examples)}]"
        response += f"**Exemple complet :** `{full_selector}`\n\n"
        response += f"**Utilisation :** `/execute as {full_selector} run say Hello!`\n\n"
    
    response += "**Notes :**\n"
    response += "- Java : supporte `sort`, `predicate`, `nbt`\n"
    response += "- Bedrock : `limit` s'écrit `c`, `sort` indisponible, `nbt` très limité\n"
    response += "- Performance : toujours filtrer par `type` et utiliser `limit`\n"
    
    metadata = {
        "edition": "both",
        "min_version": "1.13",
        "max_version": None,
        "category": "selectors",
        "command_focus": selector,
        "breaking_changes": "1.13+ modern selector syntax",
        "best_practices": ["always_use_type_filter", "limit_entity_targets", "avoid_sort_in_loops"],
        "tags": ["selectors", "targeting", "filters", "performance"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_game_architecture_example(game_name: str, game_data: Dict) -> TrainingExample:
    """Génère un exemple d'architecture de jeu complet."""
    
    edition = random.choice(["java", "both"])
    version = random.choice(["1.13", "1.16", "1.19", "1.20.4", "1.20.5", "1.21"])
    
    phase = random.choice(game_data["phases"])
    mechanic = random.choice(game_data["key_mechanics"])
    
    user_question = random.choice([
        f"Comment créer un système de {game_name.replace('_', ' ')} avec gestion des phases ?",
        f"Architecture pour un minigame {game_name.replace('_', ' ')} : explique la structure complète.",
        f"Détaille l'implémentation de {game_name.replace('_', ' ')} avec commande blocks.",
        f"Je veux faire un {game_name.replace('_', ' ')}. Quelle architecture recommandes-tu ?",
        f"Comment gérer les phases de {game_name.replace('_', ' ')} et le reset ?"
    ])
    
    response = f"## Architecture : {game_name.replace('_', ' ').title()}\n\n"
    response += f"**Description :** {game_data['description']}\n\n"
    response += f"**Phase actuelle :** `{phase}`\n\n"
    response += f"**Mécanique clé :** `{mechanic}`\n\n"
    
    # Structure du datapack
    response += "### Structure recommandée :\n"
    response += "```\n"
    response += "datapack/\n"
    response += "├── pack.mcmeta\n"
    response += "└── data/\n"
    response += "    └── mygame/\n"
    response += "        ├── functions/\n"
    response += "        │   ├── tick.mcfunction\n"
    response += "        │   ├── load.mcfunction\n"
    response += f"        │   ├── {phase}.mcfunction\n"
    response += "        │   ├── setup.mcfunction\n"
    response += "        │   ├── reset.mcfunction\n"
    response += "        │   └── utils/\n"
    response += "        └── predicates/\n"
    response += "            └── conditions.json\n"
    response += "```\n\n"
    
    # Exemples de commandes selon la phase
    response += "### Commandes clés :\n\n"
    
    if phase == "setup":
        response += "```mcfunction\n"
        response += "# Setup initial\n"
        response += "gamerule doDaylightCycle false\n"
        response += "gamerule doWeatherCycle false\n"
        response += "gamerule commandBlockOutput false\n"
        response += "scoreboard objectives add game_state dummy\n"
        response += "scoreboard objectives add players_alive dummy\n"
        response += "tag @a add waiting\n"
        response += "fill ~-10 ~ ~-10 ~10 ~ ~10 air replace stone\n"
        response += "```\n\n"
    elif phase == "playing":
        response += "```mcfunction\n"
        response += "# Boucle de jeu\n"
        response += "execute as @a[tag=playing] at @s run function mygame:player_loop\n"
        response += "execute if score global game_state matches 1 run function mygame:check_win\n"
        response += "scoreboard players add global timer 1\n"
        response += "execute store result score @a[scores={lives=1..}] lives_removed run clear @s air 0\n"
        response += "```\n\n"
    elif phase in ["ending", "victory", "finish"]:
        response += "```mcfunction\n"
        response += "# Fin de partie\n"
        response += "title @a title {\"text\":\"Victoire!\",\"color\":\"gold\"}\n"
        response += "tellraw @a [{\"text\":\"Vainqueur : \",\"color\":\"white\"},{\"selector\":\"@a[tag=winner]\",\"color\":\"yellow\"}]\n"
        response += "effect give @a[tag=winner] hero_of_the_village 60 1\n"
        response += "scoreboard players set global game_state 3\n"
        response += "schedule function mygame:reset 100t\n"
        response += "```\n\n"
    elif phase == "reset":
        response += "```mcfunction\n"
        response += "# Reset complet\n"
        response += "tag @a remove playing\n"
        response += "tag @a remove winner\n"
        response += "tag @a remove eliminated\n"
        response += "scoreboard players set global game_state 0\n"
        response += "scoreboard players set global timer 0\n"
        response += "kill @e[type=!player,tag=!protected]\n"
        response += "clone <template_coords> <dest_coords> replace normal\n"
        response += "function mygame:setup\n"
        response += "```\n\n"
    
    # Gestion spécifique de la mécanique
    response += f"### Implémentation : {mechanic}\n"
    
    if mechanic == "block_break_detection":
        response += "```mcfunction\n"
        response += "# Détection cassage de bloc\n"
        response += "execute as @a at @s if block ~ ~-1 ~ <platform_block> run function mygame:break_platform\n"
        response += "setblock ~ ~-1 ~ air destroy\n"
        response += "execute unless block ~ ~-2 ~ air run damage @s 1\n"
        response += "```\n"
    elif mechanic == "checkpoint_system":
        response += "```mcfunction\n"
        response += "# Checkpoint\n"
        response += "execute as @a at @s if block ~ ~-1 ~ gold_block run function mygame:set_checkpoint\n"
        response += "data modify storage mygame:checkpoints player_<uuid> set from entity @s Pos\n"
        response += "tellraw @s {\"text\":\"Checkpoint enregistré!\",\"color\":\"green\"}\n"
        response += "```\n"
    elif mechanic == "team_system":
        response += "```mcfunction\n"
        response += "# Système d'équipes\n"
        response += "team add Red\n"
        response += "team add Blue\n"
        response += "team option Red color red\n"
        response += "team option Blue color blue\n"
        response += "team join Red @a[tag=team_red]\n"
        response += "team join Blue @a[tag=team_blue]\n"
        response += "```\n"
    elif mechanic == "boss_health_bar":
        response += "```mcfunction\n"
        response += "# Barre de vie du boss\n"
        response += "bossbar add boss:health \"Boss\"\n"
        response += "bossbar set boss:health max 100\n"
        response += "execute store result bossbar boss:health value run data get entity @e[type=wither,limit=1] Health\n"
        response += "bossbar set boss:health color red\n"
        response += "bossbar set boss:health style notched_10\n"
        response += "```\n"
    elif mechanic == "respawn_logic":
        response += "```mcfunction\n"
        response += "# Respawn\n"
        response += "execute as @a[scores={lives=1..}] at @s run function mygame:respawn_player\n"
        response += "tp @s <spawn_point>\n"
        response += "effect clear @s\n"
        response += "scoreboard players remove @s lives 1\n"
        response += "```\n"
    else:
        response += "```mcfunction\n"
        response += "# Implémentation générique\n"
        response += "execute as @a[tag=playing] run function mygame:handle_" + mechanic + "\n"
        response += "```\n"
    
    response += "\n**Version notes :**\n"
    if version in ["1.20.5", "1.21"]:
        response += "- Utilise `components` au lieu de NBT pour les items\n"
        response += "- Syntaxe `/item modify` recommandée\n"
    else:
        response += "- NBT traditionnel avec `{tag:{...}}`\n"
    
    response += "\n**Optimisations :**\n"
    response += "- Utiliser predicates pour tests complexes\n"
    response += "- Limiter les @e avec type= et distance=\n"
    response += "- Cache les résultats de scoreboard fréquents\n"
    response += "- Utiliser /schedule au lieu de chaînes infinies\n"
    
    metadata = {
        "edition": edition,
        "min_version": version,
        "max_version": None,
        "category": f"game_architecture_{game_name}",
        "command_focus": f"full_game_{game_name}",
        "breaking_changes": ", ".join(list(BREAKING_CHANGES.keys())[:3]),
        "best_practices": random.sample(BEST_PRACTICES, 8),
        "tags": ["game-design", "architecture", "minigame", game_name, "datapack", "functions"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_scoreboard_example() -> TrainingExample:
    """Génère un exemple sur scoreboard."""
    
    criterion = random.choice(SCOREBOARD_CRITERIA)
    operation = random.choice(["=", "+=", "-=", "*=", "<", ">"])
    
    user_question = random.choice([
        f"Comment utiliser /scoreboard avec le critère {criterion} ?",
        f"Explique /scoreboard objectives et les opérations disponibles.",
        f"Comment créer et manipuler des scores pour un minigame ?",
        f"Détaille /scoreboard players operation avec exemples."
    ])
    
    response = "## Scoreboard System\n\n"
    response += "### Création d'objectif :\n"
    response += f"```mcfunction\n"
    response += f"scoreboard objectives add {criterion.split(':')[-1].split('.')[-1]} {criterion}\n"
    response += "```\n\n"
    
    response += "### Manipulation :\n"
    response += "```mcfunction\n"
    response += "scoreboard players set @a money 100\n"
    response += "scoreboard players add @a kills 1\n"
    response += "scoreboard players remove @a deaths 1\n"
    response += f"scoreboard players operation @a score1 {operation} @s score2\n"
    response += "scoreboard players reset @a\n"
    response += "```\n\n"
    
    response += "### Affichage :\n"
    response += "```mcfunction\n"
    response += "scoreboard objectives setdisplay sidebar <objective>\n"
    response += "scoreboard objectives setdisplay belowName <objective>\n"
    response += "```\n\n"
    
    response += "### Utilisation dans execute :\n"
    response += "```mcfunction\n"
    response += "execute if score @a kills matches 5.. run say Top killer!\n"
    response += "execute unless score @s deaths matches ..3 run function game:eliminate\n"
    response += "execute store result score @s health_formatted run data get entity @s Health\n"
    response += "```\n\n"
    
    response += "**Critères courants :**\n"
    response += "- `dummy` : Manuel, pour logique interne\n"
    response += "- `trigger` : Modifiable par les joueurs via /trigger\n"
    response += "- `deathCount` : Nombre de morts automatique\n"
    response += "- `playerKillCount` : Kills de joueurs\n"
    response += "- `minecraft.custom:...` : Statistiques personnalisées\n"
    
    metadata = {
        "edition": "both",
        "min_version": "1.13",
        "max_version": None,
        "category": "basic_command",
        "command_focus": "/scoreboard",
        "breaking_changes": "1.13+ syntax, Bedrock operation limits",
        "best_practices": ["use_dummy_for_logic", "combine_with_tags", "limit_checks_per_tick"],
        "tags": ["scoreboard", "tracking", "statistics", "logic", "state-machine"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_predicate_example() -> TrainingExample:
    """Génère un exemple sur les predicates."""
    
    predicate_types = ["location_check", "entity_check", "random_chance", "score_check", "alternative"]
    pred_type = random.choice(predicate_types)
    
    user_question = random.choice([
        "Comment créer et utiliser des predicates dans un datapack ?",
        "Explique les predicates avec exemples concrets.",
        "Quelle est la différence entre predicate et execute if ?",
        "Comment optimiser les conditions avec predicates ?"
    ])
    
    response = "## Predicates System\n\n"
    response += "Les predicates permettent de définir des conditions réutilisables dans un fichier JSON.\n\n"
    
    response += "### Structure du fichier :\n"
    response += "```json\n"
    response += "{\n"
    response += "  \"condition\": \"" + ("minecraft:" if pred_type != "alternative" else "") + random.choice(["location_check", "entity_properties", "random_chance", "score_check", "alternative"]) + "\",\n"
    
    if pred_type == "location_check":
        response += "  \"term\": {\n"
        response += "    \"location\": {\n"
        response += "      \"block\": {\n"
        response += "        \"tag\": \"minecraft:wool\"\n"
        response += "      },\n"
        response += "      \"dimension\": \"minecraft:overworld\"\n"
        response += "    }\n"
        response += "  }\n"
    elif pred_type == "entity_check":
        response += "  \"entity\": {\n"
        response += "    \"flags\": {\n"
        response += "      \"is_on_ground\": true\n"
        response += "    },\n"
        response += "    \"effects\": {\n"
        response += "      \"minecraft:speed\": {}\n"
        response += "    }\n"
        response += "  }\n"
    elif pred_type == "random_chance":
        response += "  \"chance\": 0.25,\n"
        response += "  \"condition\": \"minecraft:random_chance\"\n"
    elif pred_type == "score_check":
        response += "  \"scores\": {\n"
        response += "    \"kills\": {\n"
        response += "      \"min\": 5,\n"
        response += "      \"max\": 10\n"
        response += "    }\n"
        response += "  }\n"
    else:  # alternative
        response += "  \"terms\": [\n"
        response += "    {\"condition\": \"minecraft:entity_properties\", \"entity\": \"this\", \"predicate\": {\"flags\": {\"is_on_ground\": true}}},\n"
        response += "    {\"condition\": \"minecraft:score_check\", \"scores\": {\"health\": {\"min\": 10}}}\n"
        response += "  ]\n"
    
    response += "}\n"
    response += "```\n\n"
    
    response += "### Utilisation dans functions :\n"
    response += "```mcfunction\n"
    response += "execute if predicate mygame:conditions/on_ground run say On ground!\n"
    response += "execute unless predicate mygame:conditions/has_speed run effect give @s slowness 5 0\n"
    response += "execute if predicate mygame:conditions/lucky run loot give @s loot mygame:lucky_drop\n"
    response += "```\n\n"
    
    response += "**Avantages vs execute if :**\n"
    response += "- Conditions complexes dans un seul fichier\n"
    response += "- Réutilisable dans multiples functions\n"
    response += "- Meilleure lisibilité\n"
    response += "- Supporte OR logique avec 'alternative'\n"
    
    metadata = {
        "edition": "java",
        "min_version": "1.16",
        "max_version": None,
        "category": "predicate",
        "command_focus": "predicates",
        "breaking_changes": "1.16+ predicates, 1.19 enhanced conditions",
        "best_practices": ["prefer_predicates_over_block_checks", "use_predicates_for_complex_logic", "cache_frequent_lookups"],
        "tags": ["predicates", "conditions", "optimization", "datapack", "json"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_optimization_example() -> TrainingExample:
    """Génère un exemple sur l'optimisation et performance."""
    
    topics = [
        "anti_lag_entity_management",
        "efficient_selector_usage",
        "command_chain_optimization",
        "tick_loop_best_practices",
        "memory_management"
    ]
    topic = random.choice(topics)
    
    user_question = random.choice([
        "Comment optimiser mes commandes pour éviter le lag ?",
        "Best practices pour la performance des command blocks.",
        "Mes TPS chutent, comment améliorer l'efficacité ?",
        "Quelles sont les erreurs courantes à éviter en production ?",
        "Comment profiler et optimiser un datapack complexe ?"
    ])
    
    response = "## Optimisation & Performance\n\n"
    response += "### Sujet : " + topic.replace("_", " ").title() + "\n\n"
    
    if topic == "anti_lag_entity_management":
        response += "```mcfunction\n"
        response += "# ❌ MAUVAIS - Trop d'entités\n"
        response += "execute as @e run function game:process\n"
        response += "\n"
        response += "# ✅ BON - Filtrage strict\n"
        response += "execute as @e[type=armor_stand,tag=marker,distance=..50,limit=10] run function game:process\n"
        response += "\n"
        response += "# Nettoyage régulier\n"
        response += "kill @e[type=item,distance=..100]\n"
        response += "kill @e[type=experience_orb,distance=..200]\n"
        response += "tag @e[type=armor_stand] add cleanup\n"
        response += "kill @e[type=armor_stand,tag=cleanup]\n"
        response += "```\n"
    elif topic == "efficient_selector_usage":
        response += "```mcfunction\n"
        response += "# ❌ MAUVAIS - Selecteur large\n"
        response += "execute as @a run function game:check\n"
        response += "\n"
        response += "# ✅ BON - Filtrage précoce\n"
        response += "execute as @a[tag=playing,scores={game_state=1..},distance=..100] run function game:check\n"
        response += "\n"
        response += "# Utiliser predicates pour conditions complexes\n"
        response += "execute as @a if predicate mygame:is_playing run function game:check\n"
        response += "```\n"
    elif topic == "command_chain_optimization":
        response += "```mcfunction\n"
        response += "# ❌ MAUVAIS - Chaîne conditionnelle inefficace\n"
        response += "execute if score global state matches 1 run ...\n"
        response += "execute if score global state matches 1 run ...\n"
        response += "execute if score global state matches 1 run ...\n"
        response += "\n"
        response += "# ✅ BON - Exécution unique\n"
        response += "execute if score global state matches 1 run function game:batch_operations\n"
        response += "# Dans batch_operations.mcfunction :\n"
        response += "# ... toutes les opérations ...\n"
        response += "```\n"
    elif topic == "tick_loop_best_practices":
        response += "```mcfunction\n"
        response += "# tick.mcfunction\n"
        response += "gamerule doInsomnia false\n"
        response += "gamerule doTraderSpawning false\n"
        response += "\n"
        response += "# Traiter par lots\n"
        response += "execute as @e[type=!player,limit=50,sort=nearest] run function game:process_entity\n"
        response += "\n"
        response += "# Utiliser schedule pour tâches différées\n"
        response += "schedule function game:delayed_task 10t append\n"
        response += "```\n"
    else:  # memory_management
        response += "```mcfunction\n"
        response += "# Nettoyer storage inutilisé\n"
        response += "data remove storage mygame:temp_data\n"
        response += "\n"
        response += "# Reset scoreboard périodique\n"
        response += "scoreboard players reset @a[scores={temp_score=1..}] temp_score\n"
        response += "\n"
        response += "# Éviter NBT complexe persistant\n"
        response += "data remove entity @s CustomAttributes\n"
        response += "```\n"
    
    response += "\n**Règles d'or :**\n"
    response += "1. Toujours filtrer par `type` dans @e\n"
    response += "2. Utiliser `limit=` et `distance=`\n"
    response += "3. Privilégier predicates aux tests inline\n"
    response += "4. Grouper les opérations similaires\n"
    response += "5. Nettoyer régulièrement entités/tags/scores\n"
    response += "6. Éviter les boucles infinies de command blocks\n"
    response += "7. Utiliser functions + schedule plutôt que chains\n"
    response += "8. Profiler avec /debug ou spark\n"
    
    metadata = {
        "edition": "both",
        "min_version": "1.13",
        "max_version": None,
        "category": "optimization_performance",
        "command_focus": "optimization",
        "breaking_changes": "General best practices across versions",
        "best_practices": random.sample(BEST_PRACTICES, 10),
        "tags": ["optimization", "performance", "lag-prevention", "best-practices", "tps"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_version_comparison_example() -> TrainingExample:
    """Génère un exemple comparant plusieurs versions."""
    
    commands_with_changes = [
        ("/execute", "1.13", "Refonte complète : execute as/at/positioned/run"),
        ("/give", "1.20.5", "Passage NBT → Components"),
        ("/summon", "1.20.5", "NBT remplacé par components"),
        ("/data", "1.17", "Nouveau merge/get/modify"),
        ("/item", "1.17", "Ajouté pour modifier items"),
        ("/attribute", "1.16.2", "Nouvelle commande dédiée")
    ]
    
    cmd, version, change = random.choice(commands_with_changes)
    
    user_question = f"Quelle est la différence de {cmd} entre les versions ?"
    
    response = f"## Évolution de {cmd}\\n\\n"
    response += f"**Changement majeur en {version} :** {change}\\n\\n"
    
    if cmd == "/execute":
        response += "```mcfunction\\n"
        response += "# 1.12 et avant\\n"
        response += "execute @a ~ ~ ~ give @s diamond\\n"
        response += "\\n"
        response += "# 1.13+\\n"
        response += "execute as @a run give @s diamond\\n"
        response += "\\n"
        response += "# 1.19.4+ (améliorations)\\n"
        response += "execute as @a positioned ^ ^ ^1.5 if block ~ ~-1 ~ air run give @s feather\\n"
        response += "```\\n"
    elif cmd == "/give":
        response += "```mcfunction\\n"
        response += "# 1.13-1.20.4 (NBT)\\n"
        response += "/give @p minecraft:diamond_sword{Enchantments:[{id:sharpness,lvl:5}],display:{Name:'\\\"Épée Légendaire\\\"'}}\\n"
        response += "\\n"
        response += "# 1.20.5+ (Components)\\n"
        response += "/give @p minecraft:diamond_sword[enchantments={levels:{minecraft:sharpness:5}},custom_name='{\\\"text\\\":\\\"Épée Légendaire\\\"}']\\n"
        response += "```\\n"
    elif cmd == "/summon":
        response += "```mcfunction\\n"
        response += "# 1.13-1.20.4 (NBT)\\n"
        response += "/summon armor_stand ~ ~ ~ {CustomName:'\\\"Marker\\\"',Invisible:1b,NoGravity:1b}\\n"
        response += "\\n"
        response += "# 1.20.5+ (Components)\\n"
        response += "/summon armor_stand ~ ~ ~ {custom_data:{custom_name:'{\\\"text\\\":\\\"Marker\\\"}',invisible:1b,no_gravity:1b}}\\n"
        response += "```\\n"
    
    metadata = {
        "edition": "java",
        "min_version": "1.13",
        "max_version": None,
        "category": "version_migration",
        "command_focus": cmd,
        "breaking_changes": version,
        "best_practices": ["Always check version before using commands", "Use datapack pack_format to enforce version"],
        "tags": ["version", "migration", cmd.replace("/", ""), "breaking-change"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_command_block_example(cb_type: str) -> TrainingExample:
    """Génère un exemple sur les Command Blocks et leurs combinaisons."""
    
    cb_info = {
        "impulse": {
            "name": "Impulse (Orange)",
            "desc": "S'exécute UNE fois à la réception d'un signal redstone",
            "use_cases": ["Déclencheur unique", "Initialisation", "Réponse à événement"],
            "example": "Un bouton → /give @p diamond"
        },
        "repeat": {
            "name": "Repeat (Violet)",
            "desc": "S'exécute en boucle (20 fois/seconde par défaut) tant qu'alimenté",
            "use_cases": ["Boucle de jeu", "Détection continue", "Timer", "Effets permanents"],
            "example": "Toujours actif → /effect give @a[tag=playing] speed 2 1 true"
        },
        "chain": {
            "name": "Chain (Vert)",
            "desc": "S'exécute SI le bloc précédent a réussi (flèche directionnelle)",
            "use_cases": ["Séquences conditionnelles", "Chaînes de logique", "Exécution ordonnée"],
            "example": "Après un repeat → /scoreboard players add global ticks 1"
        },
        "conditional": {
            "name": "Conditionnel",
            "desc": "Ne s'exécute que si le bloc précédent a RENCONTRÉ UN SUCCÈS",
            "use_cases": ["Tests conditionnels", "Validation d'état", "Branchement logique"],
            "example": "Si testfor réussit → /tellraw @a \\\"Succès!\\\""
        },
        "unconditional": {
            "name": "Inconditionnel",
            "desc": "S'exécute toujours quand activé (défaut)",
            "use_cases": ["Exécution systématique", "Chaînes simples"],
            "example": "→ /summon creeper ~ ~ ~"
        },
        "always_active": {
            "name": "Toujours actif",
            "desc": "Pas besoin de signal redstone externe (pour Repeat/Chain)",
            "use_cases": ["Boucles autonomes", "Systèmes auto-alimentés"],
            "example": "Repeat: Toujours actif → function tick:main"
        },
        "redstone_controlled": {
            "name": "Contrôlé par Redstone",
            "desc": "Nécessite un signal redstone externe",
            "use_cases": ["Déclencheurs manuels", "Synchronisation externe"],
            "example": "Levier → Impulse → /tp @p spawn"
        }
    }
    
    info = cb_info.get(cb_type, cb_info["impulse"])
    
    user_questions = [
        f"Explique le command block {info['name']}",
        f"Comment utiliser un {info['name']} ?",
        f"À quoi sert un command block {info['name'].split()[0]} ?",
        f"Détaille le fonctionnement des {info['name']}",
        f"Quand utiliser un {info['name']} ?"
    ]
    
    response = f"## {info['name']}\\n\\n"
    response += f"**Description :** {info['desc']}\\n\\n"
    response += f"**Cas d'usage :** {', '.join(info['use_cases'])}\\n\\n"
    response += f"**Exemple concret :** {info['example']}\\n\\n"
    
    if cb_type == "impulse":
        response += "```mcfunction\\n"
        response += "# Configuration: Impulse, Redstone, Inconditionnel\\n"
        response += "# Déclencheur: Bouton ou Plaque de pression\\n"
        response += "/give @p[start_level=1] minecraft:netherite_sword\\n"
        response += "/title @p title \\\"Arme obtenue!\\\"\\n"
        response += "```\\n"
    elif cb_type == "repeat":
        response += "```mcfunction\\n"
        response += "# Configuration: Repeat, Always Active, Unconditional\\n"
        response += "# Boucle principale du jeu (tick.mcfunction équivalent)\\n"
        response += "execute as @a[tag=playing] at @s run function game:player_tick\\n"
        response += "execute as @e[type=armor_stand,tag=game_marker] at @s run function game:world_tick\\n"
        response += "scoreboard players add global timer 1\\n"
        response += "```\\n"
    elif cb_type == "chain":
        response += "```mcfunction\\n"
        response += "# Chaîne: Repeat → Chain → Chain\\n"
        response += "# Block 1 (Repeat): scoreboard players add ticks 1\\n"
        response += "# Block 2 (Chain): execute if score ticks matches 20 run scoreboard players add seconds 1\\n"
        response += "# Block 3 (Chain): execute if score seconds matches 60 run scoreboard players add minutes 1\\n"
        response += "```\\n"
    elif cb_type == "conditional":
        response += "```mcfunction\\n"
        response += "# Configuration: Chain, Conditional\\n"
        response += "# Block 1: testfor @a[scores={health=1..}]\\n"
        response += "# Block 2 (Conditional): tellraw @a \\\"Des joueurs sont en vie!\\\"\\n"
        response += "# Alternative moderne:\\n"
        response += "execute if entity @a[scores={health=1..}] run tellraw @a \\\"Joueurs détectés\\\"\\n"
        response += "```\\n"
    
    response += "\\n**Bonnes pratiques :**\\n"
    response += "- Nommer vos Command Blocks avec !setblock pour débogage\\n"
    response += "- Utiliser 'gamerule commandBlockOutput false' pour réduire le spam\\n"
    response += "- Privilégier les Functions (.mcfunction) aux longues chaînes\\n"
    response += "- Pour les boucles, Repeat + Always Active est plus efficace que l'horloge redstone\\n"
    
    metadata = {
        "edition": "both",
        "min_version": "1.9",
        "max_version": None,
        "category": f"command_block_{cb_type}",
        "command_focus": "command_block",
        "breaking_changes": "1.9: Ajout des Repeat et Chain blocks",
        "best_practices": ["Use functions over long chains", "Disable output for performance", "Name your command blocks"],
        "tags": ["command-block", cb_type, "redstone", "automation"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": random.choice(user_questions)},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_cb_combination_example(combination_type: str) -> TrainingExample:
    """Génère un exemple de combinaison de Command Blocks pour une tâche spécifique."""
    
    combinations = {
        "timer_clock": {
            "name": "Horloge / Timer",
            "description": "Compte le temps écoulé en ticks, secondes, minutes",
            "setup": [
                "1. Repeat (Always Active, Unconditional) → Incrémente ticks",
                "2. Chain (Conditional) → Si ticks=20, incrémente secondes",
                "3. Chain (Conditional) → Si secondes=60, incrémente minutes",
                "4. Chain (Conditional) → Affiche le temps si demandé"
            ],
            "commands": [
                "scoreboard objectives add ticks dummy",
                "scoreboard objectives add seconds dummy", 
                "scoreboard objectives add minutes dummy",
                "# Repeat block:",
                "scoreboard players add global ticks 1",
                "# Chain 1 (Conditional):",
                "execute if score global ticks matches 20 run scoreboard players add global seconds 1",
                "execute if score global ticks matches 20 run scoreboard players set global ticks 0",
                "# Chain 2 (Conditional):",
                "execute if score global seconds matches 60 run scoreboard players add global minutes 1",
                "execute if score global seconds matches 60 run scoreboard players set global seconds 0",
                "# Chain 3 (Affichage):",
                "title @a actionbar [{\\\"text\\\":\\\"Temps: \\\",\\\"color\\\":\\\"gold\\\"},{\\\"score\\\":{\\\"name\\\":\\\"global\\\",\\\"objective\\\":\\\"minutes\\\"}},{\\\"text\\\":\\\":\\\"},{\\\"score\\\":{\\\"name\\\":\\\"global\\\",\\\"objective\\\":\\\"seconds\\\"}}]"
            ]
        },
        "fill_clock": {
            "name": "Horloge Fill (Fill Clock)",
            "description": "Horloge ultra-rapide utilisant /fill et /testforblock",
            "setup": [
                "1. Impulse (Redstone) → Démarre l'horloge",
                "2. Repeat (Always Active) → Remplit un bloc d'air",
                "3. Chain → Teste si le bloc est air, sinon réactive"
            ],
            "commands": [
                "# Configuration classique Fill Clock:",
                "# Block A (Repeat, Always Active): fill ~ ~1 ~ ~ ~1 ~ air",
                "# Block B (Chain, Conditional): testforblock ~ ~1 ~ air",
                "# Block C (Chain, Conditional): fill ~ ~-1 ~ ~ ~-1 ~ redstone_block",
                "# Note: Cette technique est OBSOLÈTE en 1.13+",
                "# Préférer: schedule ou Repeat Always Active"
            ]
        },
        "entity_detector": {
            "name": "Détection d'Entité",
            "description": "Détecte les entités dans une zone et déclenche des actions",
            "setup": [
                "1. Repeat (Always Active) → Teste présence entités",
                "2. Chain (Conditional) → Si joueur détecté, action 1",
                "3. Chain (Conditional) → Si mob détecté, action 2",
                "4. Chain → Log dans scoreboard"
            ],
            "commands": [
                "scoreboard objectives add detected dummy",
                "# Repeat (Always Active):",
                "execute if entity @a[x=100,y=64,z=100,distance=..10] run scoreboard players add @p zone_entry 1",
                "# Chain 1 (Conditional):",
                "execute if entity @a[x=100,y=64,z=100,distance=..5] run title @a title \\\"Zone dangereuse!\\\"",
                "# Chain 2 (Conditional):",
                "execute if entity @e[type=!player,type=!armor_stand,x=100,y=64,z=100,distance=..10] run summon creeper ~ ~1 ~",
                "# Chain 3:",
                "execute store result score global entities_detected run data get entity @e[limit=1] Health"
            ]
        },
        "shop_system": {
            "name": "Système de Boutique",
            "description": "Permet aux joueurs d'acheter des objets avec une monnaie",
            "setup": [
                "1. Scoreboard: money (devise), purchases (suivi)",
                "2. Impulse (Button) → Vérifie solde et donne objet",
                "3. Chain (Conditional) → Si achat réussi, déduit argent",
                "4. Chain → Message de confirmation"
            ],
            "commands": [
                "scoreboard objectives add money dummy",
                "scoreboard objectives add purchases dummy",
                "# Button → Impulse:",
                "execute if score @p money matches 10.. run give @p diamond 1",
                "# Chain 1 (Conditional):",
                "execute if score @p money matches 10.. run scoreboard players remove @p money 10",
                "# Chain 2:",
                "execute if score @p money matches 10.. run tellraw @p [{\\\"text\\\":\\\"Achat réussi! -10$\\\",\\\"color\\\":\\\"green\\\"}]",
                "# Alternative avec ClickEvent (1.13+):",
                "tellraw @p [{\\\"text\\\":\\\"[Acheter Diamant - 10$]\\\",\\\"color\\\":\\\"gold\\\",\\\"clickEvent\\\":{\\\"action\\\":\\\"run_command\\\",\\\"value\\\":\\\"/trigger shop_diamond\\\"}}]"
            ]
        },
        "teleporter_network": {
            "name": "Réseau de Téléportation",
            "description": "Système de waypoints téléportant vers différentes zones",
            "setup": [
                "1. Pressure Plate → Détecte joueur",
                "2. Impulse → Téléporte vers destination",
                "3. Chain → Effets de téléportation",
                "4. Chain → Cooldown système"
            ],
            "commands": [
                "scoreboard objectives add tp_cooldown dummy",
                "# Pressure Plate → Impulse:",
                "execute if score @p tp_cooldown matches ..0 run tp @p 1000 100 1000",
                "# Chain 1 (Conditional):",
                "execute if score @p tp_cooldown matches ..0 run particle portal ~ ~1 ~ 1 1 1 0.5 10",
                "# Chain 2:",
                "execute if score @p tp_cooldown matches ..0 run playsound entity.enderman.teleport master @a ~ ~ ~ 1 1",
                "# Chain 3:",
                "scoreboard players set @p tp_cooldown 100",
                "# Repeat pour cooldown:",
                "scoreboard players remove @a[scores={tp_cooldown=1..}] tp_cooldown 1"
            ]
        },
        "boss_mechanic": {
            "name": "Mécanique de Boss",
            "description": "Gère les phases, vie, et attaques d'un boss",
            "setup": [
                "1. Repeat → Vérifie vie du boss",
                "2. Chain (Conditional) → Phase 1 (100%-70%)",
                "3. Chain (Conditional) → Phase 2 (70%-40%)",
                "4. Chain (Conditional) → Phase 3 (40%-0%)",
                "5. Chain → Gère attaques périodiques"
            ],
            "commands": [
                "scoreboard objectives add boss_health dummy",
                "scoreboard objectives add boss_phase dummy",
                "# Repeat (Always Active):",
                "execute store result score #boss boss_health run data get entity @e[tag=boss,limit=1] Health",
                "# Chain 1 (Conditional) - Phase 1:",
                "execute if score #boss boss_health matches 70.. run scoreboard players set #phase boss_phase 1",
                "# Chain 2 (Conditional) - Phase 2:",
                "execute if score #boss boss_health matches 40..69 run scoreboard players set #phase boss_phase 2",
                "# Chain 3 (Conditional) - Phase 3:",
                "execute if score #boss boss_health matches ..39 run scoreboard players set #phase boss_phase 3",
                "# Chain 4 - Attaque Phase 2:",
                "execute if score #phase boss_phase matches 2 if score global attack_timer matches 20.. run summon fireball ~ ~5 ~ {Motion:[0.0,-0.5,0.0]}",
                "# Chain 5:",
                "execute if score global attack_timer matches 20.. run scoreboard players set global attack_timer 0",
                "# Repeat pour timer:",
                "scoreboard players add global attack_timer 1"
            ]
        },
        "parkour_checkpoint": {
            "name": "Checkpoint Parkour",
            "description": "Système de checkpoints pour course d'obstacles",
            "setup": [
                "1. Pressure Plate → Enregistre checkpoint",
                "2. Impulse → Set tag et scoreboard",
                "3. Chain → Message personnalisé",
                "4. Death → Teleport au dernier checkpoint"
            ],
            "commands": [
                "scoreboard objectives add checkpoint dummy",
                "# Pressure Plate → Impulse:",
                "tag @p add cp_arena1_zone1",
                "scoreboard players set @p checkpoint 1",
                "# Chain 1:",
                "title @p title [{\\\"text\\\":\\\"✓ Checkpoint 1\\\",\\\"color\\\":\\\"green\\\"}]",
                "# Chain 2:",
                "tellraw @p [{\\\"text\\\":\\\"Prochaine zone: Sauts de slime!\\\",\\\"color\\\":\\\"gray\\\"}]",
                "# Système de mort (Repeat Always Active):",
                "execute as @a[tag=playing,tag=!cp_set] at @s run tp @s ~100 ~50 ~100"
            ]
        },
        "password_door": {
            "name": "Porte à Mot de Passe",
            "description": "Ouvre une porte secrète avec un code numérique",
            "setup": [
                "1. Buttons numérotés → Incrémentent code",
                "2. Repeat → Vérifie combinaison",
                "3. Chain (Conditional) → Si correct, ouvre porte",
                "4. Chain → Reset après délai"
            ],
            "commands": [
                "scoreboard objectives add password dummy",
                "scoreboard objectives add input_code dummy",
                "# Button 1 → Impulse:",
                "scoreboard players add @p input_code 1000",
                "# Button 2 → Impulse:",
                "scoreboard players add @p input_code 100",
                "# Repeat (Always Active):",
                "execute if score @p input_code matches 1234 run setblock ~ ~-1 ~ iron_door open",
                "# Chain 1 (Conditional):",
                "execute if score @p input_code matches 1234 run tellraw @p [{\\\"text\\\":\\\"Accès autorisé!\\\",\\\"color\\\":\\\"green\\\"}]",
                "# Chain 2 (Conditional):",
                "execute if score @p input_code matches 1234 run playsound block.iron_door.open master @p ~ ~ ~",
                "# Reset après 3 secondes (schedule ou chain temporelle):",
                "execute if score @p input_code matches 1234 run scoreboard players set @p input_code 0"
            ]
        },
        "wave_spawner": {
            "name": "Spawner de Vagues",
            "description": "Fait apparaître des vagues de mobs pour un minigame",
            "setup": [
                "1. Repeat → Compte temps entre vagues",
                "2. Chain (Conditional) → Si timer atteint, lance vague",
                "3. Chain → Spawne mobs selon configuration",
                "4. Chain → Annonce vague suivante"
            ],
            "commands": [
                "scoreboard objectives add wave dummy",
                "scoreboard objectives add wave_timer dummy",
                "scoreboard objectives add mobs_alive dummy",
                "# Repeat (Always Active):",
                "scoreboard players add global wave_timer 1",
                "# Chain 1 (Conditional) - Nouvelle vague:",
                "execute if score global wave_timer matches 600.. run scoreboard players add global wave 1",
                "# Chain 2:",
                "execute if score global wave_timer matches 600.. run scoreboard players set global wave_timer 0",
                "# Chain 3 - Spawn selon vague:",
                "execute if score global wave matches 1 run summon zombie ~ ~1 ~ {HandItems:[{id:\"iron_sword\",Count:1b},{}],ArmorItems:[{},{},{},{id:\"iron_helmet\",Count:1b}]}",
                "# Chain 4 - Annonce:",
                "execute if score global wave matches 1.. run title @a title [{\\\"text\\\":\\\"Vague \\\",\\\"color\\\":\\\"red\\\"},{\\\"score\\\":{\\\"name\\\":\\\"global\\\",\\\"objective\\\":\\\"wave\\\"}}]"
            ]
        },
        "leaderboard_display": {
            "name": "Classement en Temps Réel",
            "description": "Affiche le top joueurs sur un scoreboard visible",
            "setup": [
                "1. Repeat → Met à jour l'affichage",
                "2. Chain → Trie les scores",
                "3. Chain → Affiche sur sidebar ou bossbar",
                "4. Chain → Met à jour les positions"
            ],
            "commands": [
                "scoreboard objectives add kills dummy",
                "scoreboard objectives add deaths dummy",
                "scoreboard objectives setsidebar display kills",
                "# Repeat (Always Active):",
                "scoreboard objectives setdisplay sidebar kills",
                "# Chain - Top 3 avec tellraw:",
                "tellraw @a [{\\\"text\\\":\\\"=== CLASSEMENT ===\\\",\\\"color\\\":\\\"gold\\\",\\\"bold\\\":true}]",
                "execute store result score #top1 kills run scoreboard players operation #top1 kills = @a[kills_sort=highest,limit=1] kills",
                "# Alternative avec bossbar:",
                "bossbar add game:leaderboard \\\"Top Kills\\\"",
                "bossbar set game:leaderboard color yellow",
                "bossbar set game:leaderback visible true"
            ]
        }
    }
    
    combo = combinations.get(combination_type, combinations["timer_clock"])
    
    user_questions = [
        f"Comment créer un {combo['name']} avec des command blocks ?",
        f"Explique le système {combo['name']} étape par étape",
        f"Je veux faire un {combo['name']}, quelles commandes utiliser ?",
        f"Architecture pour un {combo['name']} dans Minecraft",
        f"Tutoriel complet: {combo['name']} avec command blocks"
    ]
    
    response = f"## {combo['name']}\\n\\n"
    response += f"**Description :** {combo['description']}\\n\\n"
    response += "### Configuration des Command Blocks:\\n\\n"
    
    for i, step in enumerate(combo['setup'], 1):
        response += f"{i}. {step}\\n"
    
    response += "\\n### Commandes:\\n\\n```mcfunction\\n"
    for cmd in combo['commands']:
        response += f"{cmd}\\n"
    response += "```\\n"
    
    response += "\\n**Notes importantes :**\\n"
    response += "- Adaptez les coordonnées (~ ~ ~) à votre installation\\n"
    response += "- Utilisez `gamerule commandBlockOutput false` pour réduire le spam\\n"
    response += "- Testez chaque bloc individuellement avant de connecter la chaîne\\n"
    response += "- Pour les systèmes complexes, privilégiez les .mcfunctions\\n"
    
    metadata = {
        "edition": "both",
        "min_version": "1.13",
        "max_version": None,
        "category": f"cb_combination_{combination_type}",
        "command_focus": "command_block_chain",
        "breaking_changes": "Varies by system",
        "best_practices": ["Test each block individually", "Use relative coordinates", "Consider using functions for complex systems"],
        "tags": ["command-block", "combination", combination_type, "tutorial", "automation"]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": random.choice(user_questions)},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)
    
    command = random.choice(["/give", "/summon", "/execute", "/data", "/item"])
    
    user_question = f"Quelle est la différence entre {command} en 1.12, 1.13-1.20.4 et 1.20.5+ ?"
    
    response = f"## Comparaison : {command} across versions\n\n"
    
    response += "### ⚫ 1.12.2 et antérieur :\n"
    if command == "/give":
        response += "```mcfunction\n"
        response += "/give @p 264 1 0 {display:{Name:\"Diamond\"}}\n"
        response += "# IDs numériques, NBT dans {tag:{...}}\n"
        response += "```\n"
    elif command == "/summon":
        response += "```mcfunction\n"
        response += "/summon Creeper ~ ~ ~ {powered:1,Fuse:100}\n"
        response += "# NBT direct sans namespace\n"
        response += "```\n"
    elif command == "/execute":
        response += "```mcfunction\n"
        response += "/execute @p ~ ~ ~ detect ~ ~-1 ~ grass 0 say On grass\n"
        response += "# Ancienne syntaxe monolithique\n"
        response += "```\n"
    elif command == "/data":
        response += "```mcfunction\n"
        response += "/entitydata @p {Health:20f}\n"
        response += "# /entitydata séparé, pas de /data merge\n"
        response += "```\n"
    elif command == "/item":
        response += "```mcfunction\n"
        response += "# N'existe pas en 1.12\n"
        response += "# Utiliser /replaceitem\n"
        response += "/replaceitem entity @p weapon.mainhand diamond_sword 1 0\n"
        response += "```\n"
    
    response += "\n### 🟠 1.13 - 1.20.4 :\n"
    if command == "/give":
        response += "```mcfunction\n"
        response += "/give @p minecraft:diamond 1 {display:{Name:'{\"text\":\"Diamond\"}'}}\n"
        response += "# Namespaced IDs, NBT dans {tag:{display:{...}}}\n"
        response += "```\n"
    elif command == "/summon":
        response += "```mcfunction\n"
        response += "/summon minecraft:creeper ~ ~ ~ {powered:1b,Fuse:100}\n"
        response += "# Namespaced IDs, types booléens avec b\n"
        response += "```\n"
    elif command == "/execute":
        response += "```mcfunction\n"
        response += "/execute as @p at @s if block ~ ~-1 ~ minecraft:grass_block run say On grass\n"
        response += "# Nouvelle syntaxe modulaire avec subcommands\n"
        response += "```\n"
    elif command == "/data":
        response += "```mcfunction\n"
        response += "/data merge entity @p {Health:20f}\n"
        response += "# /data unifié pour entities, blocks, storage\n"
        response += "```\n"
    elif command == "/item":
        response += "```mcfunction\n"
        response += "/item replace entity @p weapon.mainhand with minecraft:diamond_sword 1\n"
        response += "# Disponible depuis 1.17\n"
        response += "```\n"
    
    response += "\n### 🟢 1.20.5+ :\n"
    if command == "/give":
        response += "```mcfunction\n"
        response += "/give @p minecraft:diamond 1 {custom_name:'{\"text\":\"Diamond\"}',rarity:epic}\n"
        response += "# Components system remplace NBT\n"
        response += "# custom_name au lieu de display.Name\n"
        response += "```\n"
    elif command == "/summon":
        response += "```mcfunction\n"
        response += "/summon minecraft:creeper ~ ~ ~ {custom_name:'{\"text\":\"Powered\"}',ignited:1b}\n"
        response += "# Components pour entités également\n"
        response += "```\n"
    elif command == "/execute":
        response += "```mcfunction\n"
        response += "/execute as @p at @s if block ~ ~-1 ~ minecraft:grass_block run say On grass\n"
        response += "# Syntaxe stable depuis 1.13\n"
        response += "```\n"
    elif command == "/data":
        response += "```mcfunction\n"
        response += "/data merge entity @p {health:20f}\n"
        response += "# NBT reste pour entités/blocs, components pour items\n"
        response += "```\n"
    elif command == "/item":
        response += "```mcfunction\n"
        response += "/item modify entity @p weapon.mainhand {custom_name:'{\"text\":\"Épée\"}'}\n"
        response += "# Components system intégré\n"
        response += "```\n"
    
    response += "\n**Points clés :**\n"
    response += "- 1.13 : The Flattening (IDs numériques → namespaced)\n"
    response += "- 1.13 : Réécriture complète de /execute\n"
    response += "- 1.20.5 : Components system (NBT → components pour items)\n"
    response += "- Toujours tester dans la version cible\n"
    
    metadata = {
        "edition": "java",
        "min_version": "1.12",
        "max_version": "1.21",
        "category": "version_comparison",
        "command_focus": command,
        "breaking_changes": "1.13 flattening, 1.20.5 components",
        "best_practices": ["always_use_namespaced_ids", "use_components_for_1_20_5+", "test_in_target_version", "document_version_requirements"],
        "tags": ["version-history", "breaking-changes", "migration", command.replace("/", "")]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def generate_bedrock_vs_java_example() -> TrainingExample:
    """Génère un exemple comparant Java et Bedrock."""
    
    command = random.choice(["/execute", "/scoreboard", "/tag", "/summon", "/fill"])
    
    user_question = f"Quelle est la différence entre {command} sur Java et Bedrock Edition ?"
    
    response = f"## {command} : Java vs Bedrock\n\n"
    
    response += "### 🟦 Java Edition :\n"
    if command == "/execute":
        response += "```mcfunction\n"
        response += "/execute as @a at @s if predicate mygame:on_ground run function game:jump_check\n"
        response += "# Supporte predicates, store, align, anchored, in, on\n"
        response += "```\n"
    elif command == "/scoreboard":
        response += "```mcfunction\n"
        response += "/scoreboard players operation @a kills *= @s multiplier\n"
        response += "# Toutes les opérations mathématiques supportées\n"
        response += "```\n"
    elif command == "/tag":
        response += "```mcfunction\n"
        response += "/tag @e[type=armor_stand] add marker\n"
        response += "# Tags illimités, toutes entités\n"
        response += "```\n"
    elif command == "/summon":
        response += "```mcfunction\n"
        response += "/summon minecraft:armor_stand ~ ~ ~ {NoGravity:1b,Marker:1b,Invisible:1b}\n"
        response += "# NBT complet, toutes les entités\n"
        response += "```\n"
    elif command == "/fill":
        response += "```mcfunction\n"
        response += "/fill ~-5 ~ ~-5 ~5 ~ ~5 stone replace air\n"
        response += "# Tous les modes supportés\n"
        response += "```\n"
    
    response += "\n### 🟩 Bedrock Edition :\n"
    if command == "/execute":
        response += "```mcfunction\n"
        response += "/execute @a ~ ~ ~ detect ~ ~-1 ~ grass_block 0 say On grass\n"
        response += "# Syntaxe legacy encore utilisée\n"
        response += "# Predicates NON supportés\n"
        response += "# store, align limités\n"
        response += "```\n"
    elif command == "/scoreboard":
        response += "```mcfunction\n"
        response += "/scoreboard players operation @a kills = @s kills\n"
        response += "# operation très limité (=, +, - seulement)\n"
        response += "# Utiliser tags + conditions comme alternative\n"
        response += "```\n"
    elif command == "/tag":
        response += "```mcfunction\n"
        response += "/tag @a add marker\n"
        response += "# Supporté mais certaines entités limitées\n"
        response += "```\n"
    elif command == "/summon":
        response += "```mcfunction\n"
        response += "/summon armor_stand ~ ~ ~\n"
        response += "# NBT très limité\n"
        response += "# Utiliser /event entity pour comportements\n"
        response += "```\n"
    elif command == "/fill":
        response += "```mcfunction\n"
        response += "/fill ~-5 ~ ~-5 ~5 ~ ~5 stone 0 replace air\n"
        response += "# Data value requis (0)\n"
        response += "```\n"
    
    response += "\n**Différences clés :**\n"
    response += "- Java : Features complètes, predicates, datapacks avancés\n"
    response += "- Bedrock : Syntaxe parfois différente, features limitées\n"
    response += "- Bedrock : Utilise /event entity au lieu de NBT complexe\n"
    response += "- Cross-platform : Tester les deux éditions\n"
    response += "- Alternative Bedrock : Plus de tags + scoreboard, moins de NBT\n"
    
    metadata = {
        "edition": "both",
        "min_version": "1.13",
        "max_version": None,
        "category": "edition_comparison",
        "command_focus": command,
        "breaking_changes": "Java/Bedrock feature divergence",
        "best_practices": ["graceful_degradation_bedrock", "test_in_target_version", "avoid_complex_nbt_on_bedrock"],
        "tags": ["java", "bedrock", "comparison", "cross-platform", command.replace("/", "")]
    }
    
    messages = [
        {"role": "system", "content": generate_system_message()},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": response}
    ]
    
    return TrainingExample(messages=messages, metadata=metadata)


def main():
    """Génère le dataset JSONL complet."""
    
    output_file = "minecraft_commands_and_architecture_full.jsonl"
    
    examples = []
    
    print("Génération du dataset Minecraft Commands & Architecture...")
    
    # 1. Commandes de base (environ 800 exemples)
    print("  - Commandes de base...")
    for cmd_name, cmd_data in BASIC_COMMANDS.items():
        for _ in range(20):  # 20 variations par commande
            try:
                ex = generate_basic_command_example(cmd_name, cmd_data)
                examples.append(ex)
            except Exception as e:
                print(f"    Erreur pour {cmd_name}: {e}")
    
    # 2. Sélecteurs (environ 300 exemples)
    print("  - Sélecteurs...")
    for _ in range(300):
        examples.append(generate_selector_example())
    
    # 3. Scoreboard (environ 200 exemples)
    print("  - Scoreboard...")
    for _ in range(200):
        examples.append(generate_scoreboard_example())
    
    # 4. Predicates (environ 150 exemples)
    print("  - Predicates...")
    for _ in range(150):
        examples.append(generate_predicate_example())
    
    # 5. Architecture de jeux (environ 1000 exemples)
    print("  - Architecture de jeux...")
    for game_name, game_data in GAME_TEMPLATES.items():
        for _ in range(100):  # 100 variations par jeu
            examples.append(generate_game_architecture_example(game_name, game_data))
    
    # 6. Optimisation (environ 300 exemples)
    print("  - Optimisation...")
    for _ in range(300):
        examples.append(generate_optimization_example())
    
    # 7. Comparaisons de versions (environ 400 exemples)
    print("  - Comparaisons versions...")
    for _ in range(400):
        examples.append(generate_version_comparison_example())
    
    # 8. Comparaisons Java/Bedrock (environ 300 exemples)
    print("  - Comparaisons Java/Bedrock...")
    for _ in range(300):
        examples.append(generate_bedrock_vs_java_example())
    
    # 9. Command Blocks types (environ 700 exemples - 7 types x 100)
    print("  - Command Blocks (types)...")
    cb_types = ["impulse", "repeat", "chain", "conditional", "unconditional", "always_active", "redstone_controlled"]
    for cb_type in cb_types:
        for _ in range(100):
            examples.append(generate_command_block_example(cb_type))
    
    # 10. Combinaisons de Command Blocks (environ 1000 exemples - 10 combinaisons x 100)
    print("  - Combinaisons Command Blocks...")
    cb_combinations = ["timer_clock", "fill_clock", "entity_detector", "shop_system", 
                       "teleporter_network", "boss_mechanic", "parkour_checkpoint", 
                       "password_door", "wave_spawner", "leaderboard_display"]
    for combo_type in cb_combinations:
        for _ in range(100):
            examples.append(generate_cb_combination_example(combo_type))
    
    # Mélanger pour éviter le biais
    print("Mélange des exemples...")
    random.shuffle(examples)
    
    # Écrire le fichier JSONL
    print(f"Écriture de {len(examples)} exemples dans {output_file}...")
    with jsonlines.open(output_file, mode='w') as writer:
        for ex in examples:
            writer.write({
                "messages": ex.messages,
                "metadata": ex.metadata
            })
    
    print(f"✅ Dataset généré avec succès : {len(examples)} exemples")
    print(f"📁 Fichier : {output_file}")
    
    # Validation rapide
    print("\nValidation...")
    with jsonlines.open(output_file, mode='r') as reader:
        count = sum(1 for _ in reader)
    print(f"✓ {count} lignes validées")


if __name__ == "__main__":
    main()
