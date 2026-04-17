const result = Store.getResult();

if (!result) {
  window.location.href = 'upload.html';
}



function buildTitle(data) {
  const model = data.product_model ? ` — ${data.product_model}` : '';
  return `${data.product_name}${model} — Good Condition`;
}

function buildDescription(data) {
  const tagLine = data.tags.length ? `Includes: ${data.tags.slice(0, 3).join(', ')}.` : '';
  return `Selling a ${data.product_name} in great used condition. ${tagLine} Ships within 1-2 business days.`;
}


function renderGenerate(data) {
  const suggested = Math.round((data.price_low + data.price_high) / 2);

  document.getElementById('titleField').value = buildTitle(data);
  document.getElementById('descField').value  = buildDescription(data);
  document.getElementById('priceField').value = formatPrice(suggested);

  document.getElementById('priceLow').textContent       = formatPrice(data.price_low);
  document.getElementById('priceHigh').textContent      = formatPrice(data.price_high);
  document.getElementById('suggestedPrice').textContent = formatPrice(suggested);

  const tagsContainer = document.getElementById('tagsContainer');
  tagsContainer.innerHTML =
    data.tags.map(tag => `<span class="tag" onclick="this.remove()">${tag}</span>`).join('') +
    `<span class="tag-add" onclick="addTag()">+ Add tag</span>`;
}



function addTag() {
  const name = prompt('Enter a tag:');
  if (!name || !name.trim()) return;
  const container = document.getElementById('tagsContainer');
  const addBtn    = container.querySelector('.tag-add');
  const newTag    = document.createElement('span');
  newTag.className   = 'tag';
  newTag.textContent = name.trim();
  newTag.addEventListener('click', () => newTag.remove());
  container.insertBefore(newTag, addBtn);
}

function getTags() {
  return [...document.querySelectorAll('#tagsContainer .tag')]
    .map(t => t.textContent.trim());
}



document.getElementById('copyBtn').addEventListener('click', () => {
  const title = document.getElementById('titleField').value;
  const desc  = document.getElementById('descField').value;
  const price = document.getElementById('priceField').value;
  const tags  = getTags().join(', ');

  const text = `${title}\n\n${desc}\n\nTags: ${tags}\n\nPrice: ${price}`;

  navigator.clipboard.writeText(text).then(() => {
    const toast = document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }).catch(() => {
    alert('Could not copy to clipboard. Please copy manually.');
  });
});



document.getElementById('saveBtn').addEventListener('click', async () => {
  const btn      = document.getElementById('saveBtn');
  const original = btn.textContent;
  btn.textContent = 'Saving...';
  btn.disabled    = true;

  try {
    const price = parseFloat(
      document.getElementById('priceField').value.replace('$', '').trim()
    ) || 0;

    await Api.createListing({
      image_id:     result.image_id,
      product_name: document.getElementById('titleField').value.trim(),
      description:  document.getElementById('descField').value.trim(),
      tags:         getTags().join(', '),
      price_low:    result.price_low,
      price_high:   result.price_high,
      price_final:  price,
    });

    Store.clearResult();
    window.location.href = 'dashboard.html';

  } catch (err) {
    alert(err.message || 'Could not save. Please try again.');
    btn.textContent = original;
    btn.disabled    = false;
  }
});



renderGenerate(result);
