# Alienta Rojinegro — Manual de Mantenimiento

Guía rápida para actualizar, administrar y publicar la web de forma 100% autónoma.

---

## 1. Cómo agregar un producto nuevo

1. Crea una carpeta para tu producto dentro de `Imagenes/productos/`.
   - *Ejemplo:* `Imagenes/productos/11. Taza Rojinegra`
2. Coloca las imágenes del producto dentro de esa nueva carpeta (`01.png`, `02.png`, etc.).
3. Abre `datos/productos.csv` con Excel o cualquier editor de texto y añade una nueva fila al final:
   ```csv
   10,Taza Rojinegra,35,11. Taza Rojinegra,Taza de cerámica rojinegra con logo grabado,sí
   ```
4. Haz doble clic en **`Actualizar.command`**.

---

## 2. Cómo cambiar un precio

1. Abre `datos/productos.csv`.
2. Ubica el producto y modifica el número en la columna `precio`.
   - *Ejemplo:* cambia `45` por `50`.
3. Guarda el archivo y haz doble clic en **`Actualizar.command`**.

---

## 3. Cómo cambiar una descripción

1. Abre `datos/productos.csv`.
2. Ubica la columna `descripcion` del producto deseado y escribe el nuevo texto.
3. Guarda el archivo y haz doble clic en **`Actualizar.command`**.

---

## 4. Cómo agregar o quitar una imagen

- **Para agregar una imagen:** Coloca la nueva imagen compatible (`.png`, `.jpg`, `.jpeg`, `.webp`) dentro de la carpeta del producto en `Imagenes/productos/`. No necesitas modificar el CSV.
- **Para quitar una imagen:** Simplemente elimina la imagen de la carpeta del producto.
- Tras hacer el cambio, haz doble clic en **`Actualizar.command`**.
  - *Nota:* Si el producto tiene 1 sola foto, se mostrará fija. Si tiene 2 o más, el carrusel interactivo se creará automáticamente.

---

## 5. Cómo ocultar un producto

1. Abre `datos/productos.csv`.
2. En la columna `activo` del producto que deseas ocultar, escribe `no`:
   ```csv
   5,Berni Cuesta Rojinegro,55,5. Berni Rojinegro,Figura homenaje al goleador e ídolo rojinegro,no
   ```
3. Guarda el archivo y haz doble clic en **`Actualizar.command`**. El producto ya no aparecerá en la web hasta que vuelvas a poner `sí`.

---

## 6. Cómo cambiar el número de WhatsApp

1. Abre `datos/configuracion.csv`.
2. En la fila `whatsapp`, cambia el valor numérico con tu código de país y número (sin espacios ni signos `+`):
   ```csv
   whatsapp,51959740166
   ```
3. Guarda el archivo y haz doble clic en **`Actualizar.command`**. Todos los botones de compra se actualizarán automáticamente.

---

## 7. Cómo cambiar redes sociales

1. Abre `datos/configuracion.csv`.
2. Modifica o pega los enlaces completos de tus redes sociales:
   ```csv
   instagram,https://instagram.com/alientarojinegro
   facebook,https://facebook.com/alientarojinegro
   tiktok,https://tiktok.com/@alientarojinegro
   ```
   - *Si dejas una red vacía (por ejemplo `facebook,`), ese icono no se mostrará en la web.*
3. Guarda el archivo y haz doble clic en **`Actualizar.command`**.

---

## 8. Cómo ejecutar `Actualizar.command`

1. En tu Mac (Finder), haz **doble clic** sobre el archivo **`Actualizar.command`**.
2. El programa validará tus archivos, optimizará las imágenes nuevas y compilará el catálogo.
3. Al finalizar con éxito, se abrirá la web en tu navegador para que revises cómo quedó.

---

## 9. Cómo ejecutar `Publicar.command`

1. Una vez que hayas verificado tus cambios en el navegador, haz **doble clic** sobre el archivo **`Publicar.command`**.
2. El script detectará los cambios, creará el guardado en Git y subirá todo a tu repositorio en la nube (`git push`).
3. En pocos minutos tu web estará publicada y actualizada en internet.
