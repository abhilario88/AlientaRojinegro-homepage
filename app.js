/**
 * ALIENTA ROJINEGRO — APLICACIÓN PRINCIPAL
 * Lógica pura en Vanilla JS: renderizado de catálogo, carruseles y WhatsApp.
 * Sin dependencias externas ni frameworks.
 */

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  let catalogo = null;

  // 1. Cargar datos desde window.CATALOGO_DATA (inyectado por datos/catalogo.js)
  if (window.CATALOGO_DATA && window.CATALOGO_DATA.productos) {
    catalogo = window.CATALOGO_DATA;
  } else {
    // Fallback: Si no está cargado globalmente, intentar fetch del JSON
    try {
      const response = await fetch('datos/catalogo.json');
      if (response.ok) {
        catalogo = await response.json();
      }
    } catch (err) {
      console.warn('No se pudo cargar catalogo.json mediante fetch:', err);
    }
  }

  if (!catalogo) {
    showErrorState('No se pudieron cargar los productos. Ejecuta Actualizar.command para compilar el catálogo.');
    return;
  }

  // 2. Aplicar configuraciones globales
  applyConfiguration(catalogo.config || {});

  // 3. Renderizar catálogo de productos
  renderProducts(catalogo.productos || [], catalogo.config || {});
}

/**
 * Aplica los textos y enlaces globales definidos en configuracion.csv
 */
function applyConfiguration(config) {
  const whatsapp = config.whatsapp || '51959740166';

  // Textos Hero
  const heroTitle = document.getElementById('hero-title');
  if (heroTitle && config.tituloHero) {
    heroTitle.textContent = config.tituloHero;
  }

  const heroSubtitle = document.getElementById('hero-subtitle');
  if (heroSubtitle && config.textoHero) {
    heroSubtitle.textContent = config.textoHero;
  }

  const heroCtaText = document.getElementById('hero-cta-text');
  if (heroCtaText && config.ctaHero) {
    heroCtaText.textContent = config.ctaHero;
  }

  // Enlace WhatsApp del Header
  const headerWaBtn = document.getElementById('header-whatsapp-btn');
  if (headerWaBtn) {
    const defaultMsg = encodeURIComponent('Hola, quiero información sobre los productos de Alienta Rojinegro.');
    headerWaBtn.href = `https://wa.me/${whatsapp}?text=${defaultMsg}`;
  }

  // Copyright dinámico
  const footerCopy = document.getElementById('footer-copy');
  if (footerCopy) {
    const currentYear = new Date().getFullYear();
    footerCopy.textContent = `© ${currentYear} Alienta Rojinegro. Todos los derechos reservados.`;
  }

  // Redes Sociales en Footer
  renderSocialLinks(config);
}

/**
 * Renderiza los iconos de redes sociales únicamente si tienen URL configurada
 */
function renderSocialLinks(config) {
  const container = document.getElementById('footer-social');
  if (!container) return;

  container.innerHTML = '';

  const redes = [
    {
      key: 'instagram',
      name: 'Instagram',
      icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>`
    },
    {
      key: 'facebook',
      name: 'Facebook',
      icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>`
    },
    {
      key: 'tiktok',
      name: 'TikTok',
      icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"></path></svg>`
    }
  ];

  redes.forEach(red => {
    const url = config[red.key];
    if (url && url.trim() !== '') {
      const a = document.createElement('a');
      a.href = url.trim();
      a.className = 'social-link';
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.setAttribute('aria-label', `Visitar ${red.name} de Alienta Rojinegro`);
      a.innerHTML = red.icon;
      container.appendChild(a);
    }
  });
}

/**
 * Renderiza las tarjetas de productos en la cuadrícula
 */
