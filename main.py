import os
import json
import shutil
import difflib
import argparse
from datetime import datetime


SBAC_DIR = ".sbac"
COMMITS_DIR = os.path.join(SBAC_DIR, "commits")
INDEX_FILE = os.path.join(SBAC_DIR, "index.json")
BASELINES_FILE = os.path.join(SBAC_DIR, "baselines.json")
CONFIG_FILE = os.path.join(SBAC_DIR, "config.json")


def repository_exists():
    return os.path.isdir(SBAC_DIR)


def init_repository():
    if repository_exists():
        print("El repositorio SBAC ya existe.")
        return

    os.makedirs(COMMITS_DIR)

    with open(INDEX_FILE, "w", encoding="utf-8") as file:
        json.dump({"tracked_files": []}, file, indent=4)

    with open(BASELINES_FILE, "w", encoding="utf-8") as file:
        json.dump({"baselines": []}, file, indent=4)

    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump({"last_commit": 0}, file, indent=4)

    print("Repositorio SBAC inicializado correctamente.")


def load_json(path):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def add_file(file_path):
    if not repository_exists():
        print("Error: primero debes inicializar el repositorio con 'init'.")
        return

    if not os.path.exists(file_path):
        print(f"Error: el archivo '{file_path}' no existe.")
        return

    index = load_json(INDEX_FILE)

    if file_path in index["tracked_files"]:
        print(f"El archivo '{file_path}' ya está en seguimiento.")
        return

    index["tracked_files"].append(file_path)
    save_json(INDEX_FILE, index)

    print(f"Archivo agregado al seguimiento: {file_path}")


def status():
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    index = load_json(INDEX_FILE)
    tracked_files = index["tracked_files"]

    print("Estado del repositorio:")
    print("-----------------------")

    if not tracked_files:
        print("No hay archivos en seguimiento.")
        return

    for file_path in tracked_files:
        if not os.path.exists(file_path):
            print(f"Eliminado: {file_path}")
        else:
            print(f"En seguimiento: {file_path}")


def create_commit(message):
    if not repository_exists():
        print("Error: primero debes inicializar el repositorio.")
        return

    index = load_json(INDEX_FILE)
    config = load_json(CONFIG_FILE)

    tracked_files = index["tracked_files"]

    if not tracked_files:
        print("No hay archivos agregados al seguimiento.")
        return

    new_commit_id = config["last_commit"] + 1
    commit_path = os.path.join(COMMITS_DIR, str(new_commit_id))
    os.makedirs(commit_path)

    copied_files = []

    for file_path in tracked_files:
        if os.path.exists(file_path):
            destination = os.path.join(commit_path, file_path)

            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(file_path, destination)

            copied_files.append(file_path)

    metadata = {
        "id": new_commit_id,
        "message": message,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "files": copied_files
    }

    save_json(os.path.join(commit_path, "metadata.json"), metadata)

    config["last_commit"] = new_commit_id
    save_json(CONFIG_FILE, config)

    print(f"Commit creado correctamente.")
    print(f"ID: {new_commit_id}")
    print(f"Mensaje: {message}")


def history():
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    if not os.path.exists(COMMITS_DIR):
        print("No hay historial de versiones.")
        return

    commits = sorted(os.listdir(COMMITS_DIR), key=lambda x: int(x))

    if not commits:
        print("No hay commits registrados.")
        return

    print("Historial de versiones:")
    print("-----------------------")

    for commit_id in commits:
        metadata_path = os.path.join(COMMITS_DIR, commit_id, "metadata.json")
        metadata = load_json(metadata_path)

        print(f"Commit: {metadata['id']}")
        print(f"Fecha: {metadata['date']}")
        print(f"Mensaje: {metadata['message']}")
        print(f"Archivos: {', '.join(metadata['files'])}")
        print("-----------------------")


