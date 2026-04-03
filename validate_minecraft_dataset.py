#!/usr/bin/env python3
"""
Script de validation qualité pour le dataset Minecraft Ultimate Complete.
Vérifie : syntaxe JSON, schéma, duplications, distribution, anomalies.
"""

import json
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
import sys

DATASET_PATH = Path("/workspace/minecraft_ultimate_complete.jsonl")
REPORT_PATH = Path("/workspace/validation_report.json")

def validate_json_syntax(line_num, line):
    """Valide la syntaxe JSON d'une ligne."""
    try:
        data = json.loads(line)
        return True, data, None
    except json.JSONDecodeError as e:
        return False, None, str(e)

def validate_schema(data):
    """Valide la structure attendue (messages + metadata)."""
    errors = []
    if not isinstance(data, dict):
        errors.append("La racine doit être un objet JSON")
        return errors
    
    if "messages" not in data:
        errors.append("Champ 'messages' manquant")
    elif not isinstance(data["messages"], list) or len(data["messages"]) == 0:
        errors.append("'messages' doit être une liste non vide")
    else:
        for i, msg in enumerate(data["messages"]):
            if not isinstance(msg, dict):
                errors.append(f"Message {i} n'est pas un objet")
                continue
            if "role" not in msg or "content" not in msg:
                errors.append(f"Message {i} manque 'role' ou 'content'")
            elif msg["role"] not in ["system", "user", "assistant"]:
                errors.append(f"Message {i} rôle invalide: {msg['role']}")
    
    # Metadata est optionnel pour la compatibilité avec les anciens datasets
    if "metadata" in data:
        if not isinstance(data["metadata"], dict):
            errors.append("'metadata' doit être un objet")
        else:
            # Vérification souple des champs - edition peut être déduit ou absent
            meta = data["metadata"]
            # On accepte l'absence de version/edition pour la compatibilité
    
    return errors

def get_content_hash(data):
    """Génère un hash du contenu pour détecter les doublons."""
    if "messages" not in data:
        return None
    # Hash basé sur le contenu des messages utilisateur et assistant
    content_str = ""
    for msg in data["messages"]:
        if msg.get("role") in ["user", "assistant"]:
            content_str += msg.get("content", "") + "|||"
    return hashlib.md5(content_str.encode('utf-8')).hexdigest()

def analyze_distribution(datas):
    """Analyse la distribution des versions, éditions, types."""
    versions = Counter()
    editions = Counter()
    categories = Counter()
    game_types = Counter()
    
    for data in datas:
        meta = data.get("metadata", {})
        versions.update([meta.get("version", "unknown"), meta.get("min_version", "unknown")])
        editions.update([meta.get("edition", "unknown")])
        categories.update([meta.get("category", "unknown")])
        if "game_type" in meta:
            game_types.update([meta["game_type"]])
    
    return {
        "versions": dict(versions.most_common(20)),
        "editions": dict(editions),
        "categories": dict(categories.most_common(20)),
        "game_types": dict(game_types.most_common(20))
    }

def detect_anomalies(datas):
    """Détecte les anomalies potentielles."""
    anomalies = []
    
    # Vérifier les commandes obsolètes dans des versions récentes
    for i, data in enumerate(datas):
        meta = data.get("metadata", {})
        version = meta.get("version", "") or meta.get("min_version", "")
        
        if "1.20" in version or "1.21" in version:
            for msg in data.get("messages", []):
                content = msg.get("content", "")
                # Détection simple de syntaxe obsolète
                if "minecraft:stone[0]" in content and meta.get("edition") == "Java":
                    anomalies.append(f"Ligne {i}: Syntaxe NBT obsolète détectée dans version récente")
                    break
                if "/execute @a" in content and "run" not in content and meta.get("edition") == "Java":
                    # Ancienne syntaxe execute sans 'run' dans version récente
                    if "1.13" in version or "1.14" in version or "1.15" in version or "1.16" in version or "1.17" in version or "1.18" in version or "1.19" in version or "1.20" in version or "1.21" in version:
                         # C'est normal pour 1.13+, la nouvelle syntaxe est execute as @a run ...
                         # L'ancienne /execute @a ... n'existe plus
                         if "/execute @a" in content and not ("as @a" in content or "positioned as @a" in content):
                            anomalies.append(f"Ligne {i}: Ancienne syntaxe /execute détectée dans version >= 1.13")
                            break
    
    return anomalies[:100]  # Limiter le rapport