function renderProducts(productos, config) {
  const grid = document.getElementById('products-grid');
  if (!grid) return;

  if (productos.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <p>No hay productos activos en este momento.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = '';
  const whatsapp = config.whatsapp || '51959740166';

  productos.forEach((producto, index) => {
    const card = document.createElement('article');
    card.className = 'product-card';

    // Generar enlace directo a WhatsApp con mensaje personalizado
    const waText = encodeURIComponent(`Hola, quiero comprar ${producto.nombre}.`);
    const waUrl = `https://wa.me/${whatsapp}?text=${waText}`;

    // Construcción del contenedor de medios (imagen o carrusel)
    const imagenes = producto.imagenes || [];
    const totalImgs = imagenes.length;

    let mediaHTML = '';

    if (totalImgs <= 1) {
      const imgSrc = imagenes[0] || 'Imagenes/hero/HERO.png';
      mediaHTML = `
        <div class="card-media">
          <img 
            src="${imgSrc}" 
            alt="${producto.nombre}" 
            class="card-img" 
            loading="${index < 3 ? 'eager' : 'lazy'}"
            decoding="async"
          >
        </div>
      `;
    } else {
      // Carrusel interactivo automático para productos con múltiples fotos
      const slidesHTML = imagenes.map(img => `
        <div class="carousel-slide">
          <img 
            src="${img}" 
            alt="${producto.nombre}" 
            class="card-img" 
            loading="lazy" 
            decoding="async"
          >
        </div>
      `).join('');

      const dotsHTML = imagenes.map((_, i) => `
        <span class="dot ${i === 0 ? 'active' : ''}" data-index="${i}"></span>
      `).join('');

      mediaHTML = `
        <div class="card-media carousel-container" data-product-id="${producto.id}">
          <span class="badge-multiphoto">${totalImgs} FOTOS</span>
          <button class="carousel-nav-btn prev" aria-label="Foto anterior" type="button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>
          </button>
          <div class="carousel-track">
            ${slidesHTML}
          </div>
          <button class="carousel-nav-btn next" aria-label="Siguiente foto" type="button">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
          <div class="carousel-dots">
            ${dotsHTML}
          </div>
        </div>
      `;
    }

    // Contenido textual y botón de compra
    card.innerHTML = `
      ${mediaHTML}
      <div class="card-content">
        <div class="card-header-row">
          <h3 class="product-name">${producto.nombre}</h3>
          <span class="product-price">S/ ${producto.precio}</span>
        </div>
        <p class="product-desc">${producto.descripcion || ''}</p>
        <a href="${waUrl}" class="btn-buy" target="_blank" rel="noopener noreferrer" aria-label="Comprar ${producto.nombre} por WhatsApp">
          <span>COMPRAR</span>
          <svg class="icon-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </a>
      </div>
    `;

    grid.appendChild(card);
  });

  // Inicializar eventos de carrusel después de agregar elementos al DOM
  initCarousels();
}

/**
 * Inicializa los eventos de swipe, scroll y botones para todos los carruseles
 */
function initCarousels() {
  const containers = document.querySelectorAll('.carousel-container');

  containers.forEach(container => {
    const track = container.querySelector('.carousel-track');
    const prevBtn = container.querySelector('.carousel-nav-btn.prev');
    const nextBtn = container.querySelector('.carousel-nav-btn.next');
    const dots = container.querySelectorAll('.dot');
    const slides = container.querySelectorAll('.carousel-slide');

    if (!track || slides.length <= 1) return;

    // Actualizar indicador activo en base al desplazamiento
    let isScrolling = null;
    track.addEventListener('scroll', () => {
      window.clearTimeout(isScrolling);
      isScrolling = setTimeout(() => {
        const slideWidth = track.clientWidth;
        if (slideWidth <= 0) return;
        const activeIndex = Math.round(track.scrollLeft / slideWidth);
        
        dots.forEach((dot, idx) => {
          if (idx === activeIndex) {
            dot.classList.add('active');
          } else {
            dot.classList.remove('active');
          }
        });
      }, 50);
    }, { passive: true });

    // Navegación con botón siguiente
    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const slideWidth = track.clientWidth;
        track.scrollBy({ left: slideWidth, behavior: 'smooth' });
      });
    }

    // Navegación con botón anterior
    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const slideWidth = track.clientWidth;
        track.scrollBy({ left: -slideWidth, behavior: 'smooth' });
      });
    }
  });
}

/**
 * Muestra mensaje de error amigable en la cuadrícula si falla la carga
 */
function showErrorState(mensaje) {
  const grid = document.getElementById('products-grid');
  if (grid) {
    grid.innerHTML = `
      <div class="empty-state">
        <p style="color: #A6192E; font-weight: 700; margin-bottom: 0.5rem;">Aviso de catálogo</p>
        <p>${mensaje}</p>
      </div>
    `;
  }
}
