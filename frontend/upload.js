const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_B  = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES    = ['image/jpeg', 'image/png', 'image/webp'];

const form         = document.getElementById('uploadForm');
const dropzone     = document.getElementById('dropzone');
const fileInput    = document.getElementById('fileInput');
const chooseBtn    = document.getElementById('chooseBtn');
const imagePreview = document.getElementById('imagePreview');
const uploadIcon   = document.getElementById('uploadIcon');
const zoneTitle    = document.getElementById('zoneTitle');
const zoneSub      = document.getElementById('zoneSub');
const fileNameEl   = document.getElementById('fileName');
const uploadError  = document.getElementById('uploadError');
const submitBtn    = document.getElementById('submitBtn');
const hintInput    = document.getElementById('hintInput');


chooseBtn.addEventListener('click', () => fileInput.click());

dropzone.addEventListener('click', (e) => {
  if (e.target !== chooseBtn) fileInput.click();
});

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFileSelected(fileInput.files[0]);
});



dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('is-drag-over');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('is-drag-over');
});

dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('is-drag-over');
  const file = e.dataTransfer.files[0];
  if (!file) return;
  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput.files = dt.files;
  handleFileSelected(file);
});


function handleFileSelected(file) {
  clearError();

  if (!ALLOWED_TYPES.includes(file.type)) {
    showError('Only JPG, PNG, and WEBP images are accepted.');
    fileInput.value = '';
    return;
  }

  if (file.size > MAX_FILE_SIZE_B) {
    showError(`File is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`);
    fileInput.value = '';
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    imagePreview.src = e.target.result;
    imagePreview.classList.add('is-visible');
  };
  reader.readAsDataURL(file);

  uploadIcon.style.display = 'none';
  zoneTitle.textContent    = 'Image selected';
  zoneSub.style.display    = 'none';
  fileNameEl.textContent   = file.name;
  fileNameEl.classList.add('is-visible');
  dropzone.classList.add('is-file-loaded');
}


form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();

  if (!fileInput.files || fileInput.files.length === 0) {
    showError('Please select an image before analyzing.');
    return;
  }

  setLoading(true);

  try {
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('hint', hintInput ? hintInput.value.trim() : '');

    setStatus('Uploading image...');
    const uploadResult = await Api.uploadImage(formData);

    setStatus('Identifying product...');
    const analysisResult = await Api.analyzeImage(
      uploadResult.image_id,
      hintInput ? hintInput.value.trim() : ''
    );

    setStatus('Fetching pricing data...');
    const pricingResult = await Api.searchPricing(analysisResult.product_name);

    Store.saveResult({
      image_id:      uploadResult.image_id,
      image_url:     uploadResult.image_url || null,
      product_name:  analysisResult.product_name,
      product_model: analysisResult.product_model || '',
      confidence:    analysisResult.confidence,
      tags:          analysisResult.tags || [],
      price_low:     pricingResult.price_low,
      price_high:    pricingResult.price_high,
      sources:       pricingResult.sources || [],
      listings:      pricingResult.listings || [],
    });

    window.location.href = 'results.html';

  } catch (err) {
    showError(err.message || 'Something went wrong. Please try again.');
    setLoading(false);
    setStatus('Analyze image →');
  }
});



function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle('is-loading', isLoading);
}

function setStatus(text) {
  const label = submitBtn.querySelector('.analyze-btn__label');
  if (label) label.textContent = text;
}

function showError(message) {
  uploadError.textContent = message;
  uploadError.classList.add('is-visible');
}

function clearError() {
  uploadError.textContent = '';
  uploadError.classList.remove('is-visible');
}
