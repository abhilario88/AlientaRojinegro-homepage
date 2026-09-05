#!/bin/bash
# Navegar al directorio donde reside este script
cd "$(dirname "$0")"

echo "=================================================="
echo "    Publicando cambios en Alienta Rojinegro        "
echo "=================================================="
echo ""

# Verificar si git está inicializado
if [ ! -d ".git" ]; then
    echo "⚠️ Repositorio Git no inicializado. Inicializando ahora..."
    git init
    git branch -M main
fi

# Agregar todos los cambios
git add .

# Verificar si hay cambios preparados para commit
if git diff --cached --quiet; then
    echo "✨ No hay cambios nuevos detectados en el catálogo ni en las imágenes."
    echo "Tu web ya está al día."
else
    FECHA=$(date '+%Y-%m-%d %H:%M')
    echo "📝 Guardando cambios con mensaje: 'Actualización catálogo $FECHA'..."
    git commit -m "Actualización catálogo $FECHA"

    # Verificar si existe un repositorio remoto configurado
    if git remote | grep -q 'origin'; then
        echo "🚀 Subiendo cambios al repositorio remoto (git push)..."
        BRANCH_ACTUAL=$(git rev-parse --abbrev-ref HEAD)
        git push -u origin "$BRANCH_ACTUAL"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 ¡Publicación exitosa! Los cambios estarán visibles en tu sitio en unos minutos."
        else
            echo ""
            echo "⚠️ Ocurrió un inconveniente al hacer git push."
            echo "Verifica tu conexión a Internet o los permisos de tu repositorio en GitHub/GitLab."
        fi
    else
        echo ""
        echo "ℹ️ Los cambios locales se guardaron correctamente en Git."
        echo "Para publicar automáticamente en la nube (Cloudflare Pages), configura tu repositorio remoto:"
        echo "  git remote add origin <URL_DE_TU_REPOSITORIO>"
        echo "  git push -u origin main"
    fi
fi

echo ""
echo "Presiona cualquier tecla para cerrar esta ventana..."
read -n 1 -s
