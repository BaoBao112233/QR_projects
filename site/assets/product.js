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
    <a href="../index.html" class="brand">
      <img src="../assets/logo.png" alt="LUBYLAB" class="brand-logo">
    </a>
    <div class="lang-switch-wrap"></div>
  `;
  LUBY.renderLangSwitch(topbar.querySelector('.lang-switch-wrap'), () => {
    render(p);
  });

  const main = document.querySelector('.product-main');
  const heroImg = (p.images && p.images.main) || '';

  const detailBanners = (p.images && p.images.detail_banners) || [];

  main.innerHTML = `
    <section class="hero">
      <div class="gallery">
        <div class="gallery-main">
          <img src="${heroImg}" alt="${LUBY.tr(p.name)}" />
        </div>
      </div>

      <div class="info">
        <span class="badge badge-pharmacy">HERE @ READY YOUNG PHARMACY</span>
        <h1>${LUBY.tr(p.name)}</h1>
        <div class="subtitle">${p.key}</div>
      </div>
    </section>

    ${detailBanners.length ? `
      <section class="detail-section">
        <h2>${LUBY.t('detailHeading')}</h2>
        <div class="detail-banners" id="detail-banners">
          ${detailBanners.slice(0, 8).map(u => `<img src="${u}" loading="lazy" alt="">`).join('')}
        </div>
        ${detailBanners.length > 8 ? `
          <button class="show-more" id="show-more-btn">${LUBY.t('showMore')}</button>` : ''}
      </section>
    ` : ''}
  `;

  const showMoreBtn = document.getElementById('show-more-btn');
  if (showMoreBtn) {
    let expanded = false;
    showMoreBtn.addEventListener('click', () => {
      const container = document.getElementById('detail-banners');
      if (!expanded) {
        const rest = detailBanners.slice(8);
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
