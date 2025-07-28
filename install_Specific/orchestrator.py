import os
import sys
import subprocess
import shutil
from pathlib import Path
import platform

# --- Project Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent

# --- Global Environment Detection ---
# Check if running inside a virtual environment
IS_IN_VENV = (sys.prefix != sys.base_prefix)

# Get current Python version
CURRENT_PYTHON_MAJOR = sys.version_info.major
CURRENT_PYTHON_MINOR = sys.version_info.minor
CURRENT_PYTHON_VERSION_STR = f"{CURRENT_PYTHON_MAJOR}.{CURRENT_PYTHON_MINOR}"
CURRENT_PYTHON_VERSION_TUPLE = (CURRENT_PYTHON_MAJOR, CURRENT_PYTHON_MINOR)

# Define the expected Python version for "Full Features" (usually the most stable/tested)
EXPECTED_PYTHON_MAJOR = 3
EXPECTED_PYTHON_MINOR = 10
EXPECTED_PYTHON_VERSION_STR = f"{EXPECTED_PYTHON_MAJOR}.{EXPECTED_PYTHON_MINOR}"
EXPECTED_PYTHON_VERSION_TUPLE = (EXPECTED_PYTHON_MAJOR, EXPECTED_PYTHON_MINOR)

# --- Utility Functions ---

def _get_venv_python_executable():
    """Returns the path to the python executable within the .venv."""
    if sys.platform.startswith('win'):
        return str(PROJECT_ROOT / ".venv" / "Scripts" / "python.exe")
    else: # Linux, macOS, WSL
        return str(PROJECT_ROOT / ".venv" / "bin" / "python")

