import os
import json
import shutil
import argparse
from datetime import datetime

SBAC_DIR = ".sbac"
COMMITS_DIR = os.path.join(SBAC_DIR, "commits")
INDEX_FILE = os.path.join(SBAC_DIR, "index.json")
CONFIG_FILE = os.path.join(SBAC_DIR, "config.json")
BASELINES_FILE = os.path.join(SBAC_DIR, "baselines.json")


def repository_exists():
    return os.path.exists(SBAC_DIR)


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def init_repository():
    if repository_exists():
        print("El repositorio SBAC ya existe.")
        return

    os.makedirs(COMMITS_DIR)

    save_json(INDEX_FILE, {"tracked_files": []})
    save_json(CONFIG_FILE, {"last_commit": 0})
    save_json(BASELINES_FILE, {"baselines": []})

    print("Repositorio SBAC inicializado correctamente.")


def add_file(file_path):
    if not repository_exists():
        print("Error: primero debes inicializar el repositorio.")
        return

    if not os.path.exists(file_path):
        print(f"Error: el archivo '{file_path}' no existe.")
        return

    index_data = load_json(INDEX_FILE)

    if file_path in index_data["tracked_files"]:
        print(f"El archivo '{file_path}' ya está en seguimiento.")
        return

    index_data["tracked_files"].append(file_path)
    save_json(INDEX_FILE, index_data)

    print(f"Archivo agregado correctamente: {file_path}")


def status():
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    index_data = load_json(INDEX_FILE)
    tracked_files = index_data["tracked_files"]

    print("\n========== ESTADO DEL REPOSITORIO ==========")

    if not tracked_files:
        print("No hay archivos en seguimiento.")
        return

    for file_path in tracked_files:
        if os.path.exists(file_path):
            print(f"[OK] En seguimiento: {file_path}")
        else:
            print(f"[ERROR] Archivo faltante: {file_path}")

    print("============================================\n")


def commit(message):
    if not repository_exists():
        print("Error: primero debes inicializar el repositorio.")
        return

    index_data = load_json(INDEX_FILE)
    config_data = load_json(CONFIG_FILE)

    tracked_files = index_data["tracked_files"]

    if not tracked_files:
        print("No hay archivos en seguimiento para crear un commit.")
        return

    new_commit_id = config_data["last_commit"] + 1
    commit_folder = os.path.join(COMMITS_DIR, str(new_commit_id))
    os.makedirs(commit_folder)

    copied_files = []

    for file_path in tracked_files:
        if os.path.exists(file_path):
            destination = os.path.join(commit_folder, file_path)
            os.makedirs(os.path.dirname(destination) or ".", exist_ok=True)
            shutil.copy2(file_path, destination)
            copied_files.append(file_path)

    metadata = {
        "id": new_commit_id,
        "message": message,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": copied_files
    }

    save_json(os.path.join(commit_folder, "metadata.json"), metadata)

    config_data["last_commit"] = new_commit_id
    save_json(CONFIG_FILE, config_data)

    print("Commit creado correctamente.")
    print(f"ID: {new_commit_id}")
    print(f"Mensaje: {message}")


def history():
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    commits = os.listdir(COMMITS_DIR)

    if not commits:
        print("No hay commits registrados.")
        return

    commits = sorted(commits, key=lambda x: int(x))

    print("\n========== HISTORIAL DE VERSIONES ==========")

    for commit_id in commits:
        metadata_path = os.path.join(COMMITS_DIR, commit_id, "metadata.json")
        metadata = load_json(metadata_path)

        print(f"Commit: {metadata['id']}")
        print(f"Fecha: {metadata['date']}")
        print(f"Mensaje: {metadata['message']}")
        print(f"Archivos: {', '.join(metadata['files'])}")
        print("--------------------------------------------")

    print("============================================\n")


def checkout(version):
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    commit_folder = os.path.join(COMMITS_DIR, str(version))

    if not os.path.exists(commit_folder):
        print(f"Error: la versión {version} no existe.")
        return

    metadata = load_json(os.path.join(commit_folder, "metadata.json"))

    for file_path in metadata["files"]:
        source = os.path.join(commit_folder, file_path)

        if os.path.exists(source):
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            shutil.copy2(source, file_path)

    print(f"Se restauró correctamente la versión {version}.")


def create_baseline(name):
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    config_data = load_json(CONFIG_FILE)

    if config_data["last_commit"] == 0:
        print("No hay commits para marcar como línea base.")
        return

    baselines_data = load_json(BASELINES_FILE)

    baseline = {
        "name": name,
        "commit_id": config_data["last_commit"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    baselines_data["baselines"].append(baseline)
    save_json(BASELINES_FILE, baselines_data)

    print("Línea base creada correctamente.")
    print(f"Nombre: {name}")
    print(f"Commit asociado: {config_data['last_commit']}")


def list_baselines():
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    baselines_data = load_json(BASELINES_FILE)
    baselines = baselines_data["baselines"]

    if not baselines:
        print("No hay líneas base registradas.")
        return

    print("\n========== LÍNEAS BASE ==========")

    for baseline in baselines:
        print(f"Nombre: {baseline['name']}")
        print(f"Commit: {baseline['commit_id']}")
        print(f"Fecha: {baseline['date']}")
        print("---------------------------------")

    print("=================================\n")


def main():
    parser = argparse.ArgumentParser(
        description="SBAC - Sistema Básico de Administración de Configuración"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")
    subparsers.add_parser("status")
    subparsers.add_parser("history")
    subparsers.add_parser("list-baselines")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("file")

    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument("message")

    checkout_parser = subparsers.add_parser("checkout")
    checkout_parser.add_argument("version", type=int)

    baseline_parser = subparsers.add_parser("baseline")
    baseline_parser.add_argument("name")

    args = parser.parse_args()

    if args.command == "init":
        init_repository()

    elif args.command == "add":
        add_file(args.file)

    elif args.command == "status":
        status()

    elif args.command == "commit":
        commit(args.message)

    elif args.command == "history":
        history()

    elif args.command == "checkout":
        checkout(args.version)

    elif args.command == "baseline":
        create_baseline(args.name)

    elif args.command == "list-baselines":
        list_baselines()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()