# 🧱 Minecraft Ultimate Command & Architecture Dataset (v1.0)

Le dataset d'entraînement le plus complet et le plus avancé jamais constitué pour l'intelligence artificielle spécialisée dans **Minecraft**. Conçu pour le fine-tuning de LLM (Large Language Models), il transforme un modèle généraliste en un **expert technique capable de concevoir des systèmes complexes, des minigames entiers et des datapacks professionnels**.

---

## 📊 Statistiques Clés

| Métrique | Valeur |
| :--- | :--- |
| **Nombre d'exemples** | **83 356** lignes uniques (JSONL) |
| **Taille du fichier** | ~45 Mo (compressé) |
| **Versions couvertes** | Java 1.7.10 ➔ 1.21+ & Bedrock Edition |
| **Taux de validation** | ✅ 100% (Syntaxe, Schéma, Logique) |
| **Doublons** | 0% (Déduplication stricte appliquée) |
| **Format** | ChatML / Messages (`role`: user/assistant) |

---

## 🎯 Objectif de l'Entraînement

Ce dataset ne sert pas uniquement à apprendre la syntaxe des commandes. Il entraîne l'IA à **penser comme un Mapmaker et un Développeur de Datapack**.

Après fine-tuning sur ce fichier, l'IA sera capable de :
1.  **Comprendre le contexte versionné** : Distinguer automatiquement la syntaxe Java 1.12 (IDs numériques) de la 1.13+ (Namespaced IDs) et de la 1.20.5+ (Components).
2.  **Architecturer des systèmes** : Concevoir des boucles de jeu complètes (Initialisation → Tick → Win/Loss → Reset) sans hallucination.
3.  **Générer du code complexe** : Écrire des fichiers `.mcfunction`, des JSON de predicates, loot tables et advancements valides.
4.  **Optimiser les performances** : Proposer des solutions anti-lag (utilisation de `predicates`, limitation des sélecteurs `@e`, clocks optimisées).
5.  **Déboguer et corriger** : Identifier les erreurs courantes et proposer des corrections basées sur la version cible.

---

## 📚 Contenu Détaillé du Dataset

Le fichier `minecraft_ultimate_complete.jsonl` est structuré en **7 piliers majeurs** :

### 1. 🛠️ Commandes de Base & Avancées (Core Commands)
Couverture exhaustive de toutes les commandes vanilla avec leurs arguments, options et sélecteurs.
-   **Basiques** : `/give`, `/tp`, `/summon`, `/fill`, `/clone`, `/setblock`.
-   **Avancées** : `/execute` (toutes les sous-commandes: `if`, `unless`, `store`, `align`, `anchored`), `/data`, `/attribute`, `/item`, `/random`, `/tick`, `/place`.
-   **Sélecteurs** : Maîtrise totale de `@a`, `@p`, `@s`, `@e`, `@r` avec filtres complexes (`distance`, `level`, `gamemode`, `nbt`, `scores`, `tag`, `team`, `predicate`).

### 2. ⚙️ Command Blocks & Redstone Logic
Apprentissage des mécanismes physiques et logiques des blocs de commande.
-   **Types** : Impulse, Repeat, Chain (avec gestion des couleurs et flux).
-   **Paramètres** : Conditionnel vs Inconditionnel, Always Active vs Needs Redstone.
-   **Combinaisons** : Timers (ticks/ms), Fill Clocks, Détecteurs d'entités, Machines à états finis (FSM), Systèmes de boutique, Portes sécurisées.
-   **Optimisation** : Réduction du lag, placement optimal, chaînes conditionnelles efficaces.

### 3. 📦 Datapacks & Functions (Professionnel)
Focus sur le développement moderne via fichiers `.mcfunction` et structures JSON.
-   **Commande `/function`** : Utilisation avancée avec arguments `with`, `if`, `unless` (1.20.2+).
-   **Macros (1.20.5+)** : Syntaxe `$var`, passage d'arguments, calculs dynamiques.
-   **Fichiers JSON** :
    -   `pack.mcmeta` : Configuration, formats, filtres.
    -   `predicates/` : Conditions de dégâts, localisation, équipements, effets.
    -   `loot_tables/` : Pools, fonctions (`set_count`, `copy_nbt`), conditions complexes.
    -   `advancements/` : Tous les triggers possibles (interaction, localisation, combat).
    -   `tags/` : Blocs, entités, fonctions, fluides.
    -   `recipes/` : Crafting, cuisson, smithing, stonecutting.

