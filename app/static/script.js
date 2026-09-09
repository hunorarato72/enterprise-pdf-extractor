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
    fileNameEl.textContent = `✓ ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
    extractBtn.disabled = false;
    setStatus('');
    resultsEl.classList.remove('visible');
}

langSelect.addEventListener('change', updateButtonLabel);

function updateButtonLabel() {
    const isHu = (langSelect.value === 'Hungarian');
    extractBtn.textContent = isHu ? 'Dokumentum elemzése' : 'Extract & Analyze';
    const downloadBtnEl = document.getElementById('download-btn');
    if (downloadBtnEl) {
        downloadBtnEl.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            ${isHu ? 'JSON letöltése' : 'Download JSON'}
        `;
    }
}
updateButtonLabel();

extractBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const lang = langSelect.value;
    const isHu = (lang === 'Hungarian');

    extractBtn.disabled = true;
    setStatus(`<span class="loader"></span><strong>${isHu ? 'Feldolgozás folyamatban:' : 'Processing document:'}</strong> ${isHu ? 'Dokumentum besorolása és adatkivonatolás...' : 'Classifying document & extracting structured data...'}`);
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
        setStatus(err.message || (isHu ? 'Váratlan hiba történt.' : 'An unexpected error occurred.'), true);
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

    const isHungarian = (lang === 'Hungarian');

    const routeLabelEl = document.getElementById('agent-route-label');
    if (routeLabelEl) {
        routeLabelEl.textContent = isHungarian ? 'Feldolgozási folyamat' : 'Processing Pipeline';
    }

    document.getElementById('dispatched-agent-title').textContent = dispatched_agent || (isHungarian ? '📄 Standard adatkinyerés' : '📄 Standard Document Extraction');
    const classBadge = document.getElementById('classification-badge');
    if (classification) {
        const confPercent = Math.round((classification.confidence || 0) * 100);
        const typeLabel = classification.doc_type === 'general' ? (isHungarian ? 'STANDARD / ÁLTALÁNOS' : 'STANDARD / GENERAL') : classification.doc_type.toUpperCase();
        classBadge.textContent = `${typeLabel} (${confPercent}%)`;
        const rationalePrefix = isHungarian ? 'Indoklás' : 'Reasoning';
        document.getElementById('router-rationale').textContent = `${rationalePrefix}: ${classification.rationale}`;
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
        const notSpecifiedText = isHungarian ? 'Nincs megadva' : 'Not specified';
        document.getElementById('biz-budget').textContent = business.project_budget || notSpecifiedText;
        document.getElementById('biz-roi').textContent = business.roi_forecast || notSpecifiedText;
        document.getElementById('biz-recommendation').textContent = business.recommendation || '—';

        const riskTbody = document.getElementById('biz-risk-tbody');
        riskTbody.innerHTML = '';
        (business.risk_assessment || []).forEach(risk => {
            const tr = document.createElement('tr');
            const tdKey = document.createElement('td');
            const strong = document.createElement('strong');
            strong.textContent = risk.key;
            tdKey.appendChild(strong);
            const tdVal = document.createElement('td');
            tdVal.textContent = risk.value;
            tr.appendChild(tdKey);
            tr.appendChild(tdVal);
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
            const tdKey = document.createElement('td');
            tdKey.textContent = item.key;
            const tdVal = document.createElement('td');
            tdVal.textContent = item.value;
            tr.appendChild(tdKey);
            tr.appendChild(tdVal);
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
