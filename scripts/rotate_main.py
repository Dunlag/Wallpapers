#!/usr/bin/env python3
"""
Rota los wallpapers de la carpeta Main.

Vacia por completo la carpeta `Main` (la que usa el slideshow de fondo de
pantalla de Windows) y la rellena con una seleccion aleatoria de cada
carpeta de categoria del repositorio: 2 imagenes por categoria, o 1 si la
categoria tiene menos de 2 imagenes disponibles.

Debe ejecutarse con el directorio de trabajo (cwd) puesto en la raiz del
proyecto Wallpapers (donde estan Main, Animes, Cities, etc.). No usa rutas
absolutas para que funcione igual sin importar donde este montada la
carpeta en cada ejecucion.

IMPORTANTE: si borrar archivos de Main falla con "Operation not permitted",
hay que llamar primero a la tool `mcp__cowork__allow_cowork_file_delete`
sobre un archivo dentro de Main para habilitar el borrado en esa carpeta,
y volver a ejecutar este script.
"""

import os
import random
import shutil
import sys

ROOT = os.getcwd()
MAIN_DIR = os.path.join(ROOT, "Main")

# Carpetas que NO son categorias de wallpapers y deben ignorarse.
EXCLUDE_DIRS = {"Main", "assets", "scripts", ".git", ".github"}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

PER_CATEGORY = 2


def is_image(filename):
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS


def list_categories(root):
    categories = []
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isdir(full) and name not in EXCLUDE_DIRS and not name.startswith("."):
            categories.append(name)
    return categories


def list_images(folder):
    return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and is_image(f)]


def clear_main(main_dir):
    for f in os.listdir(main_dir):
        full = os.path.join(main_dir, f)
        if os.path.isfile(full):
            os.remove(full)


def main():
    if not os.path.isdir(MAIN_DIR):
        print(f"ERROR: no existe la carpeta Main en {ROOT}", file=sys.stderr)
        sys.exit(1)

    categories = list_categories(ROOT)
    if not categories:
        print("ERROR: no se encontraron carpetas de categoria.", file=sys.stderr)
        sys.exit(1)

    try:
        clear_main(MAIN_DIR)
    except PermissionError as e:
        print(
            "ERROR: no se pudo borrar el contenido de Main (Operation not permitted). "
            "Hay que habilitar el borrado con la tool allow_cowork_file_delete sobre "
            "un archivo dentro de Main y volver a lanzar el script.",
            file=sys.stderr,
        )
        raise

    chosen = []
    used_names = set()

    for category in categories:
        cat_path = os.path.join(ROOT, category)
        images = list_images(cat_path)
        if not images:
            continue

        n = PER_CATEGORY if len(images) >= PER_CATEGORY else 1
        picks = random.sample(images, n)

        for filename in picks:
            src = os.path.join(cat_path, filename)
            dst_name = filename
            if dst_name in used_names:
                dst_name = f"{category.replace(' ', '_')}_{filename}"
            used_names.add(dst_name)
            dst = os.path.join(MAIN_DIR, dst_name)
            shutil.copy2(src, dst)
            chosen.append((category, filename))

    print(f"Rotacion completada: {len(chosen)} wallpapers colocados en Main ({len(categories)} categorias)")
    for category, filename in chosen:
        print(f"  [{category}] {filename}")


if __name__ == "__main__":
    main()
