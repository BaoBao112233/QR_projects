// Logo / brand-asset URLs that appear on every page and should be hidden from product galleries
const LOGO_BLOCKLIST = [
  '1a7a3fc45bf15',
  '81cc7e1db6a23',
  'default_profile',
  'kakao',
  'npay_logo',
  'vendor-cdn.imweb.me',
  '/thumbnail/20240226/',  // brand badge "L" logos
];
function isLogo(url) {
  if (!url) return true;
  return LOGO_BLOCKLIST.some(p => url.includes(p));
}

// Approximate FX rates (KRW -> target). Update if needed.
const FX = {
  USD: 1 / 1360,   // 1 USD ≈ 1,360 KRW
  CNY: 1 / 188,    // 1 CNY ≈ 188 KRW
};

function parseKRW(priceStr) {
  if (!priceStr) return null;
  const m = String(priceStr).replace(/[^\d]/g, '');
  return m ? parseInt(m, 10) : null;
}

function formatRange(value, code) {
  // Build a ±~1.5% band, rounded to whole units, displayed as "low–high CODE"
  const low = Math.floor(value * 0.985);
  const high = Math.ceil(value * 1.015);
  const fmt = n => n.toLocaleString('en-US');
  return `${fmt(low)}–${fmt(high)} ${code}`;
}

function priceWithApprox(p) {
  const loc = LUBY.getLocale() || LUBY.DEFAULT_LOCALE;
  const krw = parseKRW(p.price);
  if (!krw || loc === 'kr') return p.price;
  if (loc === 'en') {
    return `${p.price} <span class="price-approx">≈ ${formatRange(krw * FX.USD, 'USD')}</span>`;
  }
  if (loc === 'zh') {
    return `${p.price} <span class="price-approx">≈ ${formatRange(krw * FX.CNY, 'CNY')}</span>`;
  }
  return p.price;
}

// Product page renderer — expects window.PRODUCT to be set with the product object
async function init() {
  const data = window.PRODUCT;
  if (!data) return;

  await LUBY.ensureLocale();
  render(data);
}

