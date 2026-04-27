const result = Store.getResult();

if (!result) {
  window.location.href = 'upload.html';
  throw new Error('No result in session');
}

function renderResults(data) {
  renderProductCard(data);
  renderPriceBanner(data);
  renderListingGrid(data.listings);
  renderSourcesBreakdown(data.sources);
}

function renderProductCard(data) {
  if (data.image_url) {
    const imgEl = document.getElementById('productImage');
    imgEl.style.backgroundImage    = `url(${data.image_url})`;
    imgEl.style.backgroundSize     = 'cover';
    imgEl.style.backgroundPosition = 'center';
    imgEl.textContent              = '';
  }

  document.getElementById('confidencePct').textContent =
    `${Math.round(data.confidence * 100)}% confidence`;

  document.getElementById('productName').textContent  = data.product_name;
  document.getElementById('productModel').textContent = data.product_model || '';

  document.getElementById('productTags').innerHTML = data.tags
    .map(tag => `<span class="tag">${tag}</span>`)
    .join('');
}

function renderPriceBanner(data) {
  document.getElementById('priceRange').textContent =
    `${formatPrice(data.price_low)} — ${formatPrice(data.price_high)}`;

  const sourceNames = data.sources.map(s => s.name).join(', ');
  document.getElementById('priceMeta').textContent =
    `Based on ${data.listings.length} similar listing${data.listings.length !== 1 ? 's' : ''} · ${sourceNames}`;
}

function renderListingGrid(listings) {
  const grid = document.getElementById('listingGrid');
  if (!listings || listings.length === 0) {
    grid.innerHTML = '<p style="font-size:13px;color:var(--gray-text);padding:12px 0;">No similar listings found.</p>';
    return;
  }

  grid.innerHTML = listings.slice(0, 4).map(listing => `
    <div class="listing-card">
      <div class="listing-img">
        ${listing.image_url
          ? `<img src="${listing.image_url}" alt="${listing.title}" style="width:100%;height:100%;object-fit:cover;">`
          : 'img'}
      </div>
      <div class="listing-info">
        <div class="listing-price">${formatPrice(listing.price)}</div>
        <div class="listing-name">${listing.title} — ${listing.source}</div>
      </div>
    </div>
  `).join('');
}

function renderSourcesBreakdown(sources) {
  const container = document.getElementById('sourcesBreakdown');
  if (!sources || sources.length === 0) { container.innerHTML = ''; return; }

  const maxPrice = Math.max(...sources.map(s => s.avg_price));

  container.innerHTML = sources.map(source => `
    <div class="source-row">
      <div>
        <div class="source-name">${source.name}</div>
        <div class="source-count">${source.count} listing${source.count !== 1 ? 's' : ''}</div>
      </div>
      <div class="bar-wrap">
        <div class="bar" style="width:${Math.round((source.avg_price / maxPrice) * 100)}%"></div>
      </div>
      <div class="source-price">${formatPrice(source.avg_price)} avg</div>
    </div>
  `).join('');
}

function goToGenerate() {
  window.location.href = 'generate.html';
}

async function saveResults() {
  const btn      = document.getElementById('saveBtn');
  const original = btn.textContent;
  btn.textContent = 'Saving...';
  btn.disabled    = true;

  try {
    await Api.createListing({
      image_id:     result.image_id,
      product_name: result.product_name,
      description:  '',
      tags:         result.tags.join(', '),
      price_low:    result.price_low,
      price_high:   result.price_high,
      price_final:  Math.round((result.price_low + result.price_high) / 2),
    });
    btn.textContent = 'Saved!';
  } catch (err) {
    alert(err.message || 'Could not save. Please try again.');
    btn.textContent = original;
    btn.disabled    = false;
  }
}

renderResults(result);