def run_command_os_aware(make_target_args, win_native_cmd_parts, python_exec_arg_for_make="", check_result=True, capture_output=False, text_output=True):
    """
    Executes a command by choosing the OS-appropriate version.
    Args:
        make_target_args (list): The list of arguments for 'make' (e.g., ["setup"]).
        win_native_cmd_parts (list of lists): Sequence of commands for native Windows execution.
                                             Each inner list is a command.
        python_exec_arg_for_make (str): The PYTHON_EXEC=... argument to pass to make.
        check_result (bool): If True, raises an exception on command failure.
        capture_output (bool): If True, captures stdout and stderr.
        text_output (bool): If True, décode stdout/stderr en texte.
    Returns:
        subprocess.CompletedProcess: The command result object.
    """
    is_wsl = 'WSL_DISTRO_NAME' in os.environ or 'WSL_ARCH' in os.environ

    if sys.platform.startswith('win') and not is_wsl: # Native Windows (not WSL)
        print(f"\n🚀 Exécution (Windows native):")
        
        for cmd_part_list in win_native_cmd_parts:
            current_cmd_executable_base = cmd_part_list[0]
            current_cmd_args = cmd_part_list[1:]
            
            final_cmd = []

            # Determine the actual executable path or command name
            if current_cmd_executable_base == "python_current_sys_or_chosen":
                final_cmd.append(cmd_part_list[0])
                final_cmd.extend(cmd_part_list[1:])
            elif current_cmd_executable_base == "python_venv":
                final_cmd.append(_get_venv_python_executable())
                final_cmd.extend(current_cmd_args)
            elif current_cmd_executable_base == "pip_venv":
                final_cmd.append(str(PROJECT_ROOT / ".venv" / "Scripts" / "pip.exe"))
                final_cmd.extend(current_cmd_args)
            elif current_cmd_executable_base == "yarn":
                final_cmd.append("yarn")
                final_cmd.extend(current_cmd_args)
            elif current_cmd_executable_base == "git":
                final_cmd.append("git")
                final_cmd.extend(current_cmd_args)
            elif current_cmd_executable_base == "flake8_venv":
                final_cmd.append(str(PROJECT_ROOT / ".venv" / "Scripts" / "flake8.exe"))
                final_cmd.extend(current_cmd_args)
            elif current_cmd_executable_base == "powershell":
                final_cmd.append("powershell")
                final_cmd.extend(current_cmd_args)
            else: # Fallback for any other direct executable name
                final_cmd.append(current_cmd_executable_base)
                final_cmd.extend(current_cmd_args)
            
            final_cmd_for_display = [str(arg) for arg in final_cmd]
            print(f"  -> { ' '.join(final_cmd_for_display) }")
            
            try:
                subprocess.run(final_cmd, check=check_result, capture_output=capture_output, text=text_output, cwd=PROJECT_ROOT)
            except FileNotFoundError:
                 print(f"Erreur : Commande '{final_cmd[0]}' introuvable.", file=sys.stderr)
                 print("Veuillez vous assurer que les outils Windows natifs (comme Git, Yarn, Python) sont installés et dans votre PATH.", file=sys.stderr)
                 sys.exit(1)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'exécution native Windows de : {' '.join(e.cmd)}", file=sys.stderr)
                print(f"Code de sortie : {e.returncode}", file=sys.stderr)
                if e.stdout: print(f"Sortie standard : \n{e.stdout}", file=sys.stderr)
                if e.stderr: print(f"Erreur standard : \n{e.stderr}", file=sys.stderr)
                sys.exit(e.returncode)
            except Exception as e:
                print(f"Une erreur inattendue s'est produite : {e}", file=sys.stderr)
                sys.exit(1)

    else: # Linux, macOS, WSL (where 'make' is expected)
        make_cmd = ["make"] + make_target_args
        if python_exec_arg_for_make:
            make_cmd.append(python_exec_arg_arg_for_make)
        
        print(f"\n🚀 Exécution (Linux/macOS/WSL via make) : {' '.join(make_cmd)}")
        try:
            subprocess.run(make_cmd, check=check_result, capture_output=capture_output, text=text_output, cwd=PROJECT_ROOT)
        except FileNotFoundError:
            print(f"Erreur : Commande 'make' introuvable.", file=sys.stderr)
            print("Veuillez installer 'make' (ex : 'sudo apt install build-essential' sur Linux, 'xcode-select --install' sur macOS).", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de make de : {' '.join(e.cmd)}", file=sys.stderr)
            print(f"Code de sortie : {e.returncode}", file=sys.stderr)
            if e.stdout: print(f"Sortie standard : \n{e.stdout}", file=sys.stderr)
            if e.stderr: print(f"Erreur standard : \n{e.stderr}", file=sys.stderr)
            sys.exit(e.returncode)
        except Exception as e:
            print(f"Une erreur inattendue s'est produite : {e}", file=sys.stderr)
            sys.exit(1)


def get_option_status(option_num):
    """Détermine le statut de disponibilité d'une option de menu en fonction de la version Python et de l'environnement."""

    # Définir des listes de compatibilité explicites pour chaque type d'opération majeure
    # Basé sur les scripts sous-jacents (install_pip.py, install_docker.py, setup_pyi.py)
    # et vos exigences de test.

    # 1. Compatibilité pour la création d'environnement virtuel (make setup)
    # Pratiquement toute version moderne de Python peut créer un venv.
    COMPAT_SETUP = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]
    # 2. Compatibilité pour l'installation des dépendances Python (make install-py-by-version)
    COMPAT_INSTALL_PY_DEPS = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]
    # 3. Compatibilité pour les assets web (make install-web, make build-web)
    # Votre règle : disponible uniquement en 3.10
    COMPAT_WEB_ASSETS = [(3, 10)]
    # 4. Compatibilité pour la construction Wheel et Executable (make build-wheel, make build-exe)
    # Basé sur setup_pyi.py qui supporte 3.10, 3.11, 3.12
    COMPAT_BUILD_EXE_WHEEL = [(3, 10), (3, 11), (3, 12)]
    # 5. Compatibilité pour la construction Docker (make build_docker)
    COMPAT_BUILD_DOCKER = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]
    # 6. Compatibilité pour l'activation (make activate-venv)
    COMPAT_ACTIVATE = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]

    # Mapper les options à leurs listes de compatibilité
    # La compatibilité de la cible principale ('build', 'install', 'lint') doit être la plus restrictive de ses sous-cibles.
    option_compat_map = {
        1: COMPAT_SETUP,
        2: COMPAT_INSTALL_PY_DEPS,
        3: COMPAT_WEB_ASSETS,
        4: COMPAT_WEB_ASSETS, # install inclut install-web, donc limité à COMPAT_WEB_ASSETS (3.10)
        5: COMPAT_WEB_ASSETS,
        6: COMPAT_BUILD_EXE_WHEEL,
        7: COMPAT_BUILD_EXE_WHEEL,
        8: COMPAT_BUILD_EXE_WHEEL, # build inclut build-exe/wheel, donc prend leur compatibilité la plus restrictive (3.10-3.12)
        9: COMPAT_BUILD_DOCKER,
        11: COMPAT_INSTALL_PY_DEPS, # lint-py dépend des dépendances Python (3.9-3.13)
        12: COMPAT_WEB_ASSETS,      # lint-web dépend des assets web (3.10)
        13: COMPAT_WEB_ASSETS,      # lint inclut lint-web, donc limité à COMPAT_WEB_ASSETS (3.10)
        14: COMPAT_ACTIVATE, # Nouvelle option pour afficher la commande d'activation du venv
    }

    # Cas spécial pour "Clean" qui n'est pas dépendant de la version Python
    if option_num == 10:
        return "available"

    # Get compatibility list for the current option
    compat_list = option_compat_map.get(option_num)

    if compat_list is None:
        return "unknown" # Ne devrait pas arriver pour les options valides

    # --- Specific logic for option 1 (setup) ---
    if option_num == 1:
        if IS_IN_VENV:
            return "disabled_venv_present"
        else:
            if CURRENT_PYTHON_VERSION_TUPLE not in COMPAT_SETUP:
                 return "available_warning_version_system"
            elif CURRENT_PYTHON_VERSION_TUPLE != EXPECTED_PYTHON_VERSION_TUPLE:
                 return "available_warning_version_preferred"
            else:
                return "available"
    # --- Logic for Option 14 (Activate Venv) ---
    elif option_num == 14:
        summary, has_venv = get_venv_summary_string()
        if not has_venv:
            return "disabled_no_venv_dir"
        return f"available [{summary}]"

    # --- Logic for all other Python-dependent options (2,3,4,5,6,7,8,9,11,12,13) ---
    if not IS_IN_VENV:
        return "disabled_no_venv"
    
    # Check Python version compatibility of the VIRTUAL ENVIRONMENT
    if CURRENT_PYTHON_VERSION_TUPLE not in compat_list:
        return "disabled_incompatible_version"
    
    return "available"

