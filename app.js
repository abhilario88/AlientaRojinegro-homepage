/**
 * ALIENTA ROJINEGRO — APLICACIÓN PRINCIPAL
 * Lógica en Vanilla JS: renderizado de catálogo, carruseles de alto rendimiento,
 * carga diferida y WhatsApp.
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

  // 2. Aplicar configuraciones globales (WhatsApp, textos, redes sociales)
  applyConfiguration(catalogo.config || {});

  // 3. Renderizar catálogo de productos con carga ultrarrápida
  renderProducts(catalogo.productos || [], catalogo.config || {});
}

/**
 * Normaliza y construye URLs seguras para redes sociales
 */
function resolveSocialUrl(network, rawValue) {
  if (!rawValue) return null;
  const val = rawValue.trim();
  if (!val) return null;

  // Si ya es una URL completa válida
  if (val.startsWith('http://') || val.startsWith('https://')) {
    return val;
  }

  // Si es un nombre de usuario en Instagram o TikTok
  if (network === 'instagram') {
    const cleanUser = val.replace(/^@/, '');
    return `https://instagram.com/${cleanUser}`;
  }

  if (network === 'tiktok') {
    const cleanUser = val.replace(/^@/, '');
    return `https://tiktok.com/@${cleanUser}`;
  }

  // Para Facebook, no inventar URL basándose solo en nombre si no es enlace
  if (network === 'facebook') {
    return null;
  }

  return null;
}

/**
 * Aplica los textos y enlaces globales definidos en configuracion.csv
 */