function render(p) {
  document.title = `${LUBY.tr(p.name)} — LUBYLAB`;

  // Topbar
  const topbar = document.querySelector('.topbar');
  topbar.innerHTML = `
    <a href="../index.html" class="brand">LUBYLAB</a>
    <div class="lang-switch-wrap"></div>
  `;
  LUBY.renderLangSwitch(topbar.querySelector('.lang-switch-wrap'), () => {
    render(p);
  });

  // Build hero
  const main = document.querySelector('.product-main');
  const status = p.status ? LUBY.tr(p.status) : '';
  const isSoldOut = /sold ?out|품절|售罄/i.test(status);
  const benefits = (p.key_benefits || []).map(b => `<li>${LUBY.tr(b)}</li>`).join('');
  const ingredients = (p.main_ingredients || []).map(i => `<li>${LUBY.tr(i)}</li>`).join('');

  const description = p.description ? `<div class="description">${LUBY.tr(p.description)}</div>` : '';
  const feature = p.main_feature || p.key_feature;

  const gallery = [p.images.main, ...(p.images.gallery || [])]
    .filter(Boolean)
    .filter(u => !isLogo(u));
  const thumbs = gallery.slice(0, 10);

  main.innerHTML = `
    <section class="hero">
      <div class="gallery">
        <div class="gallery-main">
          <img id="hero-img" src="${gallery[0]}" alt="${LUBY.tr(p.name)}" />
        </div>
        <div class="gallery-thumbs">
          ${thumbs.map((u, i) => `
            <button data-idx="${i}" data-src="${u}" ${i === 0 ? 'class="active"' : ''}>
              <img src="${u}" alt="" loading="lazy" />
            </button>
          `).join('')}
        </div>
      </div>

      <div class="info">
        ${status && !isSoldOut ? `<span class="badge">${status}</span>` : ''}
        ${isSoldOut ? `<span class="badge" style="background:#999">${LUBY.t('soldOut')}</span>` : ''}
        <h1>${LUBY.tr(p.name)}</h1>
        <div class="subtitle">${p.key}</div>
        ${description}
        <div class="price">
          ${priceWithApprox(p)}
          ${p.loyalty_points ? `<span class="points">+ ${p.loyalty_points}</span>` : ''}
        </div>
        <button class="cta ${isSoldOut ? 'disabled' : ''}" ${isSoldOut ? 'disabled' : ''}>
          ${isSoldOut ? LUBY.t('soldOut') : LUBY.t('cta')}
        </button>
        <div class="spec-list">
          ${feature ? `
            <div class="spec-row">
              <div class="spec-key">${LUBY.t('feature')}</div>
              <div class="spec-val">${LUBY.tr(feature)}</div>
            </div>` : ''}
          ${p.category ? `
            <div class="spec-row">
              <div class="spec-key">${LUBY.t('category')}</div>
              <div class="spec-val">${LUBY.tr(p.category)}</div>
            </div>` : ''}
          ${benefits ? `
            <div class="spec-row">
              <div class="spec-key">${LUBY.t('benefits')}</div>
              <div class="spec-val"><ul>${benefits}</ul></div>
            </div>` : ''}
          ${ingredients ? `
            <div class="spec-row">
              <div class="spec-key">${LUBY.t('ingredients')}</div>
              <div class="spec-val"><ul>${ingredients}</ul></div>
            </div>` : ''}
          ${p.exclusive ? `
            <div class="spec-row">
              <div class="spec-key">${LUBY.t('exclusive')}</div>
              <div class="spec-val">${LUBY.tr(p.exclusive)}</div>
            </div>` : ''}
          ${p.shipping ? `
            <div class="spec-row">
              <div class="spec-key">${LUBY.t('shipping')}</div>
              <div class="spec-val">${LUBY.tr(p.shipping)}</div>
            </div>` : ''}
          ${p.delivery_note ? `
            <div class="spec-row">
              <div class="spec-key">${LUBY.t('delivery')}</div>
              <div class="spec-val">${LUBY.tr(p.delivery_note)}</div>
            </div>` : ''}
        </div>
      </div>
    </section>

    ${(p.images.detail_banners || []).length ? `
      <section class="detail-section">
        <h2>${LUBY.t('detailHeading')}</h2>
        <div class="detail-banners" id="detail-banners">
          ${p.images.detail_banners.slice(0, 8).map(u => `<img src="${u}" loading="lazy" alt="">`).join('')}
        </div>
        ${p.images.detail_banners.length > 8 ? `
          <button class="show-more" id="show-more-btn">${LUBY.t('showMore')}</button>` : ''}
      </section>
    ` : ''}
  `;

  // Wire up gallery thumbs
  const heroImg = document.getElementById('hero-img');
  document.querySelectorAll('.gallery-thumbs button').forEach(btn => {
    btn.addEventListener('click', () => {
      heroImg.src = btn.dataset.src;
      document.querySelectorAll('.gallery-thumbs button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // Show more banners
  const showMoreBtn = document.getElementById('show-more-btn');
  if (showMoreBtn) {
    let expanded = false;
    showMoreBtn.addEventListener('click', () => {
      const container = document.getElementById('detail-banners');
      if (!expanded) {
        const rest = p.images.detail_banners.slice(8);
        container.insertAdjacentHTML('beforeend',
          rest.map(u => `<img src="${u}" loading="lazy" alt="">`).join(''));
        showMoreBtn.textContent = LUBY.t('showLess');
        expanded = true;
      } else {
        const imgs = container.querySelectorAll('img');
        for (let i = imgs.length - 1; i >= 8; i--) imgs[i].remove();
        showMoreBtn.textContent = LUBY.t('showMore');
        expanded = false;
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', init);
