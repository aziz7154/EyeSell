document.addEventListener('DOMContentLoaded', async () => {
  let username = Auth.getUsername();
  if (!username) {
    try {
      const session = await Api.checkSession();
      if (session.loggedIn) {
        Auth.save(session.username);
        username = session.username;
      }
    } catch (e) {}
  }
  const userEl = document.getElementById('navUsername');
  if (userEl && username) userEl.textContent = username;
  loadDashboard();
});

async function handleLogout() {
  try {
    await Api.logout();
  } catch (e) {
    Auth.logout();
  }
  window.location.href = 'login.html';
}

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
      <div class="td">
        <button onclick="editListing(${listing.id}, '${listing.product_name.replace(/'/g, "\\'")}', ${listing.price_final ?? listing.price_low})"
          style="font-size:11px;color:var(--blue-mid);background:none;border:none;cursor:pointer;padding:0;">Edit</button>
        <span style="color:var(--gray-border);margin:0 4px;">|</span>
        <button onclick="deleteListing(${listing.id})"
          style="font-size:11px;color:#A32D2D;background:none;border:none;cursor:pointer;padding:0;">Delete</button>
      </div>
    </div>
  `).join('');
}

async function editListing(id, currentName, currentPrice) {
  const newName = prompt('Edit item name:', currentName);
  if (!newName) return;
  const newPrice = prompt('Edit price ($):', currentPrice);
  if (!newPrice) return;

  try {
    await fetch(`https://eyesell.org/listings/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        product_name: newName.trim(),
        price_final:  parseFloat(newPrice),
        description:  '',
        tags:         '',
      }),
    });
    loadDashboard();
  } catch (err) {
    alert('Could not update listing.');
  }
}

async function deleteListing(id) {
  if (!confirm('Delete this listing?')) return;
  try {
    await fetch(`https://eyesell.org/listings/${id}`, {
      method: 'DELETE',
      credentials: 'include',
    });
    loadDashboard();
  } catch (err) {
    alert('Could not delete listing.');
  }
}

function renderError(message) {
  const tbody = document.getElementById('listingsBody');
  tbody.innerHTML = `
    <div class="table-row" style="grid-template-columns:1fr;">
      <div class="td" style="color:#A32D2D;padding:24px 18px;text-align:center;">${message}</div>
    </div>`;
}
