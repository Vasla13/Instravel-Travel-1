import os

# Chemin vers votre fichier SQL
file_path = os.path.join("db", "dump-app_voyage-v3.sql")

print(f"Réparation du fichier : {file_path}")

try:
    # Lecture du fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Correction des caractères corrompus
    # Le dump contient des caractères comme '├®' au lieu de 'é'
    old_content = content
    content = content.replace("date_d├®part", "date_départ")
    content = content.replace("date_arriv├®e", "date_arrivée")
    content = content.replace("nationalit├®", "nationalité")

    if content == old_content:
        print("Aucune modification nécessaire ou motifs non trouvés.")
    else:
        # Sauvegarde
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Succès : Les colonnes corrompues ont été renommées correctement.")

except FileNotFoundError:
    print("❌ Erreur : Impossible de trouver le fichier db/dump-app_voyage-v3.sql")
except Exception as e:
    print(f"❌ Erreur inattendue : {e}")