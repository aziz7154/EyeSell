// v4
const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_B  = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES    = ['image/jpeg', 'image/png', 'image/webp'];

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

let selectedFile = null;

chooseBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  fileInput.click();
});

dropzone.addEventListener('click', (e) => {
  if (e.target === chooseBtn || chooseBtn.contains(e.target)) return;
  if (e.target === submitBtn || submitBtn.contains(e.target)) return;
  fileInput.click();
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
  handleFileSelected(file);
});

function handleFileSelected(file) {
  clearError();

  if (!ALLOWED_TYPES.includes(file.type)) {
    showError('Only JPG, PNG, and WEBP images are accepted.');
    return;
  }

  if (file.size > MAX_FILE_SIZE_B) {
    showError(`File is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`);
    return;
  }

  selectedFile = file;

  const reader = new FileReader();
  reader.onload = (ev) => {
    imagePreview.src = ev.target.result;
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

submitBtn.addEventListener('click', async (e) => {
  e.preventDefault();
  e.stopPropagation();
  e.stopImmediatePropagation();
  clearError();

  if (!selectedFile) {
    showError('Please select an image before analyzing.');
    return;
  }

  setLoading(true);

  try {
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('hint', hintInput ? hintInput.value.trim() : '');

    setStatus('Analyzing image and fetching pricing...');
    const result = await Api.uploadImage(formData);

    Store.saveResult({
      image_id:      result.image_id,
      image_url:     result.image_url || null,
      product_name:  result.product_name,
      product_model: result.product_model || '',
      confidence:    result.confidence,
      tags:          result.tags || [],
      price_low:     result.price_low,
      price_high:    result.price_high,
      sources:       result.sources || [],
      listings:      result.listings || [],
    });

    window.location.href = 'results.html';

  } catch (err) {
    alert('ERROR: ' + err.message);
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