def main():
    if not DATASET_PATH.exists():
        print(f"❌ Fichier non trouvé: {DATASET_PATH}")
        sys.exit(1)
    
    print(f"🔍 Validation de {DATASET_PATH}...")
    
    total_lines = 0
    valid_lines = 0
    invalid_syntax = 0
    schema_errors = 0
    duplicates = 0
    
    seen_hashes = set()
    valid_datas = []
    error_samples = []
    
    with open(DATASET_PATH, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            line = line.strip()
            if not line:
                continue
            
            # 1. Validation syntaxe JSON
            is_valid, data, error = validate_json_syntax(line_num, line)
            if not is_valid:
                invalid_syntax += 1
                if len(error_samples) < 10:
                    error_samples.append({"line": line_num, "type": "syntax", "error": error})
                continue
            
            # 2. Validation schéma
            schema_errs = validate_schema(data)
            if schema_errs:
                schema_errors += 1
                if len(error_samples) < 10:
                    error_samples.append({"line": line_num, "type": "schema", "errors": schema_errs})
                continue
            
            # 3. Détection doublons
            content_hash = get_content_hash(data)
            if content_hash in seen_hashes:
                duplicates += 1
                continue
            seen_hashes.add(content_hash)
            
            valid_lines += 1
            valid_datas.append(data)
    
    # 4. Analyse distribution
    distribution = analyze_distribution(valid_datas)
    
    # 5. Détection anomalies
    anomalies = detect_anomalies(valid_datas)
    
    # Génération rapport
    report = {
        "summary": {
            "total_lines": total_lines,
            "valid_lines": valid_lines,
            "invalid_syntax": invalid_syntax,
            "schema_errors": schema_errors,
            "duplicates": duplicates,
            "deduplicated_valid": valid_lines,
            "quality_score": round((valid_lines / total_lines * 100) if total_lines > 0 else 0, 2)
        },
        "error_samples": error_samples,
        "distribution": distribution,
        "anomalies_detected": len(anomalies),
        "anomaly_samples": anomalies,
        "recommendation": ""
    }
    
    # Recommandation finale
    if report["summary"]["quality_score"] >= 98 and report["summary"]["duplicates"] == 0:
        report["recommendation"] = "✅ Dataset excellent, prêt pour l'entraînement."
    elif report["summary"]["quality_score"] >= 95:
        report["recommendation"] = "⚠️ Dataset de bonne qualité, quelques nettoyages mineurs recommandés."
    else:
        report["recommendation"] = "❌ Dataset nécessite un nettoyage important avant entraînement."
    
    # Sauvegarde rapport
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Affichage console
    print("\n" + "="*60)
    print("📊 RAPPORT DE VALIDATION")
    print("="*60)
    print(f"Lignes totales:       {report['summary']['total_lines']:,}")
    print(f"Lignes valides:       {report['summary']['valid_lines']:,}")
    print(f"Erreurs syntaxe:      {report['summary']['invalid_syntax']}")
    print(f"Erreurs schéma:       {report['summary']['schema_errors']}")
    print(f"Doublons détectés:    {report['summary']['duplicates']:,}")
    print(f"Score de qualité:     {report['summary']['quality_score']}%")
    print(f"Anomalies détectées:  {report['anomalies_detected']}")
    print("-"*60)
    print(f"💡 Recommandation: {report['recommendation']}")
    print("="*60)
    print(f"\n📄 Rapport complet sauvegardé dans: {REPORT_PATH}")
    
    if error_samples:
        print(f"\n⚠️  Exemples d'erreurs (max 10):")
        for err in error_samples[:5]:
            print(f"   Ligne {err['line']}: {err.get('type')} - {err.get('error') or err.get('errors')}")

if __name__ == "__main__":
    main()
