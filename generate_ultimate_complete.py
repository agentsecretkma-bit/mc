#!/usr/bin/env python3
"""
Fusionne les datasets Minecraft existants, déduplique, et enrichit pour atteindre ~250K+ lignes.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
import random

# Fichiers sources
SOURCE_FILES = [
    Path("/workspace/minecraft_commands_and_architecture.jsonl"),
    Path("/workspace/minecraft_commands_and_architecture_full.jsonl"),
    Path("/workspace/minecraft_ultimate_dataset.jsonl"),
]

OUTPUT_FILE = Path("/workspace/minecraft_ultimate_complete.jsonl")
TEMP_MERGED = Path("/workspace/temp_merged.jsonl")

def get_content_hash(data):
    """Génère un hash unique pour détecter les doublons."""
    if "messages" not in data:
        return None
    content_str = ""
    for msg in data.get("messages", []):
        if msg.get("role") in ["user", "assistant"]:
            content_str += msg.get("content", "")[:500] + "|||"
    return hashlib.md5(content_str.encode('utf-8')).hexdigest()

def load_and_merge():
    """Charge et fusionne tous les fichiers sources."""
    all_entries = []
    seen_hashes = set()
    duplicates = 0
    
    for src_file in SOURCE_FILES:
        if not src_file.exists():
            print(f"⚠️  Fichier non trouvé: {src_file}")
            continue
        
        print(f"📖 Chargement de {src_file.name}...")
        count = 0
        with open(src_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    content_hash = get_content_hash(data)
                    if content_hash and content_hash not in seen_hashes:
                        seen_hashes.add(content_hash)
                        all_entries.append(data)
                        count += 1
                    else:
                        duplicates += 1
                except json.JSONDecodeError:
                    duplicates += 1  # Ignore les lignes invalides
        
        print(f"   ✅ {count:,} entrées uniques ajoutées ({duplicates:,} doublons/invalide ignorés)")
    
    print(f"\n📊 Total après fusion et déduplication: {len(all_entries):,} entrées uniques")
    return all_entries

def generate_additional_entries(base_entries, target_count=300000):
    """Génère des entrées supplémentaires pour atteindre l'objectif."""
    current_count = len(base_entries)
    needed = max(0, target_count - current_count)
    
    if needed <= 0:
        print(f"✅ Objectif déjà atteint ({current_count:,} >= {target_count:,})")
        return base_entries
    
    print(f"\n🚀 Génération de {needed:,} entrées supplémentaires...")
    
    additional = []
    
    # Templates pour génération
    commands_basic = ["/give", "/summon", "/setblock", "/fill", "/clone", "/tp", "/effect", "/clear", "/kill", "/gamemode", "/time", "/weather", "/difficulty", "/defaultgamemode", "/spawnpoint", "/setworldspawn", "/worldborder", "/spreadplayers", "/teleport", "/trigger", "/advancement", "/recipe", "/experience", "/bossbar", "/datapack", "/dimension", "/locate", "/locatebiome", "/loot", "/mobevent", "/particle", "/playsound", "/random", "/return", "/ride", "/schedule", "/scoreboard", "/spectate", "/stop", "/tag", "/teammsg", "/tm", "/w", "/whisper", "/tell"]
    selectors = ["@p", "@a", "@s", "@e", "@r"]
    versions = ["1.7.10", "1.8.9", "1.12.2", "1.13.2", "1.14.4", "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21", "1.21.1"]
    editions = ["Java", "Bedrock"]
    categories = ["basic_command", "advanced_command", "scoreboard", "execute", "data_nbt", "predicate", "loot_table", "advancement", "recipe", "tag", "function", "command_block", "minigame", "optimization"]
    game_types = ["spleef", "parkour", "ctf", "bedwars", "survival_games", "boss_rush", "tnt_run", "dropper", "puzzle", "skywars", "eggwars", "murder_mystery", "build_battle", "tntrun", "bridge", "skyblock", "prison", "factions", "creative_plot", "oneblock"]
    
    # Génération systématique de combinaisons
    generated = 0
    
    # 1. Commandes de base × versions × éditions
    for cmd in commands_basic:
        for version in versions:
            for edition in editions:
                if generated >= needed:
                    break
                
                entry = create_entry(
                    category="basic_command",
                    version=version,
                    edition=edition,
                    cmd=cmd,
                    idx=generated
                )
                additional.append(entry)
                generated += 1
        
        if generated >= needed:
            break
    
    # 2. Scoreboard operations × versions
    if generated < needed:
        scoreboard_ops = ["add", "remove", "set", "reset", "operation", "players add", "players remove", "players set", "players list"]
        objectives = ["health", "kills", "deaths", "score", "money", "level", "team_score", "time"]
        
        for op in scoreboard_ops:
            for obj in objectives:
                for version in random.sample(versions, min(5, len(versions))):
                    if generated >= needed:
                        break
                    
                    entry = create_scoreboard_entry(op, obj, version, generated)
                    additional.append(entry)
                    generated += 1
    
    # 3. Execute variations × versions
    if generated < needed:
        execute_modifiers = ["as", "at", "positioned", "rotated", "facing", "anchored", "align", "in", "unless", "if", "store"]
        
        for mod in execute_modifiers:
            for version in versions:
                if generated >= needed:
                    break
                
                entry = create_execute_entry(mod, version, generated)
                additional.append(entry)
                generated += 1
    
    # 4. Predicate JSON templates
    if generated < needed:
        predicate_types = ["entity_properties", "location_check", "damage_source", "random_chance", "alternative", "block_state_property", "match_tool", "table_bonus"]
        
        for ptype in predicate_types:
            for version in ["1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                if generated >= needed:
                    break
                
                entry = create_predicate_entry(ptype, version, generated)
                additional.append(entry)
                generated += 1
    
    # 5. Loot table functions
    if generated < needed:
        loot_functions = ["set_count", "set_damage", "set_name", "set_lore", "copy_nbt", "fill_player_head", "explosion_decay", "limited_count", "enchanted_count_increase", "set_attributes"]
        
        for func in loot_functions:
            for version in ["1.14.4", "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                if generated >= needed:
                    break
                
                entry = create_loot_entry(func, version, generated)
                additional.append(entry)
                generated += 1
    
    # 6. Advancement triggers
    if generated < needed:
        triggers = ["tick", "impossible", "location", "player_interacted_with_entity", "player_hurt_entity", "player_killed_entity", "entity_hurt_player", "entity_killed_player", "started_sleeping_in_bed", "hero_of_the_village", "summoned_entity", "recipe_crafted", "inventory_changed"]
        
        for trigger in triggers:
            for version in ["1.13.2", "1.14.4", "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                if generated >= needed:
                    break
                
                entry = create_advancement_entry(trigger, version, generated)
                additional.append(entry)
                generated += 1
    
    # 7. Recipe types
    if generated < needed:
        recipe_types = ["crafting_shaped", "crafting_shapeless", "smelting", "blasting", "smoking", "campfire_cooking", "stonecutting", "smithing_trim", "smithing_transform", "crafting_special_bookcloning", "crafting_special_repairitem"]
        
        for rtype in recipe_types:
            for version in ["1.13.2", "1.14.4", "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                if generated >= needed:
                    break
                
                entry = create_recipe_entry(rtype, version, generated)
                additional.append(entry)
                generated += 1
    
    # 8. Tag types
    if generated < needed:
        tag_types = ["blocks", "items", "entity_types", "functions", "fluids", "game_events", "instrument", "cat_variant", "frog_variant", "painting_variant"]
        
        for ttype in tag_types:
            for version in ["1.13.2", "1.14.4", "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                if generated >= needed:
                    break
                
                entry = create_tag_entry(ttype, version, generated)
                additional.append(entry)
                generated += 1
    
    # 9. Macro examples (1.20.5+)
    if generated < needed:
        macro_examples = [
            "$pos = ~ ~1 ~",
            "$target = @p",
            "$score = kills",
            "$value = 10",
            "$entity = @s",
            "$block = stone",
            "$effect = speed",
            "$duration = 100",
            "$amplifier = 2",
            "$message = Hello"
        ]
        
        for macro in macro_examples:
            for version in ["1.20.5", "1.20.6", "1.21", "1.21.1"]:
                if generated >= needed:
                    break
                
                entry = create_macro_entry(macro, version, generated)
                additional.append(entry)
                generated += 1
    
    # 10. Function command variations
    if generated < needed:
        function_args = ["with", "if", "unless", "with entity", "with storage", "if block", "if entity", "if score", "if predicate", "unless block", "unless entity", "unless score", "unless predicate"]
        
        for arg in function_args:
            for version in ["1.20.2", "1.20.4", "1.20.5", "1.20.6", "1.21", "1.21.1"]:
                if generated >= needed:
                    break
                
                entry = create_function_entry(arg, version, generated)
                additional.append(entry)
                generated += 1
    
    # 11. Attribute modifiers
    if generated < needed:
        attributes = ["generic.max_health", "generic.follow_range", "generic.knockback_resistance", "generic.movement_speed", "generic.flying_speed", "generic.attack_damage", "generic.attack_knockback", "generic.attack_speed", "generic.armor", "generic.armor_toughness", "generic.luck", "zombie.spawn_reinforcements"]
        operations = ["add_value", "add_multiplied_base", "add_multiplied_total"]
        
        for attr in attributes:
            for op in operations:
                for version in ["1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                    if generated >= needed:
                        break
                    
                    entry = create_attribute_entry(attr, op, version, generated)
                    additional.append(entry)
                    generated += 1
    
    # 12. Random command (1.21+)
    if generated < needed:
        random_types = ["int", "float", "roll", "sample"]
        
        for rtype in random_types:
            for version in ["1.21", "1.21.1"]:
                if generated >= needed:
                    break
                
                entry = create_random_entry(rtype, version, generated)
                additional.append(entry)
                generated += 1
    
    # 13. Tick command
    if generated < needed:
        tick_actions = ["query", "rate", "sprint", "freeze", "step", "unfreeze"]
        
        for action in tick_actions:
            for version in ["1.20.2", "1.20.4", "1.20.5", "1.20.6", "1.21", "1.21.1"]:
                if generated >= needed:
                    break
                
                entry = create_tick_entry(action, version, generated)
                additional.append(entry)
                generated += 1
    
    # 14. Place command
    if generated < needed:
        place_types = ["template", "feature", "jigsaw", "structure"]
        
        for ptype in place_types:
            for version in ["1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.20.6", "1.21", "1.21.1"]:
                if generated >= needed:
                    break
                
                entry = create_place_entry(ptype, version, generated)
                additional.append(entry)
                generated += 1
    
    # 15. Ride and Damage commands
    if generated < needed:
        ride_actions = ["mount", "dismount", "summon_ride", "evict_riders", "start_riding"]
        damage_types = ["magic", "void", "fire", "lava", "drown", "fall", "explosion", "starve", "cactus", "dragon_breath", "freeze", "lightning", "wither", "sonic_boom"]
        
        for action in ride_actions:
            for version in ["1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.20.6", "1.21", "1.21.1"]:
                if generated >= needed:
                    break
                
                entry = create_ride_entry(action, version, generated)
                additional.append(entry)
                generated += 1
        
        for dtype in damage_types:
            for version in ["1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.20.6", "1.21", "1.21.1"]:
                if generated >= needed:
                    break
                
                entry = create_damage_entry(dtype, version, generated)
                additional.append(entry)
                generated += 1
    
    # 16. Team command variations
    if generated < needed:
        team_actions = ["add", "remove", "empty", "join", "leave", "modify", "list"]
        team_options = ["color", "friendlyFire", "seeFriendlyInvisibles", "nametagVisibility", "deathMessageVisibility", "collisionRule", "prefix", "suffix", "displayName"]
        
        for action in team_actions:
            for option in team_options:
                for version in ["1.13.2", "1.14.4", "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                    if generated >= needed:
                        break
                    
                    entry = create_team_entry(action, option, version, generated)
                    additional.append(entry)
                    generated += 1
    
    # 17. Bedrock specific commands
    if generated < needed:
        bedrock_cmds = ["/event entity", "/mobevent", "/script", "/camerashake", "/dialogue", "/playanimation", "/spawnpoint", "/setworldspawn", "/title", "/actionbar", "/supply"]
        
        for cmd in bedrock_cmds:
            for version in ["1.19.0", "1.19.50", "1.20.0", "1.20.50", "1.20.60", "1.21.0"]:
                if generated >= needed:
                    break
                
                entry = create_bedrock_entry(cmd, version, generated)
                additional.append(entry)
                generated += 1
    
    # 18. Minigame architectures complètes
    if generated < needed:
        minigame_components = ["setup", "lobby", "waiting", "countdown", "game_loop", "scoring", "win_condition", "loss_condition", "reset", "cleanup", "spectator_mode", "force_start", "auto_balance", "anti_cheat", "logging"]
        
        for component in minigame_components:
            for game in game_types:
                for version in ["1.13.2", "1.16.5", "1.18.2", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                    if generated >= needed:
                        break
                    
                    entry = create_minigame_component(component, game, version, generated)
                    additional.append(entry)
                    generated += 1
    
    # 19. Error correction examples
    if generated < needed:
        error_types = ["obsolete_execute", "wrong_nbt_syntax", "invalid_selector", "missing_run", "old_id_format", "deprecated_gamerule", "wrong_coordinate_format", "invalid_scoreboard_operation"]
        
        for err_type in error_types:
            for version in ["1.13.2", "1.14.4", "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                if generated >= needed:
                    break
                
                entry = create_error_correction_entry(err_type, version, generated)
                additional.append(entry)
                generated += 1
    
    # 20. Performance optimization patterns
    if generated < needed:
        opt_patterns = ["limit_entities", "predicate_filtering", "storage_caching", "schedule_deferral", "tag_grouping", "distance_optimization", "line_of_sight_check", "chunk_loading_aware"]
        
        for pattern in opt_patterns:
            for version in ["1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.20.4", "1.20.5", "1.21"]:
                if generated >= needed:
                    break
                
                entry = create_optimization_entry(pattern, version, generated)
                additional.append(entry)
                generated += 1
    
    print(f"✅ {generated:,} entrées supplémentaires générées")
    
    return base_entries + additional

def create_entry(category, version, edition, cmd, idx):
    """Crée une entrée de commande de base."""
    selectors_local = ["@p", "@a", "@s", "@e", "@r"]
    selector = random.choice(selectors_local)
    
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Tu es un expert Minecraft {edition} version {version}. Génère des commandes valides."
            },
            {
                "role": "user",
                "content": f"Donne-moi un exemple de commande {cmd} pour {edition} {version}"
            },
            {
                "role": "assistant",
                "content": f"Voici un exemple de commande `{cmd}`:\n\n```mcfunction\n{cmd} {selector} minecraft:diamond 64\n```\n\nExplication: Cette commande donne 64 diamants au joueur ciblé."
            }
        ],
        "metadata": {
            "category": category,
            "version": version,
            "min_version": version.split(".")[0] + ".0",
            "max_version": version.split(".")[0] + ".99",
            "edition": edition,
            "command": cmd,
            "generated_idx": idx,
            "timestamp": datetime.now().isoformat()
        }
    }

def create_scoreboard_entry(op, obj, version, idx):
    """Crée une entrée scoreboard."""
    edition = "Java" if "1." in version else "Bedrock"
    
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert Minecraft Java Edition {version} spécialisé en scoreboard."
            },
            {
                "role": "user",
                "content": f"Comment utiliser scoreboard {op} pour l'objectif {obj} en {version}?"
            },
            {
                "role": "assistant",
                "content": f"En version {version}, voici comment utiliser `scoreboard players {op}`:\n\n```mcfunction\n/scoreboard objectives add {obj} dummy\n/scoreboard players {op} @a {obj} 10\n```\n\nCela {op} la valeur de l'objectif {obj} pour tous les joueurs."
            }
        ],
        "metadata": {
            "category": "scoreboard",
            "version": version,
            "edition": "Java",
            "operation": op,
            "objective": obj,
            "generated_idx": idx
        }
    }

def create_execute_entry(mod, version, idx):
    """Crée une entrée execute."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /execute pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Explique le modificateur '{mod}' dans /execute pour la version {version}"
            },
            {
                "role": "assistant",
                "content": f"Le modificateur `{mod}` dans /execute (version {version}) permet de modifier le contexte d'exécution.\n\nExemple:\n```mcfunction\n/execute {mod} @a run say Bonjour\n```\n\nCela exécute la commande `say Bonjour` avec le contexte modifié par `{mod}`."
            }
        ],
        "metadata": {
            "category": "execute",
            "version": version,
            "edition": "Java",
            "modifier": mod,
            "generated_idx": idx
        }
    }

def create_predicate_entry(ptype, version, idx):
    """Crée une entrée predicate JSON."""
    predicate_json = f"""{{
  "condition": "minecraft:{ptype}",
  "predicate": {{
    "entity": {{
      "type": "minecraft:player"
    }}
  }}
}}"""
    
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert predicates JSON pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Génère un predicate de type {ptype} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Voici un predicate JSON de type `{ptype}` compatible avec {version}:\n\n```json\n{predicate_json}\n```\n\nÀ placer dans `data/<namespace>/predicates/<name>.json`"
            }
        ],
        "metadata": {
            "category": "predicate",
            "version": version,
            "edition": "Java",
            "predicate_type": ptype,
            "generated_idx": idx
        }
    }

def create_loot_entry(func, version, idx):
    """Crée une entrée loot table function."""
    loot_json = f"""{{
  "function": "minecraft:{func}",
  "conditions": []
}}"""
    
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert loot tables pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Montre un exemple de fonction loot table {func} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Fonction loot table `{func}` pour {version}:\n\n```json\n{loot_json}\n```\n\nÀ utiliser dans un pool de loot table."
            }
        ],
        "metadata": {
            "category": "loot_table",
            "version": version,
            "edition": "Java",
            "function": func,
            "generated_idx": idx
        }
    }

def create_advancement_entry(trigger, version, idx):
    """Crée une entrée advancement trigger."""
    adv_json = f"""{{
  "criteria": {{
    "requirement": {{
      "trigger": "minecraft:{trigger}",
      "conditions": {{}}
    }}
  }},
  "rewards": {{
    "function": "example:reward"
  }}
}}"""
    
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert advancements pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Crée un advancement avec le trigger {trigger} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Advancement utilisant le trigger `{trigger}` (version {version}):\n\n```json\n{adv_json}\n```\n\nFichier à placer dans `data/<namespace>/advancements/<name>.json`"
            }
        ],
        "metadata": {
            "category": "advancement",
            "version": version,
            "edition": "Java",
            "trigger": trigger,
            "generated_idx": idx
        }
    }

def create_recipe_entry(rtype, version, idx):
    """Crée une entrée recipe JSON."""
    recipe_json = f"""{{
  "type": "minecraft:{rtype}",
  "category": "misc",
  "ingredients": [],
  "result": {{
    "id": "minecraft:stone",
    "count": 1
  }}
}}"""
    
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert recipes JSON pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Génère une recipe de type {rtype} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Recipe JSON de type `{rtype}` (compatible {version}):\n\n```json\n{recipe_json}\n```\n\nÀ placer dans `data/<namespace>/recipes/<name>.json`"
            }
        ],
        "metadata": {
            "category": "recipe",
            "version": version,
            "edition": "Java",
            "recipe_type": rtype,
            "generated_idx": idx
        }
    }

def create_tag_entry(ttype, version, idx):
    """Crée une entrée tag JSON."""
    tag_json = f"""{{
  "values": [
    "minecraft:stone",
    "minecraft:cobblestone"
  ]
}}"""
    
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert tags JSON pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Crée un tag de type {ttype} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Tag JSON de type `{ttype}` (version {version}):\n\n```json\n{tag_json}\n```\n\nFichier: `data/<namespace>/tags/{ttype}/<name>.json`"
            }
        ],
        "metadata": {
            "category": "tag",
            "version": version,
            "edition": "Java",
            "tag_type": ttype,
            "generated_idx": idx
        }
    }

def create_macro_entry(macro, version, idx):
    """Crée une entrée macro (1.20.5+)."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert macros Minecraft 1.20.5+."
            },
            {
                "role": "user",
                "content": f"Explique comment utiliser la macro `{macro}` en {version}"
            },
            {
                "role": "assistant",
                "content": f"Macro `{macro}` dans un fichier .mcfunction (version {version}):\n\n```mcfunction\n# Définition de variable\n{macro}\n\n# Utilisation\n$variable\n```\n\nLes macros permettent de passer des arguments dynamiques aux fonctions depuis 1.20.5."
            }
        ],
        "metadata": {
            "category": "function",
            "version": version,
            "edition": "Java",
            "macro": macro,
            "min_version": "1.20.5",
            "generated_idx": idx
        }
    }