def get_option_compat_list(option_num):
    """Returns the compatibility list for a given option, used for informational messages."""
    # COMPAT lists are already defined globally within get_option_status,
    # but we can redefine them here for clarity or pass them as args if preferred.
    # For now, keeping them separate to avoid global variable dependency in this info function's context.

    COMPAT_SETUP = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]
    COMPAT_INSTALL_PY_DEPS = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]
    COMPAT_WEB_ASSETS = [(3, 10)]
    COMPAT_BUILD_EXE_WHEEL = [(3, 10), (3, 11), (3, 12)]
    COMPAT_BUILD_DOCKER = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]
    COMPAT_ACTIVATE = [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]

    option_compat_map = {
        1: COMPAT_SETUP,
        2: COMPAT_INSTALL_PY_DEPS,
        3: COMPAT_WEB_ASSETS,
        4: COMPAT_WEB_ASSETS,
        5: COMPAT_WEB_ASSETS,
        6: COMPAT_BUILD_EXE_WHEEL,
        7: COMPAT_BUILD_EXE_WHEEL,
        8: COMPAT_BUILD_EXE_WHEEL,
        9: COMPAT_BUILD_DOCKER,
        11: COMPAT_INSTALL_PY_DEPS,
        12: COMPAT_WEB_ASSETS,
        13: COMPAT_WEB_ASSETS,
        14: COMPAT_ACTIVATE,
    }
    return option_compat_map.get(option_num)

def clear_screen():
    """Clears the console screen."""
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        os.system('clear')