def create_baseline(name):
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    config = load_json(CONFIG_FILE)

    if config["last_commit"] == 0:
        print("No hay commits para marcar como línea base.")
        return

    baselines = load_json(BASELINES_FILE)

    baseline = {
        "name": name,
        "commit_id": config["last_commit"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    baselines["baselines"].append(baseline)
    save_json(BASELINES_FILE, baselines)

    print(f"Línea base creada correctamente.")
    print(f"Nombre: {name}")
    print(f"Commit asociado: {config['last_commit']}")


def list_baselines():
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    baselines = load_json(BASELINES_FILE)

    if not baselines["baselines"]:
        print("No hay líneas base registradas.")
        return

    print("Líneas base disponibles:")
    print("------------------------")

    for baseline in baselines["baselines"]:
        print(f"Nombre: {baseline['name']}")
        print(f"Commit: {baseline['commit_id']}")
        print(f"Fecha: {baseline['date']}")
        print("------------------------")


def diff_versions(version1, version2):
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    commit1_path = os.path.join(COMMITS_DIR, str(version1))
    commit2_path = os.path.join(COMMITS_DIR, str(version2))

    if not os.path.exists(commit1_path):
        print(f"Error: la versión {version1} no existe.")
        return

    if not os.path.exists(commit2_path):
        print(f"Error: la versión {version2} no existe.")
        return

    metadata1 = load_json(os.path.join(commit1_path, "metadata.json"))
    metadata2 = load_json(os.path.join(commit2_path, "metadata.json"))

    files1 = set(metadata1["files"])
    files2 = set(metadata2["files"])

    all_files = files1.union(files2)

    for file_path in all_files:
        file1 = os.path.join(commit1_path, file_path)
        file2 = os.path.join(commit2_path, file_path)

        print(f"\nDiferencias para archivo: {file_path}")
        print("--------------------------------------")

        if not os.path.exists(file1):
            print("Archivo agregado en la segunda versión.")
            continue

        if not os.path.exists(file2):
            print("Archivo eliminado en la segunda versión.")
            continue

        with open(file1, "r", encoding="utf-8", errors="ignore") as f1:
            content1 = f1.readlines()

        with open(file2, "r", encoding="utf-8", errors="ignore") as f2:
            content2 = f2.readlines()

        diff = difflib.unified_diff(
            content1,
            content2,
            fromfile=f"versión {version1}/{file_path}",
            tofile=f"versión {version2}/{file_path}",
            lineterm=""
        )

        diff_result = list(diff)

        if not diff_result:
            print("No hay diferencias.")
        else:
            for line in diff_result:
                print(line)


def checkout(version):
    if not repository_exists():
        print("Error: no existe un repositorio SBAC.")
        return

    commit_path = os.path.join(COMMITS_DIR, str(version))

    if not os.path.exists(commit_path):
        print(f"Error: la versión {version} no existe.")
        return

    metadata = load_json(os.path.join(commit_path, "metadata.json"))

    for file_path in metadata["files"]:
        source = os.path.join(commit_path, file_path)

        if os.path.exists(source):
            os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
            shutil.copy2(source, file_path)

    print(f"Se regresó correctamente a la versión {version}.")


def main():
    parser = argparse.ArgumentParser(
        description="SBAC - Sistema Básico de Administración de Configuración"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("file")

    subparsers.add_parser("status")

    commit_parser = subparsers.add_parser("commit")
    commit_parser.add_argument("message")

    subparsers.add_parser("history")

    baseline_parser = subparsers.add_parser("baseline")
    baseline_parser.add_argument("name")

    subparsers.add_parser("list-baselines")

    diff_parser = subparsers.add_parser("diff")
    diff_parser.add_argument("version1", type=int)
    diff_parser.add_argument("version2", type=int)

    checkout_parser = subparsers.add_parser("checkout")
    checkout_parser.add_argument("version", type=int)

    args = parser.parse_args()

    if args.command == "init":
        init_repository()
    elif args.command == "add":
        add_file(args.file)
    elif args.command == "status":
        status()
    elif args.command == "commit":
        create_commit(args.message)
    elif args.command == "history":
        history()
    elif args.command == "baseline":
        create_baseline(args.name)
    elif args.command == "list-baselines":
        list_baselines()
    elif args.command == "diff":
        diff_versions(args.version1, args.version2)
    elif args.command == "checkout":
        checkout(args.version)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()