### 4. 🎮 Architectures de Minigames (Game Design)
Exemples complets de jeux jouables, pas juste des snippets isolés.
-   **Jeux inclus** : Spleef, Parkour, Capture the Flag (CTF), Bedwars, Survival Games, Boss Rush, TNT Run, Dropper, Puzzle Maps, Quiz.
-   **Mécaniques enseignées** : Gestion des équipes (`/team`), Scoreboards dynamiques, Systèmes de vies/points, Zones de spawn/reset, Inventaires custom, Kits de départ.

### 5. 🔄 Gestion des Versions & Migrations
Un point fort unique du dataset : la conscience temporelle.
-   **Pre-1.13 (Legacy)** : IDs numériques (`1:stone`), ancien `/execute`, NBT brut.
-   **1.13-1.20.4 (Modern)** : The Flattening (`minecraft:stone`), nouveau `/execute`, NBT structuré.
-   **1.20.5+ (Components)** : Transition vers le système de Components (`custom_name` vs `CustomName`).
-   **Bedrock Edition** : Commandes spécifiques (`/event`, `/mobevent`, `/script`, `/camerashake`) et différences de sélecteurs.

### 6. 🛡️ Sécurité, Debug & Performance
Enseignement des bonnes pratiques "Production".
-   **Anti-Cheat Vanilla** : Détection de vitesse anormale, fly hack, reach.
-   **Debugging** : Utilisation de `/debug`, logging dans les storages, tests de charge.
-   **Performance** : Limitation des entités, utilisation de `predicates` pour éviter les checks inutiles, optimisation des loops.

### 7. ❌ Contre-Exemples & Corrections
Pour réduire les hallucinations, le dataset inclut des paires "Erreur → Correction".
-   Commandes obsolètes corrigées pour la version cible.
-   Syntaxes invalides expliquées et réparées.
-   Logiques buguées (boucles infinies, scores non reset) optimisées.

---

## 📝 Structure des Données (Format JSONL)

Chaque ligne est un objet JSON valide au format **ChatML**, compatible avec HuggingFace, Axolotl, Llama-Factory et OpenAI.

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Tu es un expert Minecraft. Tu génères des commandes valides pour la version spécifiée."
    },
    {
      "role": "user",
      "content": "Crée un système de timer de 10 secondes qui affiche un compte à rebours dans l'action bar, compatible Java 1.20."
    },
    {
      "role": "assistant",
      "content": "/scoreboard objectives add timer dummy\n/scoreboard players set #count timer 200\n... (code complet)"
    }
  ],
  "metadata": {
    "category": "minigame_mechanic",
    "version_min": "1.13",
    "version_max": "1.20.4",
    "edition": "java",
    "complexity": "intermediate",
    "commands_used": ["scoreboard", "execute", "title"]
  }
}
```

---

## 🚀 Comment utiliser ce dataset

### 1. Prérequis
-   Python 3.8+
-   Bibliothèque `datasets` (HuggingFace) ou outil de fine-tuning préféré (Axolotl, Llama-Factory).

### 2. Validation (Optionnel mais recommandé)
Avant l'entraînement, vous pouvez re-valider le fichier :
```bash
python validate_minecraft_dataset.py
```

### 3. Entraînement (Exemple avec HuggingFace TRL)
```python
from datasets import load_dataset

dataset = load_dataset('json', data_files='minecraft_ultimate_complete.jsonl')
# Configurer votre SFTTrainer avec ce dataset...
```

### 4. Prompting Recommandé
Pour obtenir les meilleurs résultats, utilisez toujours un **System Prompt** précis :
> "Tu es un ingénieur Minecraft expert. Lorsque l'utilisateur demande une commande, demande toujours la version (Java/Bedrock, numéro de version) si elle n'est pas précisée. Fournis le code complet, optimisé et commenté. Si le système est complexe, explique l'architecture (Setup, Loop, Reset)."

---

## ⚠️ Limites & Notes
-   **Évolutivité** : Minecraft est mis à jour régulièrement. Ce dataset couvre jusqu'à la 1.21+. Pour les versions futures, une mise à jour du dataset sera nécessaire.
-   **Plugins** : Ce dataset est focalisé sur le **Vanilla** et les **Datapacks**. Il ne couvre pas les API de plugins externes (Spigot/Paper) sauf via les commandes bridge standards.
-   **Créativité** : Bien que l'IA puisse assembler des systèmes complexes, la créativité pure (design de map, histoire) reste du domaine de l'utilisateur humain.

---

## 📄 Licence
Ce dataset est fourni à des fins éducatives et de recherche pour l'entraînement de modèles d'IA open-source. Les commandes Minecraft sont la propriété intellectuelle de Mojang Studios/Microsoft.

---

**Créé avec passion pour la communauté Minecraft et l'IA.** 🧱🤖