def display_menu():
    print("\n--- Project Orchestrator Menu (Desktop Environments) ---")
    print(f"Current Python Environment: {'Virtual Environment' if IS_IN_VENV else 'System Python'}")
    print(f"Current Python Version: {CURRENT_PYTHON_VERSION_STR}")
    print(f"Expected Python Version for Full Features: {EXPECTED_PYTHON_VERSION_STR}")
    print("--------------------------------------------------")

    options_map = {
        1: "Setup Virtual Environment",
        2: "Install Python Dependencies",
        3: "Install Web Modules",
        4: "Full Installation",
        5: "Build Web Assets",
        6: "Build Python Wheel",
        7: "Build Executable",
        8: "Full Build",
        9: "Build Docker Image",
        10: "Clean Project",
        11: "Run Python Linter",
        12: "Run Web Linter",
        13: "Run All Linters",
        14: "Display Virtual Environment Activation Command",
    }

    # --- INFORMATION SECTION FOR VIRTUAL ENVIRONMENT OPTIONS ---
    if not IS_IN_VENV: # Only display this section if NOT in a venv
        print("\n--- Information: Options available in Virtual Environment ---")
        print(f"If you set up a Python {EXPECTED_PYTHON_VERSION_STR} virtual environment (Option 1), the following options will become available (in addition to cleaning):")
        
        venv_options_info = []
        for num in sorted(options_map.keys()):
            if num == 0 or num == 10: # Ignore Exit and Clean (already always available or handled separately)
                continue
            if num == 1: # Option 1 is no longer "available" once the venv is created.
                # We don't add it here, as these are options that *will become* available *after* setup.
                continue
            
            # Simulate compatibility if IS_IN_VENV were True and version = EXPECTED_PYTHON_VERSION_TUPLE (3.10)
            compat_list = get_option_compat_list(num)
            
            if compat_list and EXPECTED_PYTHON_VERSION_TUPLE in compat_list:
                option_text = options_map[num]
                # Add precision if option is limited to 3.10
                if compat_list == [(3, 10)]: # This is COMPAT_WEB_ASSETS list
                    option_text += " (Limited to Python 3.10)"
                elif compat_list == [(3, 10), (3, 11), (3, 12)]: # This is COMPAT_BUILD_EXE_WHEEL
                    option_text += " (Compatible up to Python 3.12)"
                elif compat_list == [(3, 9), (3, 10), (3, 11), (3, 12), (3, 13)]: # This is COMPAT_INSTALL_PY_DEPS or COMPAT_BUILD_DOCKER
                    # To be more precise here, distinguish if it's for build_docker or install_py_deps
                    if num == 9: # build_docker
                         option_text += " (Compatible up to Python 3.13 for Docker image)"
                    else: # install_py_deps and linters
                        option_text += " (Compatible up to Python 3.13)"
                
                venv_options_info.append(f" {num}. {option_text}")
        
        if venv_options_info:
            for item in venv_options_info:
                print(item)
        print("--------------------------------------------------")

    # --- DISPLAY CURRENTLY AVAILABLE OPTIONS ---
    available_options_for_display = {}
    for num in sorted(options_map.keys()):
        status = get_option_status(num)
        if status.startswith("available"):
            available_options_for_display[num] = options_map[num]
            
    for num in sorted(available_options_for_display.keys()):
        print(f"{num}. {available_options_for_display[num]}")
    
    print("0. Exit")
    print("--------------------------------------------------")

def lister_venvs_avec_version(racine="."):
    suffixe_python = "Scripts\\python.exe" if platform.system() == "Windows" else "bin/python"
    venvs = []

    for dossier in os.listdir(racine):
        chemin = os.path.join(racine, dossier)
        exe_python = os.path.join(chemin, suffixe_python)
        pyvenv = os.path.join(chemin, "pyvenv.cfg")

        if os.path.isfile(pyvenv) and os.path.isfile(exe_python):
            try:
                version = subprocess.check_output([exe_python, "--version"], stderr=subprocess.STDOUT)
                version = version.decode().strip().split()[-1]  # Ex: "Python 3.12.3" -> "3.12.3"
                venvs.append((dossier, chemin, version))
            except Exception as e:
                print(f"Impossible de lire la version pour {dossier} : {e}")
    return venvs

def relancer_dans_env_virtuel(chemin_venv):
    """
    Relance le script orchestrator.py dans un nouveau terminal avec l'environnement virtuel spécifié activé.
    Cette fonction QUITTERA le processus actuel.
    """
    import subprocess, os, sys

    script_path = os.path.abspath(__file__)
    chemin_env_absolu = os.path.abspath(chemin_venv) # Correction: définir chemin_env_absolu ici

    if os.name == "nt": # Windows
        activate_path = os.path.join(chemin_env_absolu, "Scripts", "activate.bat")
        print(chemin_env_absolu)
        print(activate_path)
        cmd = f'start "" cmd /k "call "{activate_path}" && python \\"{script_path}\\""'
        print(f"Lancement d'une nouvelle fenêtre Windows avec l'environnement activé: {cmd}")
    else: # Linux, macOS
        activate_path = os.path.join(chemin_env_absolu, "bin", "activate")
        cmd = f'gnome-terminal -- bash -c "source "{activate_path}" && python \\"{script_path}\\"; exec bash"'
        print(f"Lancement d'un nouveau terminal avec l'environnement activé: {cmd}")

    subprocess.Popen(cmd, shell=True)
    sys.exit()