function applyConfiguration(config) {
  const whatsapp = (config.whatsapp || '51967031999').replace(/[^\d]/g, '');

  // Textos Hero
  const heroTitle = document.getElementById('hero-title');
  if (heroTitle && config.tituloHero) {
    heroTitle.textContent = config.tituloHero;
  }

  const heroSubtitle = document.getElementById('hero-subtitle');
  if (heroSubtitle && config.textoHero) {
    heroSubtitle.textContent = config.textoHero;
  }

  // CTA Hero con una sola flecha limpia
  const heroCtaBtn = document.getElementById('hero-cta-btn');
  if (heroCtaBtn) {
    let ctaText = (config.ctaHero || 'VER PRODUCTOS →').trim();
    if (!ctaText.includes('→') && !ctaText.includes('->')) {
      ctaText += ' →';
    }
    heroCtaBtn.textContent = ctaText;
  }

  // Mensaje general acordado para el Header y el CTA Final
  const generalMsg = encodeURIComponent('Hola, vengo de la página de Alienta Rojinegro y quisiera información sobre sus productos.');

  // Enlace WhatsApp del Header
  const headerWaBtn = document.getElementById('header-whatsapp-btn');
  if (headerWaBtn) {
    headerWaBtn.href = `https://wa.me/${whatsapp}?text=${generalMsg}`;
  }

  // Enlace WhatsApp de la Sección Final
  const finalWaBtn = document.getElementById('final-whatsapp-btn');
  if (finalWaBtn) {
    finalWaBtn.href = `https://wa.me/${whatsapp}?text=${generalMsg}`;
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
 * Renderiza los iconos de redes sociales en el footer
 */
function renderSocialLinks(config) {
  const container = document.getElementById('footer-social');
  if (!container) return;

  container.innerHTML = '';

  const redes = [
    {
      key: 'tiktok',
      name: 'TikTok',
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"></path></svg>`
    },
    {
      key: 'instagram',
      name: 'Instagram',
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>`
    },
    {
      key: 'facebook',
      name: 'Facebook',
      icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"></path></svg>`
    }
  ];

  redes.forEach(red => {
    const resolvedUrl = resolveSocialUrl(red.key, config[red.key]);
    if (resolvedUrl) {
      const a = document.createElement('a');
      a.href = resolvedUrl;
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
 * Carga de forma segura imágenes secundarias de un carrusel
 */
function loadCardDeferredImages(card) {
  const deferredImgs = card.querySelectorAll('img[data-src]');
  deferredImgs.forEach(img => {
    const realSrc = img.getAttribute('data-src');
    if (realSrc) {
      img.src = realSrc;
      img.removeAttribute('data-src');
    }
  });
}

/**
 * Renderiza las tarjetas de productos optimizadas
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
  const whatsapp = (config.whatsapp || '51967031999').replace(/[^\d]/g, '');

  productos.forEach((producto, index) => {
    const card = document.createElement('article');
    card.className = 'product-card';

    // Numeración editorial (01, 02, 03...)
    const numEditorial = String(index + 1).padStart(2, '0');

    // Enlace directo a WhatsApp con mensaje de compra
    const waText = encodeURIComponent(`Hola, quiero comprar ${producto.nombre}.`);
    const waUrl = `https://wa.me/${whatsapp}?text=${waText}`;

    // Construcción del contenedor visual
    const imagenes = producto.imagenes || [];
    const totalImgs = imagenes.length;

    let mediaHTML = '';

    if (totalImgs <= 1) {
      const imgSrc = imagenes[0] || 'assets/optimized/hero/HERO.jpg';
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
      // Optimización de carrusel:
      // La foto 0 carga de inmediato. Las fotos 1..N tienen carga diferida instantánea al interactuar.
      const slidesHTML = imagenes.map((img, i) => {
        if (i === 0) {
          return `
            <div class="carousel-slide">
              <img 
                src="${img}" 
                alt="${producto.nombre}" 
                class="card-img" 
                loading="${index < 3 ? 'eager' : 'lazy'}" 
                decoding="async"
              >
            </div>
          `;
        } else {
          return `
            <div class="carousel-slide">
              <img 
                data-src="${img}" 
                src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E"
                alt="${producto.nombre}" 
                class="card-img" 
                loading="lazy" 
                decoding="async"
              >
            </div>
          `;
        }
      }).join('');

      const dotsHTML = imagenes.map((_, i) => `
        <span class="dot ${i === 0 ? 'active' : ''}" data-index="${i}"></span>
      `).join('');

      mediaHTML = `
        <div class="card-media carousel-container" data-product-id="${producto.id}">
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

    // Contenido textual con numeración editorial discreta
    card.innerHTML = `
      ${mediaHTML}
      <div class="card-content">
        <div class="card-meta-top">
          <span class="product-number">${numEditorial}</span>
        </div>
        <div class="card-header-row">
          <h3 class="product-name">${producto.nombre}</h3>
          <span class="product-price">S/ ${producto.precio}</span>
        </div>
        <p class="product-desc">${producto.descripcion || ''}</p>
        <a href="${waUrl}" class="btn-buy" target="_blank" rel="noopener noreferrer" aria-label="Comprar ${producto.nombre} por WhatsApp">
          <span>COMPRAR</span>
          <span class="btn-arrow">→</span>
        </a>
      </div>
    `;

    // Cargar imágenes secundarias al posar el cursor o tocar la tarjeta
    card.addEventListener('mouseenter', () => loadCardDeferredImages(card), { once: true });
    card.addEventListener('touchstart', () => loadCardDeferredImages(card), { once: true, passive: true });

    grid.appendChild(card);
  });

  // Inicializar eventos de carrusel
  initCarousels();

  // Inicializar scroll reveal en tarjetas
  initProductScrollReveal();

  // Precargar suavemente el resto de fotos en segundo plano tras 1.8 segundos
  window.setTimeout(() => {
    document.querySelectorAll('.product-card').forEach(loadCardDeferredImages);
  }, 1800);
}

/**
 * Inicializa los eventos de swipe, scroll y flechas para todos los carruseles
 */
function initCarousels() {
  const containers = document.querySelectorAll('.carousel-container');

  containers.forEach(container => {
    const card = container.closest('.product-card');
    const track = container.querySelector('.carousel-track');
    const prevBtn = container.querySelector('.carousel-nav-btn.prev');
    const nextBtn = container.querySelector('.carousel-nav-btn.next');
    const dots = container.querySelectorAll('.dot');
    const slides = container.querySelectorAll('.carousel-slide');

    if (!track || slides.length <= 1) return;

    // Actualizar indicador activo en base al desplazamiento suave
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
      }, 40);
    }, { passive: true });

    // Navegación con flecha siguiente (Desktop)
    if (nextBtn) {
      nextBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (card) loadCardDeferredImages(card);
        const slideWidth = track.clientWidth;
        track.scrollBy({ left: slideWidth, behavior: 'smooth' });
      });
    }

    // Navegación con flecha anterior (Desktop)
    if (prevBtn) {
      prevBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (card) loadCardDeferredImages(card);
        const slideWidth = track.clientWidth;
        track.scrollBy({ left: -slideWidth, behavior: 'smooth' });
      });
    }
  });
}

/**
 * Microinteracción: Revela suavemente las tarjetas de productos al entrar en viewport
 */
function initProductScrollReveal() {
  const cards = document.querySelectorAll('.product-card');

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
    cards.forEach(card => card.classList.add('is-visible'));
    return;
  }

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    });
  }, {
    root: null,
    threshold: 0.1,
    rootMargin: '0px 0px -30px 0px'
  });

  cards.forEach(card => observer.observe(card));
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
