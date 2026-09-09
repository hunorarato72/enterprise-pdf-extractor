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

const i18n = {
    'Hungarian': {
        btn: 'Dokumentum elemzése',
        download: 'JSON letöltése',
        loadingTitle: 'Feldolgozás folyamatban:',
        loadingDesc: 'Dokumentum besorolása és adatkivonatolás...',
        guideHeading: 'Feldolgozási és Ágens Útvonalak',
        badgeAgent: 'Specialista Ágens',
        badgeBaseline: 'Alapszintű feldolgozás',
        guideResearch: '<strong>Tudományos & K+F cikkek:</strong> TRL szint kalkuláció (1–9), technológia-transzfer potenciál és piaci akadályok felmérése.',
        guideBiz: '<strong>Üzleti tervek & Pályázatok:</strong> Megvalósíthatósági pontszám (1–10), ROI becslés és kockázati mátrix.',
        guideGeneral: '<strong>Minden egyéb dokumentum (számlák, szerződések, jegyzetek):</strong> Nem igényel dedikált ágenst — szabványos adatkivonatolási és összefoglaló pipeline fut le.'
    },
    'English': {
        btn: 'Extract & Analyze',
        download: 'Download JSON',
        loadingTitle: 'Processing document:',
        loadingDesc: 'Classifying document & extracting structured data...',
        guideHeading: 'Processing & Agent Routes',
        badgeAgent: 'Specialist Agent',
        badgeBaseline: 'Baseline Pipeline',
        guideResearch: '<strong>Scientific & R&D Papers:</strong> Technology Readiness Level (TRL 1–9), tech-transfer potential, and validation gaps.',
        guideBiz: '<strong>Business Plans & Proposals:</strong> Commercial feasibility score (1–10), ROI forecast, budget, and risk matrix.',
        guideGeneral: '<strong>All other documents (invoices, contracts, memos):</strong> No agent required — standard structured entity extraction.'
    },
    'German': {
        btn: 'Dokument analysieren',
        download: 'JSON herunterladen',
        loadingTitle: 'Dokument wird verarbeitet:',
        loadingDesc: 'Dokumentklassifizierung und Datenextraktion...',
        guideHeading: 'Pipeline-Routing & Agenten-Pfade',
        badgeAgent: 'Spezialist-Agent',
        badgeBaseline: 'Standardverarbeitung',
        guideResearch: '<strong>Wissenschaftliche & F&E-Dokumente:</strong> TRL-Berechnung (1–9), Technologietransfer-Potenzial und Marktlücken.',
        guideBiz: '<strong>Geschäftspläne & Förderanträge:</strong> Machbarkeitsbewertung (1–10), ROI-Prognose und Risikomatrix.',
        guideGeneral: '<strong>Alle anderen Dokumente (Rechnungen, Verträge, Notizen):</strong> Kein Agent erforderlich — standardmäßige Datenextraktion.'
    },
    'French': {
        btn: 'Analyser le document',
        download: 'Télécharger JSON',
        loadingTitle: 'Traitement en cours :',
        loadingDesc: 'Classification du document et extraction des données...',
        guideHeading: 'Routage du pipeline et exécution des agents',
        badgeAgent: 'Agent Spécialiste',
        badgeBaseline: 'Traitement Standard',
        guideResearch: '<strong>Articles scientifiques & R&D :</strong> Évaluation TRL (1–9), potentiel de transfert de technologie et obstacles marché.',
        guideBiz: '<strong>Propositions commerciales & projets :</strong> Score de faisabilité (1–10), prévision du ROI et matrice des risques.',
        guideGeneral: '<strong>Tous les autres documents (factures, contrats, mémos) :</strong> Aucun agent requis — extraction et synthèse standard.'
    },
    'Spanish': {
        btn: 'Analizar documento',
        download: 'Descargar JSON',
        loadingTitle: 'Procesando documento:',
        loadingDesc: 'Clasificando documento y extrayendo datos estructurados...',
        guideHeading: 'Rutas del pipeline y ejecución de agentes',
        badgeAgent: 'Agente Especialista',
        badgeBaseline: 'Procesamiento estándar',
        guideResearch: '<strong>Artículos científicos e I+D:</strong> Nivel TRL (1–9), potencial de transferencia tecnológica y barreras de mercado.',
        guideBiz: '<strong>Propuestas comerciales y proyectos:</strong> Puntuación de viabilidad (1–10), estimación de ROI y matriz de riesgos.',
        guideGeneral: '<strong>Todos los demás documentos (facturas, contratos, notas):</strong> No requiere agente — extracción de datos estándar.'
    },
    'Italian': {
        btn: 'Analizza documento',
        download: 'Scarica JSON',
        loadingTitle: 'Elaborazione in corso:',
        loadingDesc: 'Classificazione del documento ed estrazione dei dati...',
        guideHeading: 'Instradamento della pipeline e agenti',
        badgeAgent: 'Agente Specialista',
        badgeBaseline: 'Elaborazione standard',
        guideResearch: '<strong>Articoli scientifici e R&S:</strong> Livello TRL (1–9), potenziale di trasferimento tecnologico e barriere di mercato.',
        guideBiz: '<strong>Proposte commerciali e progetti:</strong> Punteggio di fattibilità (1–10), previsione del ROI e matrice dei rischi.',
        guideGeneral: '<strong>Tutti gli altri documenti (fatture, contratti, note):</strong> Nessun agente richiesto — estrazione e sintesi standard.'
    }
};

langSelect.addEventListener('change', updateLanguageUI);

function updateLanguageUI() {
    const lang = langSelect.value;
    const t = i18n[lang] || i18n['English'];

    extractBtn.textContent = t.btn;

    const downloadBtnEl = document.getElementById('download-btn');
    if (downloadBtnEl) {
        downloadBtnEl.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            ${t.download}
        `;
    }

    const guideHeading = document.getElementById('guide-heading');
    if (guideHeading) guideHeading.textContent = t.guideHeading;

    const bAgent1 = document.getElementById('badge-agent-1');
    if (bAgent1) bAgent1.textContent = t.badgeAgent;
    const bAgent2 = document.getElementById('badge-agent-2');
    if (bAgent2) bAgent2.textContent = t.badgeAgent;
    const bBaseline = document.getElementById('badge-baseline');
    if (bBaseline) bBaseline.textContent = t.badgeBaseline;

    const descRes = document.getElementById('guide-desc-research');
    if (descRes) descRes.innerHTML = t.guideResearch;
    const descBiz = document.getElementById('guide-desc-biz');
    if (descBiz) descBiz.innerHTML = t.guideBiz;
    const descGen = document.getElementById('guide-desc-general');
    if (descGen) descGen.innerHTML = t.guideGeneral;
}
updateLanguageUI();

extractBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const lang = langSelect.value;
    const t = i18n[lang] || i18n['English'];

    extractBtn.disabled = true;
    setStatus(`<span class="loader"></span><strong>${t.loadingTitle}</strong> ${t.loadingDesc}`);
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
        setStatus(err.message || 'Hiba történt a feldolgozás során.', true);
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
