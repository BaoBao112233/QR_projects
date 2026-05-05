// Locale dictionary + helpers
const LOCALE_KEY = 'lubylab_locale';
const SUPPORTED = ['en', 'zh', 'ja'];
const DEFAULT_LOCALE = 'en';

const T = {
  en: {
    pickerTitle: 'Choose your language',
    pickerSub: 'Select a language to view product information',
    langEn: 'English',
    langZh: '中文',
    langJa: '日本語',
    brandTagline: 'Premium K-Beauty',
    indexTitle: 'LUBYLAB Products',
    indexSub: 'Discover our hero collection',
    backToProducts: '← All products',
    price: 'Price',
    points: 'points to earn',
    status: 'Status',
    category: 'Category',
    benefits: 'Key Benefits',
    ingredients: 'Main Ingredients',
    feature: 'Feature',
    description: 'Description',
    shipping: 'Shipping',
    delivery: 'Delivery',
    exclusive: 'Exclusive Distribution',
    detailHeading: 'PRODUCT DETAIL',
    showMore: 'SHOW MORE',
    showLess: 'SHOW LESS',
    cta: 'BUY NOW',
    soldOut: 'SOLD OUT',
    changeLanguage: 'Language',
  },
  zh: {
    pickerTitle: '请选择您的语言',
    pickerSub: '选择语言以查看产品信息',
    langEn: 'English',
    langZh: '中文',
    langJa: '日本語',
    brandTagline: '高端韩国美妆',
    indexTitle: 'LUBYLAB 产品',
    indexSub: '探索我们的明星系列',
    backToProducts: '← 全部产品',
    price: '价格',
    points: '积分',
    status: '状态',
    category: '类别',
    benefits: '主要功效',
    ingredients: '主要成分',
    feature: '产品特点',
    description: '产品描述',
    shipping: '配送',
    delivery: '配送说明',
    exclusive: '独家销售',
    detailHeading: '产品详情',
    showMore: '查看更多',
    showLess: '收起',
    cta: '立即购买',
    soldOut: '已售罄',
    changeLanguage: '语言',
  },
  ja: {
    pickerTitle: '言語を選択してください',
    pickerSub: '商品情報を表示する言語を選択してください',
    langEn: 'English',
    langZh: '中文',
    langJa: '日本語',
    brandTagline: 'プレミアム K-ビューティー',
    indexTitle: 'LUBYLAB 製品',
    indexSub: '代表的なコレクションをご覧ください',
    backToProducts: '← 全製品',
    price: '価格',
    points: 'ポイント',
    status: 'ステータス',
    category: 'カテゴリー',
    benefits: '主な効果',
    ingredients: '主成分',
    feature: '特徴',
    description: '製品説明',
    shipping: '配送',
    delivery: '配送案内',
    exclusive: '独占販売',
    detailHeading: '製品詳細',
    showMore: 'もっと見る',
    showLess: '閉じる',
    cta: '今すぐ購入',
    soldOut: '売り切れ',
    changeLanguage: '言語',
  }
};

// In-memory locale only — cleared on every page load so the picker shows again.
let CURRENT_LOCALE = null;

function getLocale() {
  return SUPPORTED.includes(CURRENT_LOCALE) ? CURRENT_LOCALE : null;
}

function setLocale(loc) {
  if (!SUPPORTED.includes(loc)) loc = DEFAULT_LOCALE;
  CURRENT_LOCALE = loc;
  document.documentElement.lang = loc === 'zh' ? 'zh-CN' : (loc === 'ja' ? 'ja' : 'en');
}

function t(key) {
  const loc = getLocale() || DEFAULT_LOCALE;
  return (T[loc] && T[loc][key]) || T[DEFAULT_LOCALE][key] || key;
}

// Translate field of shape {en, zh, ja} or array thereof
function tr(field) {
  if (field == null) return '';
  const loc = getLocale() || DEFAULT_LOCALE;
  if (typeof field === 'string') return field;
  if (Array.isArray(field)) {
    return field.map(tr);
  }
  if (typeof field === 'object') {
    return field[loc] || field.en || field.zh || field.ja || '';
  }
  return String(field);
}

// Render the language picker if no locale selected. Returns Promise that resolves once chosen.
function ensureLocale() {
  return new Promise(resolve => {
    if (getLocale()) return resolve(getLocale());

    const overlay = document.createElement('div');
    overlay.className = 'lang-overlay';
    overlay.innerHTML = `
      <div class="lang-modal" role="dialog" aria-modal="true">
        <h2 data-tk="pickerTitle">Choose your language</h2>
        <p data-tk="pickerSub">Select a language to view product information</p>
        <div class="lang-options">
          <button class="lang-btn default-tag" data-loc="en">
            <span class="lang-flag">🇺🇸</span>
            <span class="lang-name">English</span>
          </button>
          <button class="lang-btn" data-loc="zh">
            <span class="lang-flag">🇨🇳</span>
            <span class="lang-name">中文 (Chinese)</span>
          </button>
          <button class="lang-btn" data-loc="ja">
            <span class="lang-flag">🇯🇵</span>
            <span class="lang-name">日本語 (Japanese)</span>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);
    overlay.addEventListener('click', (e) => {
      const btn = e.target.closest('.lang-btn');
      if (!btn) return;
      const loc = btn.dataset.loc;
      setLocale(loc);
      overlay.remove();
      resolve(loc);
    });
  });
}

// Render top-bar language switcher
function renderLangSwitch(container, onChange) {
  const cur = getLocale() || DEFAULT_LOCALE;
  container.innerHTML = `
    <div class="lang-switch" role="tablist">
      <button data-loc="en" ${cur === 'en' ? 'class="active"' : ''}>EN</button>
      <button data-loc="zh" ${cur === 'zh' ? 'class="active"' : ''}>中</button>
      <button data-loc="ja" ${cur === 'ja' ? 'class="active"' : ''}>日</button>
    </div>
  `;
  container.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-loc]');
    if (!btn) return;
    setLocale(btn.dataset.loc);
    onChange && onChange(btn.dataset.loc);
  });
}

window.LUBY = { t, tr, getLocale, setLocale, ensureLocale, renderLangSwitch, SUPPORTED, DEFAULT_LOCALE };