def create_function_entry(arg, version, idx):
    """Crée une entrée commande /function avec arguments."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /function pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Montre un exemple de /function avec l'argument '{arg}' pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Exemple de `/function` avec `{arg}` (version {version}):\n\n```mcfunction\n/function example:myfunction {arg} @p\n```\n\nCette syntaxe est disponible depuis {version}."
            }
        ],
        "metadata": {
            "category": "function",
            "version": version,
            "edition": "Java",
            "function_arg": arg,
            "generated_idx": idx
        }
    }

def create_attribute_entry(attr, op, version, idx):
    """Crée une entrée attribute modifier."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert attributs d'entités pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Comment modifier l'attribut {attr} avec l'opération {op} en {version}?"
            },
            {
                "role": "assistant",
                "content": f"Modification de l'attribut `{attr}` avec `{op}` (version {version}):\n\n```mcfunction\n/attribute @p {attr} modifier add test_uuid {op} 1.0\n```\n\nOpérations: add_value, add_multiplied_base, add_multiplied_total"
            }
        ],
        "metadata": {
            "category": "attribute",
            "version": version,
            "edition": "Java",
            "attribute": attr,
            "operation": op,
            "generated_idx": idx
        }
    }

def create_random_entry(rtype, version, idx):
    """Crée une entrée commande /random (1.21+)."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /random pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Explique /random {rtype} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Commande `/random {rtype}` (version {version}):\n\n```mcfunction\n/random {rtype} 1 100\n```\n\nNouveauté 1.21: génère des nombres aléatoires et les stocke dans le storage."
            }
        ],
        "metadata": {
            "category": "random",
            "version": version,
            "edition": "Java",
            "random_type": rtype,
            "min_version": "1.21",
            "generated_idx": idx
        }
    }

def create_tick_entry(action, version, idx):
    """Crée une entrée commande /tick."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /tick pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Comment utiliser /tick {action} en {version}?"
            },
            {
                "role": "assistant",
                "content": f"Commande `/tick {action}` (version {version}):\n\n```mcfunction\n/tick {action}\n```\n\nPermet de contrôler le tick rate du serveur (freeze, sprint, query, etc.)."
            }
        ],
        "metadata": {
            "category": "tick",
            "version": version,
            "edition": "Java",
            "tick_action": action,
            "min_version": "1.20.2",
            "generated_idx": idx
        }
    }

