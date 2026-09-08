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
    dropZone.classList.add('drag-over');
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
    fileNameEl.textContent = `✓ ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    extractBtn.disabled = false;
    setStatus('');
    resultsEl.classList.remove('visible');
}

extractBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const lang = langSelect.value;

    extractBtn.disabled = true;
    setStatus('<span class="loader"></span><strong>Multi-Agent Pipeline active:</strong> Routing document & executing specialist agent...');
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

    const {
        dispatched_agent,
        classification,
        document_metadata: meta,
        research_analysis: research,
        business_analysis: business,
        extracted_data: extracted,
        translation_pipeline: translation
    } = data;

    document.getElementById('dispatched-agent-title').textContent = dispatched_agent || 'General Document Specialist';
    const classBadge = document.getElementById('classification-badge');
    if (classification) {
        const confPercent = Math.round((classification.confidence || 0) * 100);
        classBadge.textContent = `${classification.doc_type.toUpperCase()} (${confPercent}%)`;
        document.getElementById('router-rationale').textContent = `Reasoning: ${classification.rationale}`;
    } else {
        classBadge.textContent = 'STANDARD';
        document.getElementById('router-rationale').textContent = '';
    }

    const researchCard = document.getElementById('research-card');
    if (research) {
        researchCard.style.display = 'block';
        document.getElementById('trl-level-badge').textContent = `TRL ${research.trl_level}`;
        document.getElementById('trl-justification').textContent = research.trl_justification || '';
        document.getElementById('research-novelty').textContent = research.scientific_novelty || '—';

        const useCasesEl = document.getElementById('commercial-use-cases');
        useCasesEl.innerHTML = '';
        (research.commercial_use_cases || []).forEach(useCase => {
            const span = document.createElement('span');
            span.className = 'tag';
            span.textContent = useCase;
            useCasesEl.appendChild(span);
        });

        const gapsEl = document.getElementById('development-gaps');
        gapsEl.innerHTML = '';
        (research.development_gaps || []).forEach(gap => {
            const li = document.createElement('li');
            li.textContent = gap;
            gapsEl.appendChild(li);
        });
    } else {
        researchCard.style.display = 'none';
    }

    const businessCard = document.getElementById('business-card');
    if (business) {
        businessCard.style.display = 'block';
        document.getElementById('biz-feasibility').textContent = `${business.feasibility_score} / 10`;
        document.getElementById('biz-budget').textContent = business.project_budget || 'Not specified';
        document.getElementById('biz-roi').textContent = business.roi_forecast || 'Not specified';
        document.getElementById('biz-recommendation').textContent = business.recommendation || '—';

        const riskTbody = document.getElementById('biz-risk-tbody');
        riskTbody.innerHTML = '';
        (business.risk_assessment || []).forEach(risk => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td><strong>${risk.key}</strong></td><td>${risk.value}</td>`;
            riskTbody.appendChild(tr);
        });
    } else {
        businessCard.style.display = 'none';
    }

    if (meta) {
        document.getElementById('meta-title').textContent = meta.title || '—';
        document.getElementById('meta-type').textContent = meta.document_type || '—';
        document.getElementById('meta-lang').textContent = meta.detected_language || '—';
    }

    if (translation) {
        document.getElementById('summary-text').textContent = translation.summary || '—';

        const actionList = document.getElementById('action-list');
        actionList.innerHTML = '';
        (translation.action_items || []).forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            actionList.appendChild(li);
        });
    }

    if (extracted) {
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
    }

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
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `multi_agent_extraction_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
});
