#!/usr/bin/env python3
"""
Rota los fondos de pantalla de la carpeta Main eligiendo aleatoriamente
2 imagenes (o 1 si solo hay una) de cada carpeta tematica del repositorio
de Wallpapers.

Uso:
    python3 rotate_wallpapers.py /ruta/a/Wallpapers
"""
import os
import random
import shutil
import sys

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
EXCLUDED_DIRS = {"main", "assets", ".git"}


def is_image(filename: str) -> bool:
    return os.path.splitext(filename)[1].lower() in IMAGE_EXTS


def pick_images(root: str):
    """Devuelve una lista de tuplas (carpeta_tematica, ruta_completa) elegidas."""
    picks = []
    for entry in sorted(os.listdir(root)):
        full_path = os.path.join(root, entry)
        if not os.path.isdir(full_path):
            continue
        if entry.lower() in EXCLUDED_DIRS:
            continue

        images = [f for f in os.listdir(full_path) if is_image(f)]
        if not images:
            continue

        n = 2 if len(images) >= 2 else 1
        chosen = random.sample(images, n)
        for img in chosen:
            picks.append((entry, os.path.join(full_path, img)))
    return picks


def clear_main(main_dir: str):
    for f in os.listdir(main_dir):
        full_path = os.path.join(main_dir, f)
        if os.path.isfile(full_path) and is_image(f):
            os.remove(full_path)


def copy_picks(picks, main_dir: str):
    used_names = set()
    for theme, src in picks:
        filename = os.path.basename(src)
        dest_name = filename
        if dest_name in used_names:
            base, ext = os.path.splitext(filename)
            dest_name = f"{theme}_{base}{ext}"
        used_names.add(dest_name)
        shutil.copy2(src, os.path.join(main_dir, dest_name))
    return used_names


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 rotate_wallpapers.py /ruta/a/Wallpapers")
        sys.exit(1)

    root = sys.argv[1]
    main_dir = os.path.join(root, "Main")
    if not os.path.isdir(main_dir):
        print(f"No se encontro la carpeta Main en {root}")
        sys.exit(1)

    picks = pick_images(root)
    print(f"Se han elegido {len(picks)} imagenes de {len(set(t for t, _ in picks))} carpetas tematicas:")
    for theme, src in picks:
        print(f"  [{theme}] {os.path.basename(src)}")

    clear_main(main_dir)
    final_names = copy_picks(picks, main_dir)

    print(f"\nCarpeta Main actualizada con {len(final_names)} imagenes nuevas.")


if __name__ == "__main__":
    main()