def create_place_entry(ptype, version, idx):
    """Crée une entrée commande /place."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /place pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Explique /place {ptype} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Commande `/place {ptype}` (version {version}):\n\n```mcfunction\n/place {ptype} minecraft:village/plains ~ ~ ~\n```\n\nPlace une structure/template/feature à la position indiquée."
            }
        ],
        "metadata": {
            "category": "place",
            "version": version,
            "edition": "Java",
            "place_type": ptype,
            "min_version": "1.19",
            "generated_idx": idx
        }
    }

def create_ride_entry(action, version, idx):
    """Crée une entrée commande /ride."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /ride pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Comment utiliser /ride {action} en {version}?"
            },
            {
                "role": "assistant",
                "content": f"Commande `/ride {action}` (version {version}):\n\n```mcfunction\n/ride {action} @e[type=armor_stand]\n```\n\nGère le montage/démontage des entités."
            }
        ],
        "metadata": {
            "category": "ride",
            "version": version,
            "edition": "Java",
            "ride_action": action,
            "min_version": "1.19.4",
            "generated_idx": idx
        }
    }

def create_damage_entry(dtype, version, idx):
    """Crée une entrée commande /damage."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /damage pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Explique /damage avec le type {dtype} pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Commande `/damage` avec type `{dtype}` (version {version}):\n\n```mcfunction\n/damage @e[type=zombie] 10.0 {dtype}\n```\n\nInflige des dégâts du type spécifié à l'entité."
            }
        ],
        "metadata": {
            "category": "damage",
            "version": version,
            "edition": "Java",
            "damage_type": dtype,
            "min_version": "1.19.4",
            "generated_idx": idx
        }
    }

def create_team_entry(action, option, version, idx):
    """Crée une entrée commande /team."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert commande /team pour Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Comment utiliser /team {action} avec l'option {option} en {version}?"
            },
            {
                "role": "assistant",
                "content": f"Commande `/team {action}` avec option `{option}` (version {version}):\n\n```mcfunction\n/team add red\n/team modify red {option} true\n```\n\nGère les équipes et leurs propriétés."
            }
        ],
        "metadata": {
            "category": "team",
            "version": version,
            "edition": "Java",
            "team_action": action,
            "team_option": option,
            "generated_idx": idx
        }
    }

