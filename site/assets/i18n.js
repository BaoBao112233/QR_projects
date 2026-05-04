// Locale dictionary + helpers
const LOCALE_KEY = 'lubylab_locale';
const SUPPORTED = ['en', 'kr', 'zh'];
const DEFAULT_LOCALE = 'en';

const T = {
  en: {
    pickerTitle: 'Choose your language',
    pickerSub: 'Select a language to view product information',
    langEn: 'English',
    langKr: '한국어',
    langZh: '中文',
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
  kr: {
    pickerTitle: '언어를 선택하세요',
    pickerSub: '제품 정보를 확인할 언어를 선택해주세요',
    langEn: 'English',
    langKr: '한국어',
    langZh: '中文',
    brandTagline: '프리미엄 K-뷰티',
    indexTitle: '루비랩 제품',
    indexSub: '대표 컬렉션을 만나보세요',
    backToProducts: '← 전체 제품',
    price: '가격',
    points: '포인트 적립예정',
    status: '상태',
    category: '카테고리',
    benefits: '핵심 효능',
    ingredients: '주요 성분',
    feature: '특징',
    description: '제품 설명',
    shipping: '배송',
    delivery: '배송 안내',
    exclusive: '독점 판매',
    detailHeading: '상품 상세 정보',
    showMore: '더보기',
    showLess: '접기',
    cta: '구매하기',
    soldOut: '품절',
    changeLanguage: '언어',
  },
  zh: {
    pickerTitle: '请选择您的语言',
    pickerSub: '选择语言以查看产品信息',
    langEn: 'English',
    langKr: '한국어',
    langZh: '中文',
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
  }
};

function getLocale() {
  const v = localStorage.getItem(LOCALE_KEY);
  return SUPPORTED.includes(v) ? v : null;
}

function setLocale(loc) {
  if (!SUPPORTED.includes(loc)) loc = DEFAULT_LOCALE;
  localStorage.setItem(LOCALE_KEY, loc);
  document.documentElement.lang = loc === 'kr' ? 'ko' : (loc === 'zh' ? 'zh-CN' : 'en');
}

function t(key) {
  const loc = getLocale() || DEFAULT_LOCALE;
  return (T[loc] && T[loc][key]) || T[DEFAULT_LOCALE][key] || key;
}

// Translate field of shape {kr, en, zh} or array thereof
function tr(field) {
  if (field == null) return '';
  const loc = getLocale() || DEFAULT_LOCALE;
  if (typeof field === 'string') return field;
  if (Array.isArray(field)) {
    return field.map(tr);
  }
  if (typeof field === 'object') {
    return field[loc] || field.en || field.kr || field.zh || '';
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
          <button class="lang-btn" data-loc="kr">
            <span class="lang-flag">🇰🇷</span>
            <span class="lang-name">한국어 (Korean)</span>
          </button>
          <button class="lang-btn" data-loc="zh">
            <span class="lang-flag">🇨🇳</span>
            <span class="lang-name">中文 (Chinese)</span>
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
      <button data-loc="kr" ${cur === 'kr' ? 'class="active"' : ''}>KR</button>
      <button data-loc="zh" ${cur === 'zh' ? 'class="active"' : ''}>中</button>
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
