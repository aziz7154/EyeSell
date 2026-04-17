document.addEventListener('DOMContentLoaded', () => {
  const username = Auth.getUsername();
  const userEl   = document.getElementById('navUsername');
  if (userEl && username) userEl.textContent = username;
  loadDashboard();
});


async function loadDashboard() {
  try {
    const data = await Api.getListings();
    renderStats(data.stats);
    renderListings(data.listings);
  } catch (err) {
    renderStats(null);
    renderError('Could not load listings. Please refresh the page.');
  }
}


function renderStats(stats) {
  document.getElementById('statListings').textContent =
    stats ? stats.total_listings : '—';
  document.getElementById('statValue').textContent =
    stats ? formatPrice(stats.total_value) : '—';
  document.getElementById('statSearches').textContent =
    stats ? stats.total_searches : '—';
}



function renderListings(listings) {
  const tbody = document.getElementById('listingsBody');

  if (!listings || listings.length === 0) {
    tbody.innerHTML = `
      <div class="table-row" style="grid-template-columns:1fr;">
        <div class="td" style="color:var(--gray-text);padding:32px 18px;text-align:center;">
          No listings yet.
          <a href="upload.html" style="color:var(--blue-mid);margin-left:4px;">Scan your first item →</a>
        </div>
      </div>`;
    return;
  }

  tbody.innerHTML = listings.map(listing => `
    <div class="table-row">
      <div class="td">${listing.product_name}</div>
      <div class="td-price">${formatPrice(listing.price_final ?? listing.price_low)}</div>
      <div class="td-date">${formatDate(listing.created_at)}</div>
      <div class="td">
        <span class="status-badge ${listing.status === 'saved' ? 'status-saved' : 'status-draft'}">
          ${listing.status === 'saved' ? 'Saved' : 'Draft'}
        </span>
      </div>
    </div>
  `).join('');
}



function renderError(message) {
  const tbody = document.getElementById('listingsBody');
  tbody.innerHTML = `
    <div class="table-row" style="grid-template-columns:1fr;">
      <div class="td" style="color:#A32D2D;padding:24px 18px;text-align:center;">${message}</div>
    </div>`;
}
