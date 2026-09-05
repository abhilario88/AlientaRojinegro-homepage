#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Actualización del Catálogo - Alienta Rojinegro
Lee configuracion.csv y productos.csv, valida la integridad de los datos,
escanea automáticamente las imágenes de cada producto,
genera versiones optimizadas en assets/optimized/ y compila catalogo.js y catalogo.json.
"""

import os
import sys
import csv
import json
import re
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def natural_sort_key(s):
    """Permite ordenar archivos como 1, 2, 10 en lugar de 1, 10, 2."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def find_images_dir():
    """Localiza la carpeta de imágenes respetando mayúsculas/minúsculas."""
    for candidate in ["Imagenes", "imagenes", "IMAGENES"]:
        p = BASE_DIR / candidate
        if p.is_dir():
            return p
    return BASE_DIR / "Imagenes"

def optimize_image(src_path, dest_path, max_dimension=1200):
    """
    Optimiza una imagen usando la herramienta nativa de macOS 'sips'.
    No altera nunca el archivo original.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Si el archivo de destino existe y es más reciente que el origen, omitir
    if dest_path.exists() and dest_path.stat().st_mtime >= src_path.stat().st_mtime:
        return

    # Si sips está disponible en macOS
    sips_bin = shutil.which("sips")
    if sips_bin:
        try:
            # Copiar primero al destino y luego redimensionar
            shutil.copy2(src_path, dest_path)
            subprocess.run(
                [sips_bin, "-Z", str(max_dimension), str(dest_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return
        except Exception:
            # Si sips falla por alguna razón, usar la copia directa
            pass

    shutil.copy2(src_path, dest_path)

def main():
    print("==================================================")
    print("      ALIENTA ROJINEGRO - ACTUALIZADOR WEB        ")
    print("==================================================")
    print("")

    datos_dir = BASE_DIR / "datos"
    config_file = datos_dir / "configuracion.csv"
    productos_file = datos_dir / "productos.csv"
    imagenes_dir = find_images_dir()
    productos_dir = imagenes_dir / "productos"
    optimized_dir = BASE_DIR / "assets" / "optimized"

    errores = []
    advertencias = []

    # 1. Validar existencia de archivos CSV
    if not config_file.exists():
        errores.append(f"No se encontró el archivo de configuración: {config_file}")
    if not productos_file.exists():
        errores.append(f"No se encontró el archivo de productos: {productos_file}")

    if errores:
        print("❌ ERRORES CRÍTICOS:")
        for err in errores:
            print(f"  - {err}")
        sys.exit(1)

    # 2. Leer configuracion.csv
    config = {}
    try:
        with open(config_file, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row_num, row in enumerate(reader, start=2):
                if not row or len(row) < 2:
                    continue
                clave = row[0].strip()
                valor = row[1].strip()
                config[clave] = valor
    except Exception as e:
        errores.append(f"Error al leer configuracion.csv: {e}")

    # Validar campos mínimos de configuración
    whatsapp = config.get("whatsapp", "").strip()
    if not whatsapp:
        errores.append("El campo 'whatsapp' en configuracion.csv no puede estar vacío.")
    else:
        # Limpiar caracteres no numéricos para validación de formato
        clean_wa = re.sub(r"[^\d]", "", whatsapp)
        if len(clean_wa) < 8:
            errores.append(f"El número de WhatsApp '{whatsapp}' no parece un número de teléfono válido.")
        config["whatsapp"] = clean_wa

    if not config.get("tituloHero"):
        config["tituloHero"] = "Hecho para el que alienta."
    if not config.get("textoHero"):
        config["textoHero"] = "Productos rojinegros para llevar tu pasión a todas partes."
    if not config.get("ctaHero"):
        config["ctaHero"] = "VER PRODUCTOS →"
    if not config.get("dominio"):
        config["dominio"] = "alientarojinegro.com"

    # 3. Leer y validar productos.csv
    productos = []
    ids_vistos = set()
    carpetas_vistas = set()
    valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    try:
        with open(productos_file, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            required_cols = {"id", "nombre", "precio", "carpeta", "descripcion", "activo"}
            if not required_cols.issubset(set(reader.fieldnames or [])):
                missing = required_cols - set(reader.fieldnames or [])
                errores.append(f"productos.csv no contiene las columnas requeridas: {', '.join(missing)}")
            else:
                for row_idx, row in enumerate(reader, start=2):
                    p_id = (row.get("id") or "").strip()
                    nombre = (row.get("nombre") or "").strip()
                    precio_str = (row.get("precio") or "").strip()
                    carpeta = (row.get("carpeta") or "").strip()
                    descripcion = (row.get("descripcion") or "").strip()
                    activo_str = (row.get("activo") or "").strip().lower()

                    # Omitir filas totalmente vacías
                    if not any([p_id, nombre, precio_str, carpeta, descripcion, activo_str]):
                        continue

                    # Validación de activo
                    if activo_str in ["sí", "si", "true", "1", "yes", "s"]:
                        activo = True
                    elif activo_str in ["no", "false", "0", "n"]:
                        activo = False
                    else:
                        errores.append(f"Fila {row_idx}: Valor inválido en 'activo' ('{activo_str}'). Debe ser 'sí' o 'no'.")
                        activo = False

                    # Validación de ID
                    if not p_id:
                        errores.append(f"Fila {row_idx}: Falta el ID del producto '{nombre}'.")
                    elif p_id in ids_vistos:
                        errores.append(f"Fila {row_idx}: ID duplicado '{p_id}'.")
                    else:
                        ids_vistos.add(p_id)

                    # Validación de Nombre
                    if not nombre:
                        errores.append(f"Fila {row_idx}: Producto sin nombre (ID: {p_id}).")

                    # Validación de Precio
                    try:
                        precio = float(re.sub(r"[^\d.]", "", precio_str))
                        if precio < 0:
                            errores.append(f"Fila {row_idx} ('{nombre}'): El precio no puede ser negativo.")
                    except ValueError:
                        errores.append(f"Fila {row_idx} ('{nombre}'): Precio inválido ('{precio_str}').")
                        precio = 0.0

                    # Validación de Carpeta
                    if not carpeta:
                        errores.append(f"Fila {row_idx} ('{nombre}'): Falta especificar la carpeta.")
                        continue

                    if carpeta in carpetas_vistas:
                        errores.append(f"Fila {row_idx} ('{nombre}'): Carpeta duplicada '{carpeta}'.")
                    else:
                        carpetas_vistas.add(carpeta)

                    # Verificar carpeta física
                    target_dir = productos_dir / carpeta
                    if not target_dir.is_dir():
                        errores.append(f"Fila {row_idx} ('{nombre}'): La carpeta '{target_dir}' no existe.")
                        continue

                    # Escanear imágenes dentro de la carpeta
                    archivos_en_carpeta = [
                        f for f in target_dir.iterdir()
                        if f.is_file() and f.suffix.lower() in valid_extensions and not f.name.startswith(".")
                    ]

                    # Ordenar alfanuméricamente
                    archivos_en_carpeta.sort(key=lambda x: natural_sort_key(x.name))

                    if not archivos_en_carpeta:
                        if activo:
                            errores.append(f"Fila {row_idx} ('{nombre}'): La carpeta '{carpeta}' no contiene imágenes compatibles (.png, .jpg, .jpeg, .webp).")
                        else:
                            advertencias.append(f"La carpeta '{carpeta}' del producto inactivo '{nombre}' no tiene imágenes.")

                    if activo:
                        productos.append({
                            "id": p_id,
                            "nombre": nombre,
                            "precio": int(precio) if precio.is_integer() else precio,
                            "carpeta": carpeta,
                            "descripcion": descripcion,
                            "archivos_originales": archivos_en_carpeta
                        })
    except Exception as e:
        errores.append(f"Error al procesar productos.csv: {e}")

    # Si hay errores de validación, detener la ejecución con detalle
    if errores:
        print("❌ SE ENCONTRARON ERRORES QUE DEBES CORREGIR:")
        for err in errores:
            print(f"  • {err}")
        print("\nPor favor corrige estos datos en datos/productos.csv o configuracion.csv y vuelve a intentarlo.")
        sys.exit(1)

    if advertencias:
        print("⚠️  ADVERTENCIAS:")
        for adv in advertencias:
            print(f"  • {adv}")
        print("")

    # 4. Optimizar recursos globales (Hero y Logos)
    print("⏳ Procesando recursos visuales de la web...")
    
    # Hero
    hero_src = imagenes_dir / "hero" / "HERO.png"
    hero_dest = optimized_dir / "hero" / "HERO.png"
    if hero_src.exists():
        optimize_image(hero_src, hero_dest, max_dimension=1600)
    else:
        advertencias.append(f"No se encontró la imagen Hero en {hero_src}")

    # Logos
    logos_src_dir = imagenes_dir / "logos"
    logos_dest_dir = optimized_dir / "logos"
    if logos_src_dir.is_dir():
        for logo_file in logos_src_dir.iterdir():
            if logo_file.is_file() and logo_file.suffix.lower() in valid_extensions:
                optimize_image(logo_file, logos_dest_dir / logo_file.name, max_dimension=800)

    # Favicon: generar a partir de Sello.png o Logo.png si existe
    sello_path = logos_src_dir / "Sello.png"
    favicon_dest = BASE_DIR / "favicon.png"
    if sello_path.exists():
        optimize_image(sello_path, favicon_dest, max_dimension=128)

    # 5. Optimizar imágenes de cada producto y preparar estructura para el catálogo
    productos_salida = []
    total_imagenes = 0

    for prod in productos:
        carpeta = prod["carpeta"]
        nombre = prod["nombre"]
        rutas_web = []

        prod_dest_dir = optimized_dir / "productos" / carpeta

        for orig_file in prod["archivos_originales"]:
            dest_file = prod_dest_dir / orig_file.name
            optimize_image(orig_file, dest_file, max_dimension=1000)
            
            # Ruta web relativa
            rel_path = f"assets/optimized/productos/{carpeta}/{orig_file.name}"
            rutas_web.append(rel_path)
            total_imagenes += 1

        productos_salida.append({
            "id": prod["id"],
            "nombre": prod["nombre"],
            "precio": prod["precio"],
            "carpeta": carpeta,
            "descripcion": prod["descripcion"],
            "imagenes": rutas_web
        })

    # 6. Generar catalogo.json y catalogo.js
    catalogo_payload = {
        "config": {
            "whatsapp": config.get("whatsapp", ""),
            "tituloHero": config.get("tituloHero", ""),
            "textoHero": config.get("textoHero", ""),
            "ctaHero": config.get("ctaHero", ""),
            "instagram": config.get("instagram", ""),
            "facebook": config.get("facebook", ""),
            "tiktok": config.get("tiktok", ""),
            "dominio": config.get("dominio", "alientarojinegro.com")
        },
        "productos": productos_salida
    }

    json_path = datos_dir / "catalogo.json"
    js_path = datos_dir / "catalogo.js"

    with open(json_path, mode="w", encoding="utf-8") as f:
        json.dump(catalogo_payload, f, ensure_ascii=False, indent=2)

    with open(js_path, mode="w", encoding="utf-8") as f:
        f.write("/* Generado automáticamente por Actualizar.command - No editar manualmente */\n")
        f.write("window.CATALOGO_DATA = ")
        json.dump(catalogo_payload, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print("\n✅ ¡ACTUALIZACIÓN COMPLETADA CON ÉXITO!")
    print("--------------------------------------------------")
    print(f"📦 Productos activos procesados : {len(productos_salida)}")
    print(f"🖼️  Imágenes procesadas          : {total_imagenes}")
    print(f"📄 Archivo generado             : {js_path.relative_to(BASE_DIR)}")
    print(f"📄 Archivo generado             : {json_path.relative_to(BASE_DIR)}")
    print("--------------------------------------------------")
    for p in productos_salida:
        num_imgs = len(p["imagenes"])
        tipo_galeria = "Carrusel dinámico" if num_imgs > 1 else "Imagen estática"
        print(f"  • {p['nombre']:<24} : S/ {p['precio']:<4} ({num_imgs} foto{'s' if num_imgs > 1 else ''} - {tipo_galeria})")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    main()
