const dropZone    = document.getElementById('drop-zone');
const fileInput   = document.getElementById('file-input');
const fileNameEl  = document.getElementById('file-name');
const langSelect  = document.getElementById('lang-select');
const extractBtn  = document.getElementById('extract-btn');
const statusEl    = document.getElementById('status');
const resultsEl   = document.getElementById('results');
const jsonOutput  = document.getElementById('json-output');
const downloadBtn = document.getElementById('download-btn');

let selectedFile = null;
let lastData     = null;

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
    handleFile(fileInput.files[0]);
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

function handleFile(file) {
    if (!file) return;

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        setStatus('Only PDF files are accepted.', true);
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        setStatus('File exceeds the 10 MB limit.', true);
        return;
    }

    selectedFile = file;
    fileNameEl.textContent = `✓ ${file.name}`;
    extractBtn.disabled = false;
    setStatus('');
    resultsEl.classList.remove('visible');
}

extractBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const lang = langSelect.value;

    extractBtn.disabled = true;
    setStatus('<span class="loader"></span>Processing document…');
    resultsEl.classList.remove('visible');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch(`/api/v1/extract?target_language=${encodeURIComponent(lang)}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        renderResults(data, lang);
        setStatus('');

    } catch (err) {
        setStatus(err.message || 'An unexpected error occurred.', true);
    } finally {
        extractBtn.disabled = false;
    }
});

function renderResults(data, lang) {
    lastData = data;

    const { document_metadata: meta, extracted_data: extracted, translation_pipeline: translation } = data;

    document.getElementById('meta-title').textContent    = meta.title         || '—';
    document.getElementById('meta-type').textContent     = meta.document_type || '—';
    document.getElementById('meta-lang').textContent     = meta.detected_language || '—';

    document.getElementById('summary-text').textContent  = translation.summary || '—';

    const actionList = document.getElementById('action-list');
    actionList.innerHTML = '';
    (translation.action_items || []).forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        actionList.appendChild(li);
    });

    const entitiesEl = document.getElementById('entities-list');
    entitiesEl.innerHTML = '';
    (extracted.key_entities || []).forEach(entity => {
        const span = document.createElement('span');
        span.className = 'tag';
        span.textContent = entity;
        entitiesEl.appendChild(span);
    });

    const tbody = document.getElementById('numbers-tbody');
    tbody.innerHTML = '';
    (extracted.important_numbers || []).forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${item.key}</td><td>${item.value}</td>`;
        tbody.appendChild(tr);
    });

    jsonOutput.textContent = JSON.stringify(data, null, 2);

    resultsEl.classList.add('visible');
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setStatus(html, isError = false) {
    statusEl.innerHTML = html;
    statusEl.className = isError ? 'error' : '';
}

downloadBtn.addEventListener('click', () => {
    if (!lastData) return;
    const blob = new Blob([JSON.stringify(lastData, null, 2)], { type: 'application/json' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'extraction_result.json';
    a.click();
    URL.revokeObjectURL(url);
});
