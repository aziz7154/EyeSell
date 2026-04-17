const API_BASE = 'http://127.0.0.1:5000';



const MOCK_UPLOAD = {
  image_id:  'mock_001',
  image_url: null,
};

const MOCK_ANALYSIS = {
  product_name:  'Nike Air Max 90',
  product_model: 'Size 10 · Used condition',
  confidence:    0.94,
  tags:          ['Nike', 'Air Max', 'sneakers', 'shoes', 'size 10'],
};

const MOCK_PRICING = {
  price_low:  45,
  price_high: 72,
  sources: [
    { name: 'eBay',                avg_price: 68, count: 6 },
    { name: 'Facebook Marketplace', avg_price: 52, count: 4 },
    { name: 'Poshmark',            avg_price: 71, count: 3 },
    { name: 'OfferUp',             avg_price: 45, count: 1 },
  ],
  listings: [
    { title: 'Nike Air Max 90', price: 68, source: 'eBay',     image_url: null },
    { title: 'Air Max 90',      price: 52, source: 'FB Mkt',   image_url: null },
    { title: 'Nike Sneakers',   price: 71, source: 'Poshmark', image_url: null },
    { title: 'Used Shoes',      price: 45, source: 'OfferUp',  image_url: null },
  ],
};

const MOCK_LISTINGS = {
  stats: { total_listings: 5, total_value: 669, total_searches: 12 },
  listings: [
    { id: 1, product_name: 'Nike Air Max 90',   price_final: 62,  created_at: '2026-04-10', status: 'saved' },
    { id: 2, product_name: 'Sony WH-1000XM4',   price_final: 140, created_at: '2026-04-08', status: 'saved' },
    { id: 3, product_name: 'iPad Air Gen 4',     price_final: 310, created_at: '2026-04-05', status: 'saved' },
    { id: 4, product_name: "Levi's 501 Jeans",   price_final: 35,  created_at: '2026-04-03', status: 'draft' },
    { id: 5, product_name: 'Canon EOS Rebel T7', price_final: 220, created_at: '2026-04-01', status: 'saved' },
  ],
};



window.EYESELL_USE_MOCK = true;


function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  });
}

function formatPrice(num) {
  return '$' + Math.round(num);
}

async function request(method, path, body = null, withCredentials = false) {
  const headers = { 'Content-Type': 'application/json' };
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);
  if (withCredentials) options.credentials = 'include';

  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }
  return res.json();
}


const Api = {

  async uploadImage(formData) {
    if (window.EYESELL_USE_MOCK) { await delay(600); return { ...MOCK_UPLOAD }; }
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });
    if (!res.ok) {
      const e = await res.json().catch(() => ({}));
      throw new Error(e.error || `Upload failed: ${res.status}`);
    }
    return res.json();
  },

  async analyzeImage(imageId, hint = '') {
    if (window.EYESELL_USE_MOCK) { await delay(800); return { ...MOCK_ANALYSIS }; }
    return request('POST', '/analyze', { image_id: imageId, hint }, true);
  },

  async searchPricing(productName) {
    if (window.EYESELL_USE_MOCK) { await delay(600); return { ...MOCK_PRICING }; }
    return request('POST', '/search', { product_name: productName }, true);
  },

  async createListing(data) {
    if (window.EYESELL_USE_MOCK) { await delay(400); return { id: Date.now(), status: 'saved' }; }
    return request('POST', '/listings', data, true);
  },

  async getListings() {
    if (window.EYESELL_USE_MOCK) { await delay(400); return { ...MOCK_LISTINGS }; }
    return request('GET', '/listings', null, true);
  },

  async deleteListing(id) {
    if (window.EYESELL_USE_MOCK) { await delay(300); return { success: true }; }
    return request('DELETE', `/listings/${id}`, null, true);
  },

  async login(username, password) {
    if (window.EYESELL_USE_MOCK) {
      await delay(500);
      if (username && password.length >= 1) {
        return { message: `Welcome back, ${username}!`, username };
      }
      throw new Error('Invalid username or password.');
    }
    return request('POST', '/login', { username, password }, true);
  },

  async register(username, email, password) {
    if (window.EYESELL_USE_MOCK) {
      await delay(500);
      return { message: 'Account created successfully', user_id: 1 };
    }
    return request('POST', '/register', { username, email, password });
  },

  async logout() {
    if (window.EYESELL_USE_MOCK) { await delay(200); Auth.clear(); return; }
    await request('POST', '/logout', null, true);
    Auth.clear();
  },

  async checkSession() {
    if (window.EYESELL_USE_MOCK) {
      const u = Auth.getUsername();
      return { loggedIn: !!u, username: u };
    }
    return request('GET', '/me', null, true);
  },

};



const Auth = {

  save(username) {
    sessionStorage.setItem('es_username', username);
  },

  getUsername() {
    return sessionStorage.getItem('es_username');
  },

  isLoggedIn() {
    return !!Auth.getUsername();
  },

  clear() {
    sessionStorage.removeItem('es_username');
    sessionStorage.removeItem('es_result');
  },

  logout() {
    Auth.clear();
    window.location.href = 'login.html';
  },

};


const Store = {
  saveResult(data)  { sessionStorage.setItem('es_result', JSON.stringify(data)); },
  getResult()       { const d = sessionStorage.getItem('es_result'); return d ? JSON.parse(d) : null; },
  clearResult()     { sessionStorage.removeItem('es_result'); },
};
