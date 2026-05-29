import os
import json
import shutil
import argparse
import difflib
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


def validate_repository():
    if not repository_exists():
        print("Error: primero debes inicializar el repositorio con: python main.py init")
        return False
    return True


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
    if not validate_repository():
        return

    if not os.path.exists(file_path):
        print(f"Error: el archivo '{file_path}' no existe.")
        return

    if file_path.startswith(SBAC_DIR):
        print("Error: no puedes agregar archivos internos de .sbac.")
        return

    index_data = load_json(INDEX_FILE)

    if file_path in index_data["tracked_files"]:
        print(f"El archivo '{file_path}' ya está en seguimiento.")
        return

    index_data["tracked_files"].append(file_path)
    save_json(INDEX_FILE, index_data)

    print(f"Archivo agregado correctamente: {file_path}")


def status():
    if not validate_repository():
        return

    index_data = load_json(INDEX_FILE)
    tracked_files = index_data["tracked_files"]

    print("\n========== ESTADO DEL REPOSITORIO ==========")

    if not tracked_files:
        print("No hay archivos en seguimiento.")
        print("============================================\n")
        return

    for file_path in tracked_files:
        if os.path.exists(file_path):
            print(f"[OK] En seguimiento: {file_path}")
        else:
            print(f"[ERROR] Archivo faltante: {file_path}")

    print("============================================\n")


def commit(message):
    if not validate_repository():
        return

    index_data = load_json(INDEX_FILE)
    config_data = load_json(CONFIG_FILE)

    tracked_files = index_data["tracked_files"]

    if not tracked_files:
        print("No hay archivos en seguimiento para crear un commit.")
        return

    existing_files = [file for file in tracked_files if os.path.exists(file)]

    if not existing_files:
        print("No hay archivos existentes para guardar en el commit.")
        return

    new_commit_id = config_data["last_commit"] + 1
    commit_folder = os.path.join(COMMITS_DIR, str(new_commit_id))
    os.makedirs(commit_folder)

    copied_files = []

    for file_path in existing_files:
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
    if not validate_repository():
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
    if not validate_repository():
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
    if not validate_repository():
        return

    config_data = load_json(CONFIG_FILE)

    if config_data["last_commit"] == 0:
        print("No hay commits para marcar como línea base.")
        return

    baselines_data = load_json(BASELINES_FILE)

    for baseline in baselines_data["baselines"]:
        if baseline["name"] == name:
            print(f"Error: ya existe una línea base llamada '{name}'.")
            return

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
    if not validate_repository():
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


def get_baseline_commit_id(name):
    baselines_data = load_json(BASELINES_FILE)

    for baseline in baselines_data["baselines"]:
        if baseline["name"] == name:
            return baseline["commit_id"]

    return None


def diff_versions(version1, version2):
    if not validate_repository():
        return

    commit1_folder = os.path.join(COMMITS_DIR, str(version1))
    commit2_folder = os.path.join(COMMITS_DIR, str(version2))

    if not os.path.exists(commit1_folder):
        print(f"Error: la versión {version1} no existe.")
        return

    if not os.path.exists(commit2_folder):
        print(f"Error: la versión {version2} no existe.")
        return

    metadata1 = load_json(os.path.join(commit1_folder, "metadata.json"))
    metadata2 = load_json(os.path.join(commit2_folder, "metadata.json"))

    files1 = set(metadata1["files"])
    files2 = set(metadata2["files"])
    all_files = sorted(files1.union(files2))

    print("\n========== DIFERENCIAS ENTRE VERSIONES ==========")
    print(f"Comparando versión {version1} contra versión {version2}")
    print("=================================================\n")

    for file_path in all_files:
        file1_path = os.path.join(commit1_folder, file_path)
        file2_path = os.path.join(commit2_folder, file_path)

        print(f"\nArchivo: {file_path}")
        print("-----------------------------------------------")

        if not os.path.exists(file1_path):
            print("Archivo agregado en la segunda versión.")
            continue

        if not os.path.exists(file2_path):
            print("Archivo eliminado en la segunda versión.")
            continue

        with open(file1_path, "r", encoding="utf-8", errors="ignore") as file1:
            content1 = file1.readlines()

        with open(file2_path, "r", encoding="utf-8", errors="ignore") as file2:
            content2 = file2.readlines()

        diff = difflib.unified_diff(
            content1,
            content2,
            fromfile=f"version_{version1}/{file_path}",
            tofile=f"version_{version2}/{file_path}",
            lineterm=""
        )

        diff_result = list(diff)

        if not diff_result:
            print("No hay diferencias.")
        else:
            for line in diff_result:
                print(line)

    print("\n=================================================\n")


def diff_baselines(baseline1, baseline2):
    if not validate_repository():
        return

    commit_id_1 = get_baseline_commit_id(baseline1)
    commit_id_2 = get_baseline_commit_id(baseline2)

    if commit_id_1 is None:
        print(f"Error: la línea base '{baseline1}' no existe.")
        return

    if commit_id_2 is None:
        print(f"Error: la línea base '{baseline2}' no existe.")
        return

    print(f"Comparando línea base '{baseline1}' con '{baseline2}'")
    diff_versions(commit_id_1, commit_id_2)


def run_system_check():
    if not validate_repository():
        return

    print("\n========== VERIFICACIÓN GENERAL DEL SISTEMA ==========")

    required_paths = [
        SBAC_DIR,
        COMMITS_DIR,
        INDEX_FILE,
        CONFIG_FILE,
        BASELINES_FILE
    ]

    all_ok = True

    for path in required_paths:
        if os.path.exists(path):
            print(f"[OK] Existe: {path}")
        else:
            print(f"[ERROR] Falta: {path}")
            all_ok = False

    if all_ok:
        print("Resultado: el sistema tiene su estructura interna completa.")
    else:
        print("Resultado: el sistema tiene errores en su estructura interna.")

    print("======================================================\n")


def main():
    parser = argparse.ArgumentParser(
        description="SBAC - Sistema Básico de Administración de Configuración"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Inicializar repositorio")
    subparsers.add_parser("status", help="Mostrar estado del repositorio")
    subparsers.add_parser("history", help="Mostrar historial de versiones")
    subparsers.add_parser("list-baselines", help="Listar líneas base")
    subparsers.add_parser("check", help="Verificar estructura interna del sistema")

    add_parser = subparsers.add_parser("add", help="Agregar archivo al seguimiento")
    add_parser.add_argument("file")

    commit_parser = subparsers.add_parser("commit", help="Crear una nueva versión")
    commit_parser.add_argument("message")

    checkout_parser = subparsers.add_parser("checkout", help="Restaurar una versión")
    checkout_parser.add_argument("version", type=int)

    baseline_parser = subparsers.add_parser("baseline", help="Crear línea base")
    baseline_parser.add_argument("name")

    diff_parser = subparsers.add_parser("diff", help="Comparar dos versiones")
    diff_parser.add_argument("version1", type=int)
    diff_parser.add_argument("version2", type=int)

    diff_baseline_parser = subparsers.add_parser(
        "diff-baseline",
        help="Comparar dos líneas base"
    )
    diff_baseline_parser.add_argument("baseline1")
    diff_baseline_parser.add_argument("baseline2")

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

    elif args.command == "diff":
        diff_versions(args.version1, args.version2)

    elif args.command == "diff-baseline":
        diff_baselines(args.baseline1, args.baseline2)

    elif args.command == "check":
        run_system_check()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()