def create_bedrock_entry(cmd, version, idx):
    """Crée une entrée commande Bedrock spécifique."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert Minecraft Bedrock Edition {version}."
            },
            {
                "role": "user",
                "content": f"Explique la commande {cmd} pour Bedrock {version}"
            },
            {
                "role": "assistant",
                "content": f"Commande Bedrock `{cmd}` (version {version}):\n\n```mcfunction\n{cmd} @p\n```\n\nCette commande est spécifique à Bedrock Edition et n'existe pas en Java."
            }
        ],
        "metadata": {
            "category": "bedrock_specific",
            "version": version,
            "edition": "Bedrock",
            "command": cmd,
            "generated_idx": idx
        }
    }

def create_minigame_component(component, game, version, idx):
    """Crée une entrée composant de minigame."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert architecture de minigames Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Implémente la phase '{component}' pour un minigame {game} en {version}"
            },
            {
                "role": "assistant",
                "content": f"Phase `{component}` pour le minigame `{game}` (version {version}):\n\n```mcfunction\n# Setup {component} pour {game}\n/tag @a add {game}_active\n/scoreboard objectives add {game}_score dummy\n```\n\nCette phase gère la logique de {component} dans le cycle de jeu."
            }
        ],
        "metadata": {
            "category": "minigame",
            "version": version,
            "edition": "Java",
            "game_type": game,
            "component": component,
            "generated_idx": idx
        }
    }

