# SBAC - Sistema Básico de Administración de Configuración

## Descripción

SBAC (Sistema Básico de Administración de Configuración) es una aplicación desarrollada en Python que permite llevar un control básico de versiones de archivos dentro de un proyecto.

El sistema fue desarrollado como una implementación simplificada de un sistema de control de versiones similar a Git, enfocándose en conceptos fundamentales de administración de configuración de software.

Permite registrar archivos, guardar versiones, consultar historial, restaurar estados anteriores, crear líneas base y comparar cambios entre distintas versiones.

---

# Objetivo

El objetivo principal del proyecto es desarrollar una herramienta básica de administración de configuración que permita:

- Inicializar un repositorio local
- Agregar archivos al seguimiento
- Consultar el estado del repositorio
- Crear versiones del proyecto mediante commits
- Consultar historial de versiones
- Restaurar versiones anteriores
- Crear líneas base
- Listar líneas base registradas
- Comparar diferencias entre versiones
- Comparar cambios entre líneas base

---

# Estructura del sistema

Una vez inicializado el repositorio, el sistema genera automáticamente la siguiente estructura:

```bash
.sbac/
│
├── commits/
│
├── index.json
│
├── config.json
│
└── baselines.json
```

---

# Descripción de archivos internos

## `.sbac/`

Carpeta principal del repositorio interno del sistema.

Aquí se almacena toda la información relacionada con el control de versiones.

---

## `commits/`

Contiene todas las versiones creadas mediante commits.

Cada commit se almacena dentro de una carpeta numerada:

```bash
.sbac/commits/1/
.sbac/commits/2/
.sbac/commits/3/
```

Cada carpeta contiene:

- copia completa de los archivos registrados
- archivo `metadata.json`

---

## `index.json`

Almacena los archivos registrados en seguimiento.

Ejemplo:

```json
{
  "tracked_files": [
    "main.py",
    "hola.py"
  ]
}
```

---

## `config.json`

Guarda configuración general del sistema.

Ejemplo:

```json
{
  "last_commit": 3
}
```

Indica cuál fue el último commit creado.

---

## `baselines.json`

Guarda las líneas base creadas por el usuario.

Ejemplo:

```json
{
  "baselines": [
    {
      "name": "estable1",
      "commit_id": 3,
      "date": "2026-05-28 19:00:00"
    }
  ]
}
```

---

# Funcionamiento del sistema

## 1. Inicializar repositorio

### Comando

```bash
python main.py init
```

### Función

Crea la estructura interna del sistema:

- `.sbac/`
- `commits/`
- `index.json`
- `config.json`
- `baselines.json`

---

## 2. Agregar archivo al seguimiento

### Comando

```bash
python main.py add <archivo>
```

### Ejemplo

```bash
python main.py add hola.py
```

### Función

Registra un archivo dentro de `index.json` para que pueda ser incluido en futuros commits.

---

## 3. Consultar estado del repositorio

### Comando

```bash
python main.py status
```

### Función

Muestra el estado actual del repositorio:

- archivos en seguimiento
- archivos existentes
- archivos faltantes

---

## 4. Crear commit

### Comando

```bash
python main.py commit "mensaje"
```

### Ejemplo

```bash
python main.py commit "Primera versión"
```

### Función

Genera una nueva versión del proyecto.

Durante el commit el sistema:

1. Lee los archivos registrados en `index.json`
2. Crea una nueva carpeta dentro de `commits/`
3. Copia los archivos actuales
4. Genera `metadata.json`
5. Actualiza `last_commit`

Ejemplo:

```bash
.sbac/commits/1/
```

---

## 5. Consultar historial de versiones

### Comando

```bash
python main.py history
```

### Función

Muestra todos los commits registrados incluyendo:

- ID
- fecha
- mensaje
- archivos incluidos

---

## 6. Restaurar versión anterior

### Comando

```bash
python main.py checkout <versión>
```

### Ejemplo

```bash
python main.py checkout 1
```

### Función

Restaura el proyecto al estado guardado dentro del commit seleccionado.

---

## 7. Crear línea base

### Comando

```bash
python main.py baseline <nombre>
```

### Ejemplo

```bash
python main.py baseline estable1
```

### Función

Marca el último commit como una versión estable del sistema.

---

## 8. Listar líneas base

### Comando

```bash
python main.py list-baselines
```

### Función

Muestra todas las líneas base registradas dentro del sistema.

---

## 9. Comparar versiones

### Comando

```bash
python main.py diff <version1> <version2>
```

### Ejemplo

```bash
python main.py diff 1 2
```

### Función

Compara dos versiones distintas del proyecto y muestra las diferencias entre archivos línea por línea.

Utiliza la librería `difflib` de Python.

---

## 10. Comparar líneas base

### Comando

```bash
python main.py diff-baseline <baseline1> <baseline2>
```

### Ejemplo

```bash
python main.py diff-baseline estable1 estable2
```

### Función

Compara los commits asociados a dos líneas base.

---

## 11. Verificación general del sistema

### Comando

```bash
python main.py check
```

### Función

Verifica que existan todos los archivos internos requeridos:

- `.sbac/`
- `commits/`
- `index.json`
- `config.json`
- `baselines.json`

---

# Flujo de uso del sistema

Ejemplo completo de ejecución:

```bash
python main.py init

python main.py add hola.py

python main.py status

python main.py commit "Primera versión"

python main.py baseline estable1

python main.py history

python main.py diff 1 2

python main.py diff-baseline estable1 estable2

python main.py checkout 1

python main.py check
```

---

# Librerías utilizadas

El sistema fue desarrollado utilizando bibliotecas estándar de Python:

- `os` → manejo de archivos y directorios
- `json` → lectura y escritura de archivos JSON
- `shutil` → copia de archivos
- `argparse` → línea de comandos
- `difflib` → comparación entre versiones
- `datetime` → generación de fechas y timestamps

---

# Consideraciones técnicas

- El sistema funciona localmente
- No requiere conexión a internet
- No utiliza base de datos externa
- Toda la persistencia se realiza mediante archivos JSON
- Los commits almacenan snapshots completos de archivos
- Está enfocado al control básico de configuración y versionado local

---

# Conclusión

SBAC implementa un sistema básico de administración de configuración que permite controlar versiones de archivos dentro de un proyecto de forma local.

A través del manejo de commits, historial, líneas base y comparación entre versiones, el sistema permite aplicar conceptos fundamentales de administración de configuración de software y control de versiones.
