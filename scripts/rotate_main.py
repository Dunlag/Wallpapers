#!/usr/bin/env python3
"""
Rota los wallpapers de la carpeta Main.

Rellena la carpeta `Main` (la que usa el slideshow de fondo de pantalla de
Windows) con una seleccion aleatoria de cada carpeta de categoria del
repositorio: 2 imagenes por categoria, o 1 si la categoria tiene menos de 2
imagenes disponibles.

DISENO SIN BORRADO: en vez de vaciar Main y volver a crear archivos (lo que
requiere permiso de borrado y en ejecuciones automaticas desatendidas puede
pedir aprobacion cada dia), este script mantiene un conjunto FIJO de nombres
de archivo "slot_NNN.jpg" y simplemente SOBRESCRIBE su contenido cada vez
(convirtiendo cada imagen elegida a JPEG). Sobrescribir un archivo existente
no requiere el permiso especial de borrado, solo el de escritura que ya se
concede al conectar la carpeta.

Si el numero de imagenes a colocar esta ejecucion es menor que en la
ejecucion anterior, los slots sobrantes se intentan borrar (best effort);
si eso falla por permisos, simplemente se dejan como estan (quedaran
sobreescritos en la siguiente rotacion en la que vuelvan a hacer falta) en
vez de hacer fallar todo el script.

Debe ejecutarse con el directorio de trabajo (cwd) puesto en la raiz del
proyecto Wallpapers (donde estan Main, Animes, Cities, etc.). No usa rutas
absolutas para que funcione igual sin importar donde este montada la
carpeta en cada ejecucion.
"""

import os
import random
import sys

from PIL import Image

ROOT = os.getcwd()
MAIN_DIR = os.path.join(ROOT, "Main")

# Carpetas que NO son categorias de wallpapers y deben ignorarse.
EXCLUDE_DIRS = {"Main", "assets", "scripts", ".git", ".github"}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

PER_CATEGORY = 2

SLOT_PREFIX = "slot_"
SLOT_SUFFIX = ".jpg"


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


def slot_name(index):
    return f"{SLOT_PREFIX}{index:03d}{SLOT_SUFFIX}"


def existing_slot_indices(main_dir):
    indices = []
    for f in os.listdir(main_dir):
        if f.startswith(SLOT_PREFIX) and f.endswith(SLOT_SUFFIX):
            middle = f[len(SLOT_PREFIX):-len(SLOT_SUFFIX)]
            if middle.isdigit():
                indices.append(int(middle))
    return sorted(indices)


def write_slot(src_path, dst_path):
    """Convierte src_path a JPEG y lo escribe (sobrescribiendo) en dst_path."""
    with Image.open(src_path) as img:
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        elif img.mode != "RGB":
            img = img.convert("RGB")
        img.save(dst_path, "JPEG", quality=92)


def cleanup_extra_slots(main_dir, used_count, previous_indices):
    """Best effort: borra slots que ya no hacen falta. Si falla por permisos,
    lo ignora en vez de interrumpir el script."""
    removed = 0
    for idx in previous_indices:
        if idx > used_count:
            full = os.path.join(main_dir, slot_name(idx))
            try:
                if os.path.isfile(full):
                    os.remove(full)
                    removed += 1
            except PermissionError:
                pass
    return removed


def cleanup_legacy_files(main_dir):
    """Best effort: borra archivos que no siguen el patron slot_NNN.jpg
    (restos de versiones anteriores del script que si borraban Main). Si no
    hay permiso de borrado disponible esta ejecucion, simplemente los deja
    y lo intenta de nuevo la proxima vez."""
    removed = 0
    left = 0
    for f in os.listdir(main_dir):
        full = os.path.join(main_dir, f)
        if not os.path.isfile(full):
            continue
        is_slot = f.startswith(SLOT_PREFIX) and f.endswith(SLOT_SUFFIX) and f[len(SLOT_PREFIX):-len(SLOT_SUFFIX)].isdigit()
        if is_slot:
            continue
        try:
            os.remove(full)
            removed += 1
        except PermissionError:
            left += 1
    return removed, left


def main():
    if not os.path.isdir(MAIN_DIR):
        print(f"ERROR: no existe la carpeta Main en {ROOT}", file=sys.stderr)
        sys.exit(1)

    categories = list_categories(ROOT)
    if not categories:
        print("ERROR: no se encontraron carpetas de categoria.", file=sys.stderr)
        sys.exit(1)

    previous_indices = existing_slot_indices(MAIN_DIR)

    chosen = []
    slot_idx = 0
    skipped = []

    for category in categories:
        cat_path = os.path.join(ROOT, category)
        images = list_images(cat_path)
        if not images:
            continue

        n = PER_CATEGORY if len(images) >= PER_CATEGORY else 1
        picks = random.sample(images, n)

        for filename in picks:
            slot_idx += 1
            src = os.path.join(cat_path, filename)
            dst = os.path.join(MAIN_DIR, slot_name(slot_idx))
            try:
                write_slot(src, dst)
            except Exception as e:
                skipped.append((category, filename, str(e)))
                slot_idx -= 1
                continue
            chosen.append((category, filename))

    removed = cleanup_extra_slots(MAIN_DIR, slot_idx, previous_indices)
    legacy_removed, legacy_left = cleanup_legacy_files(MAIN_DIR)
    removed += legacy_removed

    print(f"Rotacion completada: {len(chosen)} wallpapers colocados en Main ({len(categories)} categorias)")
    for category, filename in chosen:
        print(f"  [{category}] {filename}")
    if removed:
        print(f"  (limpiados {removed} archivos sobrantes/legacy de Main)")
    if legacy_left:
        print(
            f"  AVISO: quedan {legacy_left} archivos antiguos en Main que no se "
            "pudieron borrar por falta de permiso de borrado esta ejecucion; "
            "se reintentara en la proxima rotacion.",
            file=sys.stderr,
        )
    if skipped:
        print(f"  AVISO: {len(skipped)} imagenes no se pudieron procesar:", file=sys.stderr)
        for category, filename, err in skipped:
            print(f"    [{category}] {filename}: {err}", file=sys.stderr)


if __name__ == "__main__":
    main()