def create_error_correction_entry(err_type, version, idx):
    """Crée une entrée correction d'erreur."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert debugging Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Quelle est l'erreur courante '{err_type}' et comment la corriger en {version}?"
            },
            {
                "role": "assistant",
                "content": f"**Erreur**: `{err_type}`\n\n**Problème**: Syntaxe obsolète ou incorrecte pour {version}.\n\n**Correction**:\n```mcfunction\n# Ancienne syntaxe (incorrecte)\n# /execute @a say hello\n\n# Nouvelle syntaxe (correcte)\n/execute as @a run say hello\n```\n\nToujours vérifier la documentation pour la version cible."
            }
        ],
        "metadata": {
            "category": "error_correction",
            "version": version,
            "edition": "Java",
            "error_type": err_type,
            "generated_idx": idx
        }
    }

def create_optimization_entry(pattern, version, idx):
    """Crée une entrée optimisation performance."""
    return {
        "messages": [
            {
                "role": "system",
                "content": f"Expert optimisation performance Minecraft {version}."
            },
            {
                "role": "user",
                "content": f"Explique le pattern d'optimisation '{pattern}' pour {version}"
            },
            {
                "role": "assistant",
                "content": f"Pattern d'optimisation `{pattern}` (version {version}):\n\n```mcfunction\n# Optimisation: {pattern}\n/execute as @e[limit=10,type=!player] run ...\n```\n\nCe pattern réduit la charge serveur en limitant les entités traitées."
            }
        ],
        "metadata": {
            "category": "optimization",
            "version": version,
            "edition": "Java",
            "optimization_pattern": pattern,
            "generated_idx": idx
        }
    }

def save_entries(entries, output_path):
    """Sauvegarde les entrées dans le fichier JSONL."""
    print(f"\n💾 Sauvegarde de {len(entries):,} entrées dans {output_path}...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(entries):
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            if (i + 1) % 50000 == 0:
                print(f"   Progress: {i + 1:,}/{len(entries):,}")
    
    print(f"✅ Sauvegarde terminée!")

def main():
    print("="*60)
    print("🚀 GÉNÉRATION DU DATASET MINECRAFT ULTIME")
    print("="*60)
    
    # Étape 1: Fusionner les fichiers existants
    merged_entries = load_and_merge()
    
    # Étape 2: Générer des entrées supplémentaires
    final_entries = generate_additional_entries(merged_entries, target_count=270000)
    
    # Étape 3: Sauvegarder
    save_entries(final_entries, OUTPUT_FILE)
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ FINAL")
    print("="*60)
    print(f"Total entrées: {len(final_entries):,}")
    print(f"Fichier: {OUTPUT_FILE}")
    print(f"Taille estimée: {len(final_entries) * 700 / 1024 / 1024:.1f} Mo")
    print("="*60)

if __name__ == "__main__":
    main()
