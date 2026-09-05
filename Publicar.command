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

BRANCH_ACTUAL=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

# Agregar todos los cambios
git add .

# Verificar si hay cambios locales preparados para commit
if ! git diff --cached --quiet; then
    FECHA=$(date '+%Y-%m-%d %H:%M')
    echo "📝 Guardando cambios con mensaje: 'Actualización catálogo $FECHA'..."
    git commit -m "Actualización catálogo $FECHA"
else
    echo "✨ Todos los archivos locales ya estaban guardados."
fi

# Sincronizar siempre con el repositorio remoto
if git remote | grep -q 'origin'; then
    echo "🚀 Sincronizando con GitHub (git push origin $BRANCH_ACTUAL)..."
    git push -u origin "$BRANCH_ACTUAL"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 ¡Publicación exitosa! Tu repositorio y tu web en Cloudflare están actualizados."
    else
        echo ""
        echo "⚠️ Ocurrió un inconveniente al hacer git push."
        echo "Verifica tu conexión a Internet o permisos de GitHub."
    fi
else
    echo ""
    echo "ℹ️ No se detectó un repositorio remoto configurado."
fi

echo ""
echo "Presiona cualquier tecla para cerrar esta ventana..."
read -n 1 -s
