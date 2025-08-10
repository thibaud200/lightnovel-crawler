import sys
import subprocess

def installer_dependances_selon_version():
    # Récupération des informations de version de Python
    version_majeure = sys.version_info.major
    version_mineure = sys.version_info.minor
    version_patch = sys.version_info.micro

    print(f"Version Python détectée : {version_majeure}.{version_mineure}.{version_patch}")

    # Convertir la version en un seul entier pour des comparaisons plus simples
    # Exemple : 3.9.5 devient 309005, 3.10.10 devient 310010
    version_actuelle_int = (version_majeure * 100000) + \
                           (version_mineure * 1000) + \
                           version_patch

    # Définition des bornes pour chaque plage de version
    # Note : J'ai ajusté les bornes pour correspondre à vos fichiers requirements.
    # Si la version est 3.9.x, on utilise requirements_309.txt
    # Si la version est 3.10.x, on utilise requirements_310.txt
    # Si la version est 3.11.x, on utilise requirements_311.txt
    
    requirements_file = None
    pip_info = "pip"

    if version_majeure == 3 and (version_mineure >= 9 and version_mineure < 10):
        requirements_file = "requirements_309.txt"
    elif version_majeure == 3 and (version_mineure >= 10 and version_mineure < 11):
        requirements_file = "requirements_310.txt"
    elif version_majeure == 3 and version_mineure >= 11:
        requirements_file = "requirements_311.txt"
    else:
        print(f"Aucun fichier de dépendances spécifique trouvé pour Python {version_majeure}.{version_mineure}.")
        print("Veuillez créer un fichier 'requirements_X_Y.txt' ou ajuster le script.")
        return # Sortir de la fonction si aucune version n'est gérée

    if requirements_file:
        print(f"Installation des dépendances à partir de {requirements_file}...")
        try:
            # Exécution de la commande pip install
            # `check=True` fera lever une exception si la commande échoue
            subprocess.run(["pip", "install", "--upgrade", pip_info], check=True)
            subprocess.run(["pip", "install", "-r", requirements_file], check=True)
            print("Installation des dépendances terminée avec succès.")
        except FileNotFoundError:
            print(f"Erreur : Le fichier '{requirements_file}' n'a pas été trouvé. Assurez-vous qu'il existe dans le même répertoire que le script.")
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'exécution de pip pour {requirements_file}:")
            print(f"Code de sortie : {e.returncode}")
            print(f"Sortie standard : {e.stdout.decode()}")
            print(f"Erreur standard : {e.stderr.decode()}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    installer_dependances_selon_version()