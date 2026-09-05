#!/bin/bash
# Navegar al directorio donde reside este script
cd "$(dirname "$0")"

echo "=================================================="
echo "    Iniciando actualización de Alienta Rojinegro  "
echo "=================================================="
echo ""

# Ejecutar el script procesador de catálogo e imágenes
python3 scripts/actualizar.py

if [ $? -eq 0 ]; then
    echo "🌐 Abriendo la web localmente para tu revisión..."
    open index.html
    echo ""
    echo "Presiona cualquier tecla para cerrar esta ventana..."
    read -n 1 -s
else
    echo ""
    echo "❌ Ocurrieron errores durante la validación."
    echo "Revisa los mensajes anteriores para corregir los archivos."
    echo ""
    echo "Presiona cualquier tecla para salir..."
    read -n 1 -s
fi
