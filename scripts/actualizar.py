#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Actualización del Catálogo - Alienta Rojinegro
Lee configuracion.csv y productos.csv, valida la integridad de los datos,
escanea automáticamente las imágenes de cada producto,
genera versiones de alto rendimiento en assets/optimized/ y compila catalogo.js y catalogo.json.
"""

import os
import sys
import csv
import json
import re
import shutil
import subprocess
import zlib
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

def lossless_compress_png(png_path):
    """Recomprime los datos IDAT de un PNG con zlib nivel 9 para reducir tamaño sin perder un solo pixel."""
    try:
        with open(png_path, 'rb') as f:
            data = f.read()
        if len(data) < 8 or data[:8] != b'\x89PNG\r\n\x1a\n':
            return
        
        pos = 8
        chunks = []
        idat = b''
        while pos < len(data):
            chunk_len = int.from_bytes(data[pos:pos+4], 'big')
            chunk_type = data[pos+4:pos+8]
            chunk_data = data[pos+8:pos+8+chunk_len]
            crc = data[pos+8+chunk_len:pos+12+chunk_len]
            
            if chunk_type == b'IDAT':
                idat += chunk_data
            else:
                chunks.append((chunk_type, chunk_data))
            pos += 12 + chunk_len
            
        if not idat:
            return
            
        decompressed = zlib.decompress(idat)
        comp = zlib.compressobj(level=9, wbits=15, memLevel=9)
        new_idat = comp.compress(decompressed) + comp.flush()
        
        # Solo escribir si la recompreción es más compacta
        if len(new_idat) >= len(idat):
            return
            
        out = b'\x89PNG\r\n\x1a\n'
        for ctype, cdata in chunks:
            if ctype == b'IHDR':
                out += len(cdata).to_bytes(4, 'big') + ctype + cdata + zlib.crc32(ctype + cdata).to_bytes(4, 'big')
                break
                
        out += len(new_idat).to_bytes(4, 'big') + b'IDAT' + new_idat + zlib.crc32(b'IDAT' + new_idat).to_bytes(4, 'big')
        
        for ctype, cdata in chunks:
            if ctype != b'IHDR':
                out += len(cdata).to_bytes(4, 'big') + ctype + cdata + zlib.crc32(ctype + cdata).to_bytes(4, 'big')
                
        with open(png_path, 'wb') as f:
            f.write(out)
    except Exception:
        pass

def optimize_image(src_path, dest_path, max_dimension=700, format_type=None, quality=85):
    """
    Optimiza una imagen usando 'sips' nativo de macOS y recompresión zlib.
    No altera nunca el archivo original.
    """
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    sips_bin = shutil.which("sips")
    if sips_bin:
        try:
            shutil.copy2(src_path, dest_path)
            cmd = [sips_bin, "-Z", str(max_dimension)]
            if format_type == "jpeg":
                cmd.extend(["-s", "format", "jpeg", "-s", "formatOptions", str(quality)])
            cmd.append(str(dest_path))
            
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            if dest_path.suffix.lower() == ".png":
                lossless_compress_png(dest_path)
            return
        except Exception:
            pass

    shutil.copy2(src_path, dest_path)
    if dest_path.suffix.lower() == ".png":
        lossless_compress_png(dest_path)

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

    # Validar WhatsApp
    whatsapp = config.get("whatsapp", "").strip()
    clean_wa = re.sub(r"[^\d]", "", whatsapp)
    if not clean_wa or len(clean_wa) < 8:
        errores.append(f"El número de WhatsApp '{whatsapp}' no parece un número válido.")
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

                    if not any([p_id, nombre, precio_str, carpeta, descripcion, activo_str]):
                        continue

                    if activo_str in ["sí", "si", "true", "1", "yes", "s"]:
                        activo = True
                    elif activo_str in ["no", "false", "0", "n"]:
                        activo = False
                    else:
                        errores.append(f"Fila {row_idx}: Valor inválido en 'activo' ('{activo_str}'). Debe ser 'sí' o 'no'.")
                        activo = False

                    if not p_id:
                        errores.append(f"Fila {row_idx}: Falta el ID del producto '{nombre}'.")
                    elif p_id in ids_vistos:
                        errores.append(f"Fila {row_idx}: ID duplicado '{p_id}'.")
                    else:
                        ids_vistos.add(p_id)

                    if not nombre:
                        errores.append(f"Fila {row_idx}: Producto sin nombre (ID: {p_id}).")

                    try:
                        precio = float(re.sub(r"[^\d.]", "", precio_str))
                        if precio < 0:
                            errores.append(f"Fila {row_idx} ('{nombre}'): El precio no puede ser negativo.")
                    except ValueError:
                        errores.append(f"Fila {row_idx} ('{nombre}'): Precio inválido ('{precio_str}').")
                        precio = 0.0

                    if not carpeta:
                        errores.append(f"Fila {row_idx} ('{nombre}'): Falta especificar la carpeta.")
                        continue

                    if carpeta in carpetas_vistas:
                        errores.append(f"Fila {row_idx} ('{nombre}'): Carpeta duplicada '{carpeta}'.")
                    else:
                        carpetas_vistas.add(carpeta)

                    target_dir = productos_dir / carpeta
                    if not target_dir.is_dir():
                        errores.append(f"Fila {row_idx} ('{nombre}'): La carpeta '{target_dir}' no existe.")
                        continue

                    archivos_en_carpeta = [
                        f for f in target_dir.iterdir()
                        if f.is_file() and f.suffix.lower() in valid_extensions and not f.name.startswith(".")
                    ]
                    archivos_en_carpeta.sort(key=lambda x: natural_sort_key(x.name))

                    if not archivos_en_carpeta:
                        if activo:
                            errores.append(f"Fila {row_idx} ('{nombre}'): La carpeta '{carpeta}' no contiene imágenes compatibles.")
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

    if errores:
        print("❌ SE ENCONTRARON ERRORES QUE DEBES CORREGIR:")
        for err in errores:
            print(f"  • {err}")
        sys.exit(1)

    # 4. Optimizar recursos globales (Hero y Logos)
    print("⏳ Optimizando recursos visuales para carga ultrarrápida...")
    
    # Hero: generar versión JPEG super liviana (150KB) y PNG optimizada
    hero_src = imagenes_dir / "hero" / "HERO.png"
    if hero_src.exists():
        optimize_image(hero_src, optimized_dir / "hero" / "HERO.jpg", max_dimension=1200, format_type="jpeg", quality=85)
        optimize_image(hero_src, optimized_dir / "hero" / "HERO.png", max_dimension=1200)

    # Logos
    logos_src_dir = imagenes_dir / "logos"
    logos_dest_dir = optimized_dir / "logos"
    if logos_src_dir.is_dir():
        # Sello: optimizado para 250px (pesa ~70KB en vez de 1.1MB)
        sello_src = logos_src_dir / "Sello.png"
        if sello_src.exists():
            optimize_image(sello_src, logos_dest_dir / "Sello.png", max_dimension=280)
            
        # Logo horizontal: optimizado para 600px
        logo_h_src = logos_src_dir / "LogoHorizontal.png"
        if logo_h_src.exists():
            optimize_image(logo_h_src, logos_dest_dir / "LogoHorizontal.png", max_dimension=600)
            
        logo_sq_src = logos_src_dir / "Logo.png"
        if logo_sq_src.exists():
            optimize_image(logo_sq_src, logos_dest_dir / "Logo.png", max_dimension=600)

    # Favicon
    if sello_src.exists():
        optimize_image(sello_src, BASE_DIR / "favicon.png", max_dimension=128)

    # 5. Optimizar imágenes de cada producto
    productos_salida = []
    total_imagenes = 0

    for prod in productos:
        carpeta = prod["carpeta"]
        rutas_web = []
        prod_dest_dir = optimized_dir / "productos" / carpeta

        for orig_file in prod["archivos_originales"]:
            dest_file = prod_dest_dir / orig_file.name
            # Optimizar a max 680px (suficiente para 2x retina y carga instantánea)
            optimize_image(orig_file, dest_file, max_dimension=680)
            
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

    print("\n✅ ¡OPTIMIZACIÓN COMPLETADA CON ÉXITO!")
    print("--------------------------------------------------")
    print(f"📦 Productos activos procesados : {len(productos_salida)}")
    print(f"🖼️  Imágenes procesadas          : {total_imagenes}")
    print(f"📄 Archivo generado             : {js_path.relative_to(BASE_DIR)}")
    print(f"📄 Archivo generado             : {json_path.relative_to(BASE_DIR)}")
    print("--------------------------------------------------\n")

if __name__ == "__main__":
    main()