def menu_choix_env():
    venvs = lister_venvs_avec_version()
    if not venvs:
        print("Aucun environnement virtuel détecté.")
        return

    print("\nEnvironnements virtuels détectés :")
    for i, (nom, _, version) in enumerate(venvs, 1):
        print(f"{i}. {nom} (Python {version})")

    choix = input("Sélectionne un environnement à utiliser (numéro) : ")
    if choix.isdigit():
        index = int(choix) - 1
        if 0 <= index < len(venvs):
            _, chemin, _ = venvs[index]
            relancer_dans_env_virtuel(chemin)
    print("Choix invalide.")

def get_venv_summary_string(racine="."):
    """
    Retourne (summary_string, has_venv) :
    - summary_string = chaîne comme ".venv (3.10), venv312 (3.12.5)"
    - has_venv = True si au moins un environnement détecté
    """
    venvs = lister_venvs_avec_version(racine)

    if not venvs:
        return ("(aucun environnement détecté)", False)

    # Trie .venv en premier
    venvs.sort(key=lambda v: 0 if v[0] == ".venv" else 1)

    # Crée le résumé
    resume = ", ".join(f"{nom} (Python {version})" for nom, _, version in venvs)
    return (resume, True)


def main():
    print("This orchestrator is designed for desktop environments (Linux, macOS, Windows with make).")
    print("For Termux/Android, please use the dedicated 'termux_setup.sh' script.")

    # General note on Python 3.13 compatibility, moved here for clarity
    print("\nGeneral note on Python 3.13 compatibility:")
    print("- Options compatible up to 3.13 (e.g., Python dependency installation, Docker build) fully support Python 3.13.")
    print("- For executable and wheel builds (and the full build which includes them), Python 3.13 is currently excluded due to compatibility issues with the PyInstaller packaging tool.")
    print("--------------------------------------------------")


    while True:
        display_menu() # This function now displays only the menu and venv info if needed
        lister_venvs_avec_version()
        choice = input("Enter your choice: ")

        if choice == '0':
            print("Exiting orchestrator. Goodbye!")
            break

        try:
            choice_num = int(choice)
        except ValueError:
            print("Invalid input. Please enter a number.")
            # Added pause after invalid input
            input("Press Enter to continue...") 
            continue

        status_message = get_option_status(choice_num) 
        if not status_message.startswith("available"):
            print(f"Option {choice_num} is currently unavailable in the current environment.")
            if status_message == "disabled_venv_present":
                print("Reason: You are already in a virtual environment. 'make setup' is unnecessary.")
            elif status_message == "disabled_no_venv":
                print("Reason: This operation requires a virtual environment. Please create a venv first (Option 1).")
            elif status_message == "disabled_incompatible_version":
                compat_list = get_option_compat_list(choice_num)
                supported_versions_str = ", ".join([f'{v[0]}.{v[1]}' for v in compat_list])
                print(f"Reason: Python {CURRENT_PYTHON_VERSION_STR} is incompatible for this operation. Supported versions: {supported_versions_str}")
            elif status_message == "disabled_no_venv_dir": # Specific message for option 14
                print("Reason: No virtual environment directory (.venv) found. Please create one first (Option 1).")
            # Added pause after displaying a disabled reason
            input("Press Enter to continue...") 
            continue

        # --- Execution Logic (now using run_command_os_aware) ---
        make_target_args = []
        win_native_cmd_parts = []
        python_exec_arg_for_make = ""

        # General path to Python executable for native Windows commands.
        # For initial setup, it's the system python running the orchestrator.
        # For later steps, it's the python within the created venv.
        # _get_venv_python_executable() returns the path to the venv python.

        if choice_num == 1: # Setup Virtual Environment
            make_target_args = ["setup"]
            # For Windows native, we directly call python to create venv and pip within it
            # If user specified a PYTHON_EXEC, use it for the venv creation command itself
            # Otherwise, use the current orchestrator's python.
            python_for_venv_creation_input = input(f"Current system Python is {CURRENT_PYTHON_VERSION_STR}. Do you want to specify a different Python executable for the venv (e.g., 'python3.10', 'py -3.10') or a full path (e.g., 'C:\\Python\\Python310\\python.exe')? Leave empty for current: ").strip()
            
            # The command base (python or py) and its arguments (e.g., -3.10)
            if python_for_venv_creation_input:
                cmd_parts = python_for_venv_creation_input.split()
                python_for_venv_creation_cmd_base = cmd_parts[0] # e.g., 'python', 'py', or full path
                python_for_venv_creation_cmd_args = cmd_parts[1:] # e.g., ['-3.10']
            else:
                python_for_venv_creation_cmd_base = "python" # Default 'python' in PATH
                python_for_venv_creation_cmd_args = []

            venv_path_str = str(PROJECT_ROOT / ".venv") # Path to .venv directory

            win_native_cmd_parts = [
                # Command 1: Create venv
                [python_for_venv_creation_cmd_base] + python_for_venv_creation_cmd_args + ["-m", "venv", venv_path_str],
                # Command 2: Update pip in venv (use the venv's python)
                [_get_venv_python_executable(), "-m", "pip", "install", "-q", "-U", "pip"]
            ]
            
            # If a specific Python was chosen, pass it to make for consistency
            if python_for_venv_creation_input:
                python_exec_arg_for_make = f"PYTHON_EXEC={python_for_venv_creation_input}"
            
            run_command_os_aware(make_target_args, win_native_cmd_parts, python_exec_arg_for_make)

            print("\n*** Virtual environment created! Remember to activate it in your terminal. ***")
            if sys.platform.startswith('win'):
                print(f"For CMD/PowerShell: '{PROJECT_ROOT / '.venv' / 'Scripts' / 'activate.bat'}' or '{PROJECT_ROOT / '.venv' / 'Scripts' / 'Activate.ps1'}'")
            else:
                print(f"For Bash/Zsh: 'source {PROJECT_ROOT / '.venv' / 'bin' / 'activate'}'")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice_num == 2: # Install Python Dependencies
            make_target_args = ["install-py-by-version"]
            venv_python = _get_venv_python_executable()
            win_native_cmd_parts = [
                [venv_python, str(PROJECT_ROOT / "install_pip.py")]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 3: # Install Web Modules
            make_target_args = ["install-web"]
            win_native_cmd_parts = [
                ["yarn", "--cwd", "lncrawl-web", "install"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 4: # Full Installation (reimplementing make install)
            make_target_args = ["install"] # Make target for documentation
            venv_python = _get_venv_python_executable()
            win_native_cmd_parts = [
                # 1. Install Python Deps (from option 2)
                [venv_python, str(PROJECT_ROOT / "install_pip.py")],
                # 2. Install Web Modules (from option 3)
                ["yarn", "--cwd", "lncrawl-web", "install"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)
            print("\n*** Full installation complete! Remember to activate the virtual environment in your terminal to use the application. ***")
            if sys.platform.startswith('win'):
                print(f"For CMD/PowerShell: '{PROJECT_ROOT / '.venv' / 'Scripts' / 'activate.bat'}' or '{PROJECT_ROOT / '.venv' / 'Scripts' / 'Activate.ps1'}'")
            else:
                print(f"For Bash/Zsh: 'source {PROJECT_ROOT / '.venv' / 'bin' / 'activate'}'")
            input("\nAppuyez sur Entrée pour continuer...")


        elif choice_num == 5: # Build Web Assets
            make_target_args = ["build-web"]
            win_native_cmd_parts = [
                ["yarn", "--cwd", "lncrawl-web", "build"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 6: # Build Python Wheel
            make_target_args = ["build-wheel"]
            venv_python = _get_venv_python_executable()
            win_native_cmd_parts = [
                [venv_python, "-m", "build", "-w"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 7: # Build Executable
            make_target_args = ["build-exe"]
            venv_python = _get_venv_python_executable()
            win_native_cmd_parts = [
                [venv_python, str(PROJECT_ROOT / "setup_pyi.py")]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 8: # Full Build (reimplementing make build)
            make_target_args = ["build"]
            venv_python = _get_venv_python_executable()
            win_native_cmd_parts = [
                # Call actions from 4 (Full Installation)
                [venv_python, str(PROJECT_ROOT / "install_pip.py")], # Python deps
                ["yarn", "--cwd", "lncrawl-web", "install"], # Web modules

                # Call actions from 5 (Build Web Assets)
                ["yarn", "--cwd", "lncrawl-web", "build"],

                # Call actions from 6 (Build Python Wheel)
                [venv_python, "-m", "build", "-w"],

                # Call actions from 7 (Build Executable)
                [venv_python, str(PROJECT_ROOT / "setup_pyi.py")]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)
            print("\n*** Full build complete! ***") # Add success message


        elif choice_num == 9: # Build Docker Image
            make_target_args = ["build_docker"]
            venv_python = _get_venv_python_executable()
            win_native_cmd_parts = [
                [venv_python, str(PROJECT_ROOT / "install_docker.py")]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 10: # Clean Project (reimplementing make clean)
            make_target_args = ["clean"]
            # Windows native clean needs careful PowerShell commands
            win_native_cmd_parts = [
                # Using powershell commands directly from Makefile for robustness
                ["powershell", "-Command", "try { Remove-Item -ErrorAction SilentlyContinue -Recurse -Force .venv, logs, build, dist } catch {};"],
                ["powershell", "-Command", "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '*.egg-info' | Remove-Item -Recurse -Force"],
                ["powershell", "-Command", "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"],
                ["powershell", "-Command", "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter 'node_modules' | Remove-Item -Recurse -Force"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts) # No shell=True here for powershell itself
            print("Project cleanup complete.")


        elif choice_num == 11: # Run Python Linter
            make_target_args = ["lint-py"]
            # Flake8 path in venv
            venv_flake8_path = str(PROJECT_ROOT / ".venv" / "Scripts" / "flake8.exe") if sys.platform.startswith('win') else str(PROJECT_ROOT / ".venv" / "bin" / "flake8")
            win_native_cmd_parts = [
                [venv_flake8_path, "--config", str(PROJECT_ROOT / ".flake8"), "-v", "--count", "--show-source", "--statistics"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 12: # Run Web Linter
            make_target_args = ["lint-web"]
            win_native_cmd_parts = [
                ["yarn", "--cwd", "lncrawl-web", "lint"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 13: # Run All Linters (reimplementing make lint)
            make_target_args = ["lint"]
            # Combine Python and Web linters for Windows native
            venv_flake8_path = str(PROJECT_ROOT / ".venv" / "Scripts" / "flake8.exe") if sys.platform.startswith('win') else str(PROJECT_ROOT / ".venv" / "bin" / "flake8")
            win_native_cmd_parts = [
                [venv_flake8_path, "--config", str(PROJECT_ROOT / ".flake8"), "-v", "--count", "--show-source", "--statistics"],
                ["yarn", "--cwd", "lncrawl-web", "lint"]
            ]
            run_command_os_aware(make_target_args, win_native_cmd_parts)


        elif choice_num == 14: # Display Virtual Environment Activation Command
            # This option is handled entirely in Python without calling make
            print("\n*** Pour activer l'environnement virtuel, exécutez l'une des commandes suivantes dans votre terminal : ***")
            if sys.platform.startswith('win'):
                print(f"Pour CMD: '{PROJECT_ROOT / '.venv' / 'Scripts' / 'activate.bat'}'")
                print(f"Pour PowerShell: '{PROJECT_ROOT / '.venv' / 'Scripts' / 'Activate.ps1'}'")
            else: # Linux, macOS, WSL
                print(f"Pour Bash/Zsh: 'source {PROJECT_ROOT / '.venv' / 'bin' / 'activate'}'")
            print("**********************************************************************************")
            menu_choix_env()
            input("\nAppuyez sur Entrée pour continuer...")

        else:
            print("Invalid choice. Please try again.")

    # Added a single pause at the very end of the loop, before the next screen clear and menu display.
    input("\nPress Enter to continue...")
    clear_screen() # Added clear_screen after the pause
if __name__ == "__main__":
    main()