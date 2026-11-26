/**
 * YouTube Shorts Generator - Client Application
 */

// Application State
const state = {
    currentProject: null,
    autosaveTimer: null,
    isSaving: false
};

// DOM Elements
const DOM = {
    // Project & Sidebar
    btnNewProject: document.getElementById('btn-new-project'),
    projectsList: document.getElementById('projects-list'),
    projectTitleInput: document.getElementById('project-title-input'),
    btnEditTitle: document.getElementById('btn-edit-title'),
    saveStatus: document.getElementById('save-status'),
    systemStatus: document.getElementById('system-status'),

    // Editor & Toolbar
    scriptEditor: document.getElementById('script-editor'),
    wordCount: document.getElementById('word-count'),
    estDuration: document.getElementById('est-duration'),
    targetDurationDisplay: document.getElementById('target-duration-display'),
    btnRandomLength: document.getElementById('btn-random-length'),
    cheatsheetContent: document.querySelector('.cheatsheet-content'),
    presetSelector: document.getElementById('preset-selector'),
    btnSelectVoice: document.getElementById('btn-select-voice'),
    btnPreviewAudio: document.getElementById('btn-preview-audio'),

    // Audio Preview
    audioPreviewBar: document.getElementById('audio-preview-bar'),
    audioPreviewLabel: document.getElementById('audio-preview-label'),
    audioPreviewTag: document.getElementById('audio-preview-tag'),
    audioPlayer: document.getElementById('audio-player'),
    btnPreviewParagraph: document.getElementById('btn-preview-paragraph'),
    btnPreviewAll: document.getElementById('btn-preview-all'),
    btnCancelPreview: document.getElementById('btn-cancel-preview'),
    btnCloseAudio: document.getElementById('btn-close-audio'),

    // Voice Modal
    voiceModal: document.getElementById('voice-modal'),
    voiceOptionsList: document.getElementById('voice-options-list'),
    btnCloseVoiceModal: document.getElementById('btn-close-voice-modal'),
    btnCancelVoice: document.getElementById('btn-cancel-voice'),
    btnSaveVoice: document.getElementById('btn-save-voice'),

    // Export Pipeline & Modal
    btnExportProject: document.getElementById('btn-export-project'),
    exportModal: document.getElementById('export-modal'),
    exportModalTitle: document.getElementById('export-modal-title'),
    btnCloseExportModal: document.getElementById('btn-close-export-modal'),
    btnCloseExport: document.getElementById('btn-close-export'),
    exportPrecheckSection: document.getElementById('export-precheck-section'),
    btnModalPreviewAudio: document.getElementById('btn-modal-preview-audio'),
    exportAuditionStatus: document.getElementById('export-audition-status'),
    exportAuditionDuration: document.getElementById('export-audition-duration'),
    exportAuditionPlayer: document.getElementById('export-audition-player'),
    exportPrecheckWarning: document.getElementById('export-precheck-warning'),
    btnCancelPreExport: document.getElementById('btn-cancel-pre-export'),
    btnConfirmStartExport: document.getElementById('btn-confirm-start-export'),
    exportProgressSection: document.getElementById('export-progress-section'),
    exportStepLabel: document.getElementById('export-step-label'),
    exportProgressBar: document.getElementById('export-progress-bar'),
    exportProgressPercent: document.getElementById('export-progress-percent'),
    exportDurationInfo: document.getElementById('export-duration-info'),
    exportWarningBox: document.getElementById('export-warning-box'),
    exportResultSection: document.getElementById('export-result-section'),
    btnDownloadNarration: document.getElementById('btn-download-narration'),
    btnDownloadSubtitles: document.getElementById('btn-download-subtitles'),
    btnDownloadSources: document.getElementById('btn-download-sources'),

    // Export History Modal (R5.8, R5.9)
    btnExportHistory: document.getElementById('btn-export-history'),
    exportHistoryModal: document.getElementById('export-history-modal'),
    exportHistoryList: document.getElementById('export-history-list'),
    btnCloseHistoryModal: document.getElementById('btn-close-history-modal'),
    btnCloseHistory: document.getElementById('btn-close-history'),
    btnViewHistoryFromModal: document.getElementById('btn-view-history-from-modal'),

    // Audio FX Modal (R2.12)
    btnAudioFx: document.getElementById('btn-audio-fx'),
    audioFxModal: document.getElementById('audio-fx-modal'),
    btnCloseAudioFxModal: document.getElementById('btn-close-audio-fx-modal'),
    btnCloseAudioFx: document.getElementById('btn-close-audio-fx'),
    btnSaveAudioFx: document.getElementById('btn-save-audio-fx'),
    fxSaveStatus: document.getElementById('fx-save-status'),
    fxCompression: document.getElementById('fx-compression'),
    fxMaleEq: document.getElementById('fx-male-eq'),
    fxDeesser: document.getElementById('fx-deesser'),
    fxReverb: document.getElementById('fx-reverb'),
    fxLoudnorm: document.getElementById('fx-loudnorm'),

    // Paragraph Takes Modal (R2.11)
    btnParagraphTakes: document.getElementById('btn-paragraph-takes'),
    paragraphTakesModal: document.getElementById('paragraph-takes-modal'),
    btnCloseTakesModal: document.getElementById('btn-close-takes-modal'),
    btnCloseTakes: document.getElementById('btn-close-takes'),
    takesParagraphSelect: document.getElementById('takes-paragraph-select'),
    btnGenerateNewTake: document.getElementById('btn-generate-new-take'),
    takesParaPreview: document.getElementById('takes-para-preview'),
    takesLoading: document.getElementById('takes-loading'),
    paragraphTakesList: document.getElementById('paragraph-takes-list'),

    // Gemini Writing Assistant
    aiNotes: document.getElementById('ai-notes'),
    btnSuggestNext: document.getElementById('btn-suggest-next'),
    btnRewriteScript: document.getElementById('btn-rewrite-script'),
    btnOutlineDraft: document.getElementById('btn-outline-draft'),

    // Suggestions Modal
    suggestionsModal: document.getElementById('suggestions-modal'),
    suggestionsList: document.getElementById('suggestions-list'),
    btnCloseSuggestionsModal: document.getElementById('btn-close-suggestions-modal'),
    btnCancelSuggestions: document.getElementById('btn-cancel-suggestions'),

    // Rewrite Modal
    rewriteModal: document.getElementById('rewrite-modal'),
    rewriteOriginal: document.getElementById('rewrite-original'),
    rewriteResult: document.getElementById('rewrite-result'),
    btnCloseRewriteModal: document.getElementById('btn-close-rewrite-modal'),
    btnCancelRewrite: document.getElementById('btn-cancel-rewrite'),
    btnApplyRewrite: document.getElementById('btn-apply-rewrite'),

    // Outline Modal
    outlineModal: document.getElementById('outline-modal'),
    outlineTopic: document.getElementById('outline-topic'),
    outlineDuration: document.getElementById('outline-duration'),
    outlineLoading: document.getElementById('outline-loading'),
    outlineResultSection: document.getElementById('outline-result-section'),
    outlineResult: document.getElementById('outline-result'),
    btnGenerateOutline: document.getElementById('btn-generate-outline'),
    btnApplyOutline: document.getElementById('btn-apply-outline'),
    btnCloseOutlineModal: document.getElementById('btn-close-outline-modal'),
    btnCancelOutline: document.getElementById('btn-cancel-outline'),

    // Auto-Pace Modal (R2.8)
    btnAutoPace: document.getElementById('btn-auto-pace'),
    autoPaceModal: document.getElementById('auto-pace-modal'),
    autoPaceOriginal: document.getElementById('auto-pace-original'),
    autoPaceResult: document.getElementById('auto-pace-result'),
    btnCloseAutoPaceModal: document.getElementById('btn-close-auto-pace-modal'),
    btnCancelAutoPace: document.getElementById('btn-cancel-auto-pace'),
    btnApplyAutoPace: document.getElementById('btn-apply-auto-pace'),

    // Fact Check (R4)
    btnCheckFacts: document.getElementById('btn-check-facts'),
    factcheckLoading: document.getElementById('factcheck-loading'),
    factcheckDisclaimer: document.getElementById('factcheck-disclaimer'),
    claimsList: document.getElementById('claims-list'),
    safeRewriteModal: document.getElementById('safe-rewrite-modal'),
    safeOrigSentence: document.getElementById('safe-orig-sentence'),
    safeNewSentence: document.getElementById('safe-new-sentence'),
    btnCloseSafeRewrite: document.getElementById('btn-close-safe-rewrite'),
    btnCancelSafeRewrite: document.getElementById('btn-cancel-safe-rewrite'),
    btnApplySafeRewrite: document.getElementById('btn-apply-safe-rewrite'),

    // Tabs
    tabButtons: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content')
};

// ==========================================
// 1. Calculations & Stats
// ==========================================

function calculateStats(text) {
    if (!text || !text.trim()) {
        return { words: 0, duration: 0 };
    }

    // 1. Calculate pause time from [pause X] tags
    let pauseSeconds = 0;
    const pauseRegex = /\[pause\s+([0-9.]+)\]/gi;
    let match;
    while ((match = pauseRegex.exec(text)) !== null) {
        const val = parseFloat(match[1]);
        if (!isNaN(val)) pauseSeconds += val;
    }

    // 2. Remove pacing tags to count speakable words
    const cleanText = text
        .replace(/\[\/?(pause(\s+[0-9.]+)?|slow|fast|whisper)\]/gi, ' ')
        .replace(/\*([^*]+)\*/g, '$1') // preserve word inside *emphasis*
        .trim();

    const words = cleanText ? cleanText.split(/\s+/).filter(Boolean).length : 0;

    // About 150 words per minute => 2.5 words/sec => 0.4s per word
    const duration = Math.round((words * 0.4) + pauseSeconds);

    return { words, duration };
}

function updateStatsDisplay() {
    const text = DOM.scriptEditor.value;
    const { words, duration } = calculateStats(text);

    DOM.wordCount.textContent = words;

    const mins = Math.floor(duration / 60);
    const secs = duration % 60;
    const durationText = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
    DOM.estDuration.textContent = durationText;

    // Visual indicator if outside 60-180s target range
    const badge = DOM.estDuration.parentElement;
    if (duration > 0 && (duration < 60 || duration > 180)) {
        DOM.estDuration.classList.add('text-warning');
        DOM.estDuration.title = "Khuyến nghị thời lượng Shorts từ 60 đến 180 giây";
    } else {
        DOM.estDuration.classList.remove('text-warning');
        DOM.estDuration.title = "";
    }
}

function setTargetDuration(seconds) {
    if (!seconds) seconds = 90;
    const minWords = Math.round(seconds * 2.2);
    const maxWords = Math.round(seconds * 2.8);
    DOM.targetDurationDisplay.textContent = `Mục tiêu: ${seconds}s (~${minWords} - ${maxWords} từ)`;

    if (state.currentProject) {
        state.currentProject.target_duration = seconds;
        scheduleAutosave();
    }
}

function randomTargetDuration() {
    // Pick random between 60 and 180 seconds
    const randomSecs = Math.floor(Math.random() * (180 - 60 + 1)) + 60;
    setTargetDuration(randomSecs);
}

// ==========================================
// 2. Project Management (CRUD)
// ==========================================

async function fetchProjects() {
    try {
        const res = await fetch('/api/projects');
        if (!res.ok) throw new Error('Không thể tải danh sách dự án');
        return await res.json();
    } catch (err) {
        console.error(err);
        return [];
    }
}

async function renderProjectsList() {
    const projects = await fetchProjects();
    DOM.projectsList.innerHTML = '';

    if (projects.length === 0) {
        DOM.projectsList.innerHTML = '<div class="empty-state">Chưa có dự án nào.<br>Bấm "+ Mới" để bắt đầu!</div>';
        return;
    }

    projects.forEach(proj => {
        const item = document.createElement('div');
        item.className = 'project-item';
        if (state.currentProject && state.currentProject.id === proj.id) {
            item.classList.add('active');
        }

        const dateStr = proj.updated_at ? new Date(proj.updated_at).toLocaleDateString('vi-VN', {
            month: 'numeric',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : '';

        item.innerHTML = `
            <div class="project-info" data-id="${proj.id}">
                <div class="project-title">${escapeHtml(proj.title || 'Dự án chưa đặt tên')}</div>
                <div class="project-meta">
                    <span>${dateStr}</span>
                    <span>${proj.word_count || 0} từ</span>
                </div>
            </div>
            <div class="project-item-actions">
                <button class="btn-icon btn-rename" data-id="${proj.id}" title="Đổi tên dự án">✏️</button>
                <button class="btn-icon btn-dup" data-id="${proj.id}" title="Nhân bản">📋</button>
                <button class="btn-icon btn-del" data-id="${proj.id}" title="Xóa">🗑️</button>
            </div>
        `;

        // Click to open
        item.querySelector('.project-info').addEventListener('click', () => {
            loadProject(proj.id);
        });

        // Rename
        item.querySelector('.btn-rename').addEventListener('click', (e) => {
            e.stopPropagation();
            renameProject(proj.id, proj.title);
        });

        // Duplicate
        item.querySelector('.btn-dup').addEventListener('click', (e) => {
            e.stopPropagation();
            duplicateProject(proj.id);
        });

        // Delete
        item.querySelector('.btn-del').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteProject(proj.id, proj.title);
        });

        DOM.projectsList.appendChild(item);
    });
}

async function loadProject(id) {
    try {
        const res = await fetch(`/api/projects/${id}`);
        if (!res.ok) throw new Error('Không thể tải chi tiết dự án');
        const proj = await res.json();

        state.currentProject = proj;
        DOM.projectTitleInput.value = proj.title || 'Dự án chưa đặt tên';
        DOM.scriptEditor.value = proj.script || '';
        if (DOM.presetSelector) {
            DOM.presetSelector.value = proj.pacing_preset || 'mystery';
        }
        setTargetDuration(proj.target_duration || 90);
        updateStatsDisplay();

        DOM.saveStatus.textContent = 'Đã lưu';
        DOM.saveStatus.className = 'save-status';

        // Render fact-checked claims if present
        renderClaimsList(proj.claims || []);

        // Re-render project list to highlight active item
        renderProjectsList();
    } catch (err) {
        alert('Lỗi tải dự án: ' + err.message);
    }
}

async function createNewProject() {
    try {
        const res = await fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: 'Dự án Shorts mới',
                script: ''
            })
        });
        if (!res.ok) throw new Error('Không thể tạo dự án mới');
        const newProj = await res.json();
        await loadProject(newProj.id);
    } catch (err) {
        alert('Lỗi tạo dự án: ' + err.message);
    }
}

async function duplicateProject(id) {
    try {
        const res = await fetch(`/api/projects/${id}/duplicate`, { method: 'POST' });
        if (!res.ok) throw new Error('Không thể nhân bản dự án');
        const duplicated = await res.json();
        await loadProject(duplicated.id);
    } catch (err) {
        alert('Lỗi nhân bản: ' + err.message);
    }
}

async function deleteProject(id, title) {
    if (!confirm(`Bạn có chắc muốn xóa dự án "${title || id}"?`)) return;

    try {
        const res = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Không thể xóa dự án');

        if (state.currentProject && state.currentProject.id === id) {
            state.currentProject = null;
            DOM.projectTitleInput.value = '';
            DOM.scriptEditor.value = '';
            updateStatsDisplay();
        }

        const projects = await fetchProjects();
        if (projects.length > 0) {
            await loadProject(projects[0].id);
        } else {
            await createNewProject();
        }
    } catch (err) {
        alert('Lỗi xóa dự án: ' + err.message);
    }
}

async function renameProject(id, currentTitle) {
    const newTitle = prompt('Nhập tên mới cho dự án:', currentTitle || '');
    if (newTitle === null) return; // Người dùng bấm Hủy
    const cleanTitle = newTitle.trim();
    if (!cleanTitle) {
        alert('Tên dự án không được để trống.');
        return;
    }

    try {
        const res = await fetch(`/api/projects/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: cleanTitle })
        });
        if (!res.ok) throw new Error('Không thể đổi tên dự án');
        const updated = await res.json();

        // Nếu dự án đang mở đúng là dự án này thì cập nhật input và state
        if (state.currentProject && state.currentProject.id === id) {
            state.currentProject.title = updated.title;
            DOM.projectTitleInput.value = updated.title;
        }

        await renderProjectsList();
    } catch (err) {
        alert('Lỗi đổi tên dự án: ' + err.message);
    }
}

// ==========================================
// 3. Autosave Engine
// ==========================================

function scheduleAutosave() {
    if (!state.currentProject) return;

    DOM.saveStatus.textContent = 'Đang lưu...';
    DOM.saveStatus.className = 'save-status saving';

    clearTimeout(state.autosaveTimer);
    state.autosaveTimer = setTimeout(async () => {
        await executeAutosave();
    }, 1500); // 1.5 seconds debounce
}

async function executeAutosave() {
    if (!state.currentProject || state.isSaving) return;

    state.isSaving = true;
    try {
        const payload = {
            title: DOM.projectTitleInput.value.trim() || 'Dự án chưa đặt tên',
            script: DOM.scriptEditor.value,
            target_duration: state.currentProject.target_duration || 90,
            pacing_preset: DOM.presetSelector ? DOM.presetSelector.value : 'mystery'
        };

        const res = await fetch(`/api/projects/${state.currentProject.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Lỗi phản hồi từ server');
        const updated = await res.json();
        state.currentProject = updated;

        const timeStr = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        DOM.saveStatus.textContent = `Đã lưu (${timeStr})`;
        DOM.saveStatus.className = 'save-status saved';

        // Update title/word count in sidebar without full re-render
        const activeItem = DOM.projectsList.querySelector(`.project-item.active .project-title`);
        if (activeItem) {
            activeItem.textContent = updated.title;
        }
    } catch (err) {
        console.error('Autosave error:', err);
        DOM.saveStatus.textContent = 'Lỗi tự động lưu';
        DOM.saveStatus.className = 'save-status error';
    } finally {
        state.isSaving = false;
    }
}

// ==========================================
// 4. Interactive Cheatsheet & Quick Pacing Toolbar (R1.4, R2.13)
// ==========================================

function setupQuickPacingToolbar() {
    const toolbar = document.getElementById('pacing-quick-toolbar');
    const textarea = DOM.scriptEditor;
    if (!toolbar || !textarea) return;

    toolbar.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-pacing-tag');
        if (!btn) return;
        e.preventDefault();

        const tag = btn.dataset.pacingTag;
        const val = btn.dataset.val || '0.5';

        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
        const selected = text.substring(start, end);

        let openTag = '';
        let closeTag = '';
        let defaultInner = '';

        if (tag === 'pause') {
            const pauseSnippet = `[pause ${val}] `;
            textarea.value = text.substring(0, start) + pauseSnippet + text.substring(end);
            const newPos = start + pauseSnippet.length;
            textarea.focus();
            textarea.setSelectionRange(newPos, newPos);
            updateStatsDisplay();
            scheduleAutosave();
            return;
        } else if (tag === 'emphasis') {
            openTag = '*';
            closeTag = '*';
            defaultInner = 'keyword';
        } else {
            // fast, slow, whisper, deep, shock, urgent, solemn, loud
            openTag = `[${tag}]`;
            closeTag = `[/${tag}]`;
            defaultInner = 'text';
        }

        const innerContent = selected || defaultInner;
        const insertion = openTag + innerContent + closeTag;

        textarea.value = text.substring(0, start) + insertion + text.substring(end);
        textarea.focus();

        if (selected) {
            // Move cursor after the closing tag
            const newPos = start + insertion.length;
            textarea.setSelectionRange(newPos, newPos);
        } else {
            // Highlight the default inner text so user can immediately type over it
            const selStart = start + openTag.length;
            const selEnd = selStart + defaultInner.length;
            textarea.setSelectionRange(selStart, selEnd);
        }

        updateStatsDisplay();
        scheduleAutosave();
    });
}

function setupCheatsheet() {
    if (!DOM.cheatsheetContent) return;

    const items = DOM.cheatsheetContent.querySelectorAll('p');
    items.forEach(p => {
        p.style.cursor = 'pointer';
        p.title = 'Bấm để chèn vào vị trí con trỏ';
        p.addEventListener('click', () => {
            const code = p.querySelector('code');
            if (code) {
                insertTagAtCursor(code.textContent);
            }
        });
    });
}

function insertTagAtCursor(tagText) {
    const textarea = DOM.scriptEditor;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;

    let insertion = tagText;
    let newCursorPos = start + insertion.length;

    // If tag is paired (like [slow]văn bản[/slow] or *từ quan trọng*)
    if (tagText.includes('văn bản')) {
        const selected = text.substring(start, end) || 'text';
        const openTag = tagText.split('văn bản')[0];
        const closeTag = tagText.split('văn bản')[1];
        insertion = openTag + selected + closeTag;
        newCursorPos = start + openTag.length + selected.length;
    } else if (tagText.startsWith('*') && tagText.endsWith('*')) {
        const selected = text.substring(start, end) || 'word';
        insertion = `*${selected}*`;
        newCursorPos = start + insertion.length;
    }

    textarea.value = text.substring(0, start) + insertion + text.substring(end);
    textarea.focus();
    textarea.setSelectionRange(newCursorPos, newCursorPos);

    updateStatsDisplay();
    scheduleAutosave();
}

// ==========================================
// 5. System Status & Diagnostics (R5.7)
// ==========================================

async function checkSystemStatus() {
    try {
        const res = await fetch('/api/status');
        if (!res.ok) throw new Error();
        const data = await res.json();

        let dotColor = 'var(--success)';
        let statusText = 'Hệ thống sẵn sàng';

        if (!data.ffmpeg) {
            dotColor = 'var(--danger)';
            statusText = '⚠️ Thiếu FFmpeg (Bấm xem cách cài)';
            DOM.systemStatus.onclick = () => {
                alert(
                    "CHƯA TÌM THẤY FFMPEG TRÊN HỆ THỐNG!\n\n" +
                    "FFmpeg là công cụ bắt buộc để ghép audio và chuẩn hóa âm lượng theo chuẩn EBU R128.\n\n" +
                    "Cách cài đặt tự động trên Windows:\n" +
                    "1. Mở PowerShell (hoặc Terminal)\n" +
                    "2. Chạy lệnh: winget install Gyan.FFmpeg\n" +
                    "3. Khởi động lại ứng dụng (chạy lại start.bat)"
                );
            };
            DOM.systemStatus.style.cursor = 'pointer';
        } else if (!data.has_gemini_key) {
            dotColor = 'var(--warning)';
            statusText = '⚠️ Thiếu GEMINI_API_KEY';
            DOM.systemStatus.onclick = () => {
                alert(
                    "CHƯA CẤU HÌNH KHÓA GEMINI_API_KEY!\n\n" +
                    "Các tính năng trợ lý viết kịch bản, thêm nhịp đọc và kiểm chứng nguồn cần khóa Gemini API miễn phí.\n\n" +
                    "Cách cấu hình:\n" +
                    "1. Truy cập https://aistudio.google.com và tạo khóa API miễn phí\n" +
                    "2. Mở file .env trong thư mục phần mềm\n" +
                    "3. Điền: GEMINI_API_KEY=khóa_vừa_tạo\n" +
                    "4. Khởi động lại ứng dụng (start.bat)"
                );
            };
            DOM.systemStatus.style.cursor = 'pointer';
        } else {
            statusText = `Hệ thống sẵn sàng (${data.gpu && data.gpu.has_gpu ? 'GPU' : 'CPU'})`;
            DOM.systemStatus.onclick = null;
            DOM.systemStatus.style.cursor = 'default';
        }

        DOM.systemStatus.innerHTML = `<span class="status-dot" style="background:${dotColor}"></span> ${statusText}`;
        DOM.systemStatus.title = `Model AI: ${data.config.model} | Giọng: ${data.config.voice}`;
    } catch (err) {
        DOM.systemStatus.innerHTML = `<span class="status-dot" style="background:var(--danger)"></span> Mất kết nối server`;
        DOM.systemStatus.onclick = null;
        DOM.systemStatus.style.cursor = 'default';
    }
}

// ==========================================
// 6. TTS Audio Preview & Voice Management
// ==========================================

let previewAbortController = null;

function cancelAudioPreview() {
    if (previewAbortController) {
        previewAbortController.abort();
        previewAbortController = null;
    }
    if (DOM.audioPlayer) {
        DOM.audioPlayer.pause();
    }
    resetPreviewState('⏹ Đã hủy đọc thử');
}

function resetPreviewState(statusMessage = null) {
    if (DOM.btnPreviewParagraph) {
        DOM.btnPreviewParagraph.disabled = false;
        DOM.btnPreviewParagraph.innerHTML = '▶ Đoạn này';
    }
    if (DOM.btnPreviewAll) {
        DOM.btnPreviewAll.disabled = false;
        DOM.btnPreviewAll.innerHTML = '▶ Toàn bài';
    }
    if (DOM.btnPreviewAudio) {
        DOM.btnPreviewAudio.disabled = false;
        DOM.btnPreviewAudio.textContent = '🔊 Đọc thử kịch bản';
    }
    if (DOM.btnCancelPreview) {
        DOM.btnCancelPreview.classList.add('hidden');
    }
    if (DOM.audioPreviewTag) {
        DOM.audioPreviewTag.classList.remove('generating');
    }
    if (statusMessage && DOM.audioPreviewLabel) {
        DOM.audioPreviewLabel.textContent = statusMessage;
    }
}

async function handleAudioPreview(scope = 'auto') {
    if (previewAbortController) {
        return; // Đang tạo âm thanh dở dang, chặn click lặp lại
    }

    const textarea = DOM.scriptEditor;
    const fullText = textarea.value.trim();
    if (!fullText) {
        alert('Vui lòng nhập nội dung kịch bản để nghe đọc thử nhịp điệu.');
        return;
    }

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    let targetText = "";
    let scopeTag = "Đoạn văn";

    if (scope === 'full') {
        targetText = fullText;
        scopeTag = "Toàn bài";
    } else if (scope === 'paragraph') {
        const beforeCursor = textarea.value.substring(0, start);
        const afterCursor = textarea.value.substring(start);
        const paraStart = beforeCursor.lastIndexOf('\n') + 1;
        const paraEndRel = afterCursor.indexOf('\n');
        const paraEnd = paraEndRel === -1 ? textarea.value.length : start + paraEndRel;

        targetText = textarea.value.substring(paraStart, paraEnd).trim();
        if (!targetText) {
            targetText = fullText.split('\n\n')[0].trim();
        }
        scopeTag = "Đoạn này";
    } else {
        // 'auto': if selection exists use it, otherwise paragraph around cursor
        if (start !== end) {
            targetText = textarea.value.substring(start, end).trim();
            scopeTag = "Đoạn chọn";
        } else {
            const beforeCursor = textarea.value.substring(0, start);
            const afterCursor = textarea.value.substring(start);
            const paraStart = beforeCursor.lastIndexOf('\n') + 1;
            const paraEndRel = afterCursor.indexOf('\n');
            const paraEnd = paraEndRel === -1 ? textarea.value.length : start + paraEndRel;

            targetText = textarea.value.substring(paraStart, paraEnd).trim();
            if (!targetText) {
                targetText = fullText.split('\n\n')[0].trim();
            }
            scopeTag = "Đoạn này";
        }
    }

    if (!targetText) {
        alert('Đoạn văn bản đang trống.');
        return;
    }

    // Hiển thị thanh Audition ngay lập tức với chỉ báo khởi tạo
    DOM.audioPreviewBar.classList.remove('hidden');
    if (DOM.audioPreviewTag) {
        DOM.audioPreviewTag.textContent = scopeTag;
        DOM.audioPreviewTag.classList.add('generating');
    }
    if (DOM.audioPreviewLabel) {
        DOM.audioPreviewLabel.textContent = `⏳ Đang khởi tạo & tạo âm thanh (${scopeTag})...`;
    }

    // Vô hiệu hóa các nút điều khiển để chống spam click nhiều lần
    if (DOM.btnPreviewParagraph) {
        DOM.btnPreviewParagraph.disabled = true;
        if (scope === 'paragraph' || (scope === 'auto' && scopeTag === 'Đoạn này')) {
            DOM.btnPreviewParagraph.innerHTML = '⏳ Đang tạo...';
        }
    }
    if (DOM.btnPreviewAll) {
        DOM.btnPreviewAll.disabled = true;
        if (scope === 'full') {
            DOM.btnPreviewAll.innerHTML = '⏳ Đang tạo...';
        }
    }
    if (DOM.btnPreviewAudio) {
        DOM.btnPreviewAudio.disabled = true;
        DOM.btnPreviewAudio.textContent = '⏳ Đang đọc...';
    }
    if (DOM.btnCancelPreview) {
        DOM.btnCancelPreview.classList.remove('hidden');
    }

    previewAbortController = new AbortController();

    try {
        const preset = DOM.presetSelector ? DOM.presetSelector.value : 'mystery';
        const res = await fetch('/api/tts/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: targetText,
                preset: preset,
                scope: scope
            }),
            signal: previewAbortController.signal
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Lỗi từ máy chủ TTS');
        }

        const data = await res.json();
        if (data.audio_url) {
            DOM.audioPreviewBar.classList.remove('hidden');
            if (DOM.audioPreviewTag) {
                DOM.audioPreviewTag.textContent = scopeTag;
                DOM.audioPreviewTag.classList.remove('generating');
            }
            DOM.audioPreviewLabel.textContent = `🔊 Đọc thử (${data.duration.toFixed(1)}s):`;
            DOM.audioPlayer.src = data.audio_url;
            DOM.audioPlayer.play().catch(e => console.log('Autoplay blocked:', e));
        }
    } catch (err) {
        if (err.name === 'AbortError') {
            if (DOM.audioPreviewLabel) DOM.audioPreviewLabel.textContent = '⏹ Đã hủy tạo âm thanh.';
        } else {
            alert('Lỗi nghe đọc thử: ' + err.message);
            if (DOM.audioPreviewLabel) DOM.audioPreviewLabel.textContent = '❌ Lỗi tạo âm thanh.';
        }
    } finally {
        previewAbortController = null;
        resetPreviewState();
    }
}

let selectedVoiceId = null;

async function openVoiceModal() {
    DOM.voiceModal.classList.remove('hidden');
    DOM.voiceOptionsList.innerHTML = '<div class="empty-state">Đang tải danh sách giọng đọc nam tiếng Anh...</div>';

    try {
        const res = await fetch('/api/tts/voices');
        if (!res.ok) throw new Error('Không thể tải danh sách giọng đọc');
        const data = await res.json();

        selectedVoiceId = data.current_voice || 'en-US-ChristopherNeural';
        DOM.voiceOptionsList.innerHTML = '';

        if (!data.voices || data.voices.length === 0) {
            DOM.voiceOptionsList.innerHTML = '<div class="empty-state">Không tìm thấy giọng đọc nào.</div>';
            return;
        }

        data.voices.forEach(v => {
            const item = document.createElement('div');
            item.className = 'voice-item';
            if (v.id === selectedVoiceId) {
                item.classList.add('selected');
            }

            item.innerHTML = `
                <input type="radio" name="voice_radio" value="${v.id}" ${v.id === selectedVoiceId ? 'checked' : ''}>
                <div class="voice-info">
                    <div class="voice-name">${escapeHtml(v.name)}</div>
                    <div class="voice-sub">${escapeHtml(v.locale)} • ${escapeHtml(v.id)}</div>
                </div>
            `;

            item.addEventListener('click', () => {
                selectedVoiceId = v.id;
                DOM.voiceOptionsList.querySelectorAll('.voice-item').forEach(el => el.classList.remove('selected'));
                item.classList.add('selected');
                item.querySelector('input').checked = true;
            });

            DOM.voiceOptionsList.appendChild(item);
        });
    } catch (err) {
        DOM.voiceOptionsList.innerHTML = `<div class="empty-state" style="color:var(--danger)">Lỗi: ${err.message}</div>`;
    }
}

function closeVoiceModal() {
    DOM.voiceModal.classList.add('hidden');
}

async function saveSelectedVoice() {
    if (!selectedVoiceId) return;

    DOM.btnSaveVoice.disabled = true;
    DOM.btnSaveVoice.textContent = 'Đang lưu...';

    try {
        const res = await fetch('/api/tts/lock-voice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ voice: selectedVoiceId })
        });
        if (!res.ok) throw new Error('Không thể lưu giọng đọc');

        closeVoiceModal();
        checkSystemStatus();
        alert(`Đã khóa giọng đọc: ${selectedVoiceId}`);
    } catch (err) {
        alert('Lỗi khóa giọng đọc: ' + err.message);
    } finally {
        DOM.btnSaveVoice.disabled = false;
        DOM.btnSaveVoice.textContent = 'Khóa giọng đọc này';
    }
}

// ==========================================
// 7. Export Pipeline & Modal Controls
// ==========================================

let exportPollTimer = null;

async function handleStartExport() {
    if (!state.currentProject) {
        alert('Vui lòng chọn hoặc tạo một dự án trước.');
        return;
    }

    const script = DOM.scriptEditor.value.trim();
    if (!script) {
        alert('Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi xuất.');
        return;
    }

    // Ensure latest changes are saved first
    await executeAutosave();

    // Check estimated duration and unverified claims for inline warnings in modal
    const { duration } = calculateStats(script);
    const claims = state.currentProject.claims || [];
    const unclearClaims = claims.filter(c => c.label === 'CHƯA RÕ');

    let warnings = [];
    if (duration < 60 || duration > 180) {
        warnings.push(`⚠️ Thời lượng ước tính: ${duration}s (khuyến nghị cho Shorts là 60–180s).`);
    }
    if (unclearClaims.length > 0) {
        warnings.push(`⚠️ Có ${unclearClaims.length} luận điểm chưa được chứng minh (nhãn "CHƯA RÕ").`);
    }

    // Open export modal into Pre-Export Audition Review state (R5.10)
    DOM.exportModal.classList.remove('hidden');
    if (DOM.exportPrecheckSection) DOM.exportPrecheckSection.classList.remove('hidden');
    DOM.exportProgressSection.classList.add('hidden');
    DOM.exportResultSection.classList.add('hidden');
    DOM.exportWarningBox.classList.add('hidden');

    // Reset Audition Player
    if (DOM.exportAuditionPlayer) {
        DOM.exportAuditionPlayer.pause();
        DOM.exportAuditionPlayer.style.display = 'none';
        DOM.exportAuditionPlayer.src = '';
    }
    if (DOM.exportAuditionStatus) DOM.exportAuditionStatus.textContent = 'Chưa nghe thử';
    if (DOM.exportAuditionDuration) DOM.exportAuditionDuration.textContent = '';

    if (DOM.exportPrecheckWarning) {
        if (warnings.length > 0) {
            DOM.exportPrecheckWarning.innerHTML = warnings.join('<br>');
            DOM.exportPrecheckWarning.classList.remove('hidden');
        } else {
            DOM.exportPrecheckWarning.classList.add('hidden');
        }
    }
}

async function handleModalAudition() {
    const script = DOM.scriptEditor.value.trim();
    if (!script) {
        alert('Kịch bản đang trống.');
        return;
    }

    DOM.btnModalPreviewAudio.disabled = true;
    DOM.btnModalPreviewAudio.textContent = '⏳ Đang tổng hợp audio đọc thử...';
    if (DOM.exportAuditionStatus) DOM.exportAuditionStatus.textContent = 'Đang xử lý nhịp điệu & Audio FX...';

    try {
        const preset = DOM.presetSelector ? DOM.presetSelector.value : 'mystery';
        const res = await fetch('/api/tts/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: script,
                preset: preset,
                scope: 'full'
            })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Lỗi đọc thử audio');
        }

        const data = await res.json();
        if (data.audio_url) {
            DOM.exportAuditionPlayer.src = data.audio_url;
            DOM.exportAuditionPlayer.style.display = 'block';
            DOM.exportAuditionPlayer.play().catch(e => console.log('Autoplay blocked:', e));
            if (DOM.exportAuditionDuration) DOM.exportAuditionDuration.textContent = `⏱️ ${data.duration.toFixed(1)}s`;
            if (DOM.exportAuditionStatus) DOM.exportAuditionStatus.innerHTML = '<span style="color:var(--success)">✓ Đã sẵn sàng phát</span>';
        }
    } catch (err) {
        alert('Lỗi đọc thử: ' + err.message);
        if (DOM.exportAuditionStatus) DOM.exportAuditionStatus.textContent = 'Lỗi đọc thử';
    } finally {
        DOM.btnModalPreviewAudio.disabled = false;
        DOM.btnModalPreviewAudio.textContent = '🔊 Đọc thử toàn bộ kịch bản';
    }
}

async function executeActualExport() {
    if (DOM.exportAuditionPlayer) {
        DOM.exportAuditionPlayer.pause();
    }

    if (DOM.exportPrecheckSection) DOM.exportPrecheckSection.classList.add('hidden');
    DOM.exportProgressSection.classList.remove('hidden');
    DOM.exportResultSection.classList.add('hidden');
    DOM.exportWarningBox.classList.add('hidden');

    DOM.exportStepLabel.textContent = 'Đang khởi động tiến trình xuất...';
    DOM.exportProgressBar.style.width = '5%';
    DOM.exportProgressBar.style.background = 'var(--accent)';
    DOM.exportProgressPercent.textContent = '5%';
    DOM.exportDurationInfo.textContent = '';

    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/export`, {
            method: 'POST'
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể bắt đầu xuất');
        }

        const data = await res.json();
        const jobId = data.job_id;

        // Poll export status
        pollExportProgress(state.currentProject.id, jobId);
    } catch (err) {
        DOM.exportStepLabel.textContent = 'Lỗi: ' + err.message;
        DOM.exportProgressBar.style.background = 'var(--danger)';
    }
}

function pollExportProgress(projectId, jobId) {
    clearInterval(exportPollTimer);

    exportPollTimer = setInterval(async () => {
        try {
            const res = await fetch(`/api/projects/${projectId}/export-status/${jobId}`);
            if (!res.ok) throw new Error('Mất kết nối với tiến trình xuất');
            const job = await res.json();

            // Update progress
            DOM.exportProgressBar.style.width = `${job.progress || 5}%`;
            DOM.exportProgressPercent.textContent = `${job.progress || 5}%`;
            DOM.exportStepLabel.textContent = job.step || 'Đang xử lý...';

            if (job.duration) {
                DOM.exportDurationInfo.textContent = `Thời lượng audio: ${job.duration.toFixed(1)}s`;
            }

            // Completed
            if (job.status === 'completed') {
                clearInterval(exportPollTimer);
                DOM.exportStepLabel.textContent = '🎉 Gói xuất đã sẵn sàng!';
                DOM.exportProgressBar.style.width = '100%';
                DOM.exportProgressPercent.textContent = '100%';

                // Setup download links
                DOM.btnDownloadNarration.href = `/api/projects/${projectId}/narration`;
                DOM.btnDownloadSubtitles.href = `/api/projects/${projectId}/subtitles`;
                DOM.btnDownloadSources.href = `/api/projects/${projectId}/sources`;

                DOM.exportResultSection.classList.remove('hidden');

                // Refresh sidebar projects
                renderProjectsList();
            }

            // Failed
            if (job.status === 'failed') {
                clearInterval(exportPollTimer);
                DOM.exportStepLabel.textContent = '❌ ' + (job.error || 'Quá trình xuất thất bại');
                DOM.exportProgressBar.style.background = 'var(--danger)';
            }
        } catch (err) {
            console.error('Polling error:', err);
        }
    }, 1000);
}

function closeExportModal() {
    clearInterval(exportPollTimer);
    if (DOM.exportAuditionPlayer) {
        DOM.exportAuditionPlayer.pause();
    }
    DOM.exportModal.classList.add('hidden');
}

// ==========================================
// 7.5. Export History Functions (R5.8, R5.9)
// ==========================================

async function openExportHistoryModal() {
    if (!state.currentProject) {
        alert('Vui lòng chọn hoặc tạo một dự án trước.');
        return;
    }

    DOM.exportHistoryModal.classList.remove('hidden');
    DOM.exportHistoryList.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 25px;">Đang tải lịch sử các bản audio...</div>';

    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/exports`);
        if (!res.ok) throw new Error('Không thể tải lịch sử xuất.');
        const data = await res.json();
        const exports = data.exports || [];

        if (exports.length === 0) {
            DOM.exportHistoryList.innerHTML = `
                <div style="text-align: center; color: var(--text-muted); padding: 30px;">
                    <div style="font-size: 2.2rem; margin-bottom: 8px;">📂</div>
                    <p style="font-weight: 500;">Dự án này chưa có bản audio nào được xuất.</p>
                    <small>Bấm "Xuất Audio & Phụ đề" để tạo và lưu trữ bản đầu tiên.</small>
                </div>
            `;
            return;
        }

        DOM.exportHistoryList.innerHTML = '';
        exports.forEach((exp) => {
            const card = document.createElement('div');
            card.className = 'history-card';
            
            const dateStr = exp.created_at ? new Date(exp.created_at).toLocaleString('vi-VN') : 'Không rõ thời gian';
            const durationStr = exp.duration ? `${exp.duration}s` : 'N/A';
            const presetStr = exp.pacing_preset ? exp.pacing_preset.toUpperCase() : 'MYSTERY';
            const previewText = exp.script_preview || 'Không có bản xem trước kịch bản';

            const audioUrl = exp.audio_url || `/api/projects/${state.currentProject.id}/exports/${exp.id}/audio`;
            const srtUrl = exp.subtitles_url || `/api/projects/${state.currentProject.id}/exports/${exp.id}/subtitles`;
            const sourcesUrl = exp.sources_url || `/api/projects/${state.currentProject.id}/exports/${exp.id}/sources`;

            card.innerHTML = `
                <div class="history-card-header">
                    <div class="history-title-group">
                        <span class="history-job-id">#${escapeHtml(exp.id)}</span>
                        <span class="history-time">🕒 ${escapeHtml(dateStr)}</span>
                    </div>
                    <div class="history-badges">
                        <span class="history-badge">⏱️ ${escapeHtml(durationStr)}</span>
                        <span class="history-badge" style="background: rgba(16, 185, 129, 0.15); color: var(--success);">🎵 ${escapeHtml(presetStr)}</span>
                    </div>
                </div>
                <div class="history-preview">"${escapeHtml(previewText)}"</div>
                <div class="history-actions">
                    <button class="btn-primary btn-play-history" style="font-size: 0.8rem; padding: 5px 12px; cursor: pointer;">
                        ▶️ Nghe audio này
                    </button>
                    <div class="history-download-links">
                        <a href="${audioUrl}" download class="history-link-btn" title="Tải file audio của job này">🎵 .mp3</a>
                        <a href="${srtUrl}" download class="history-link-btn" title="Tải file phụ đề SRT của job này">📝 .srt</a>
                        <a href="${sourcesUrl}" download class="history-link-btn" title="Tải file nguồn kiểm chứng của job này">🔗 sources.txt</a>
                    </div>
                </div>
            `;

            // Audio Playback isolated to this job
            const btnPlay = card.querySelector('.btn-play-history');
            if (btnPlay) {
                btnPlay.addEventListener('click', () => {
                    DOM.audioPreviewBar.classList.remove('hidden');
                    DOM.audioPreviewLabel.textContent = `Bản audio #${exp.id} (${durationStr}) - ${dateStr}`;
                    DOM.audioPlayer.src = audioUrl;
                    DOM.audioPlayer.play().catch(e => console.log('Autoplay blocked:', e));
                });
            }

            DOM.exportHistoryList.appendChild(card);
        });

    } catch (err) {
        DOM.exportHistoryList.innerHTML = `<div style="color: var(--danger); padding: 15px;">Lỗi: ${err.message}</div>`;
    }
}

function closeExportHistoryModal() {
    DOM.exportHistoryModal.classList.add('hidden');
}

// ==========================================
// Audio Enhancements FX (R2.12)
// ==========================================

async function openAudioFxModal() {
    DOM.audioFxModal.classList.remove('hidden');
    if (DOM.fxSaveStatus) DOM.fxSaveStatus.classList.add('hidden');
    try {
        const res = await fetch('/api/config/audio-enhancements');
        if (res.ok) {
            const data = await res.json();
            const enh = data.enhancements || {};
            if (DOM.fxCompression) DOM.fxCompression.checked = enh.compression !== false;
            if (DOM.fxMaleEq) DOM.fxMaleEq.checked = enh.male_eq !== false;
            if (DOM.fxDeesser) DOM.fxDeesser.checked = enh.deesser !== false;
            if (DOM.fxReverb) DOM.fxReverb.checked = enh.reverb !== false;
            if (DOM.fxLoudnorm) DOM.fxLoudnorm.checked = enh.loudnorm !== false;
        }
    } catch (err) {
        console.error('Lỗi tải cấu hình FX:', err);
    }
}

function closeAudioFxModal() {
    DOM.audioFxModal.classList.add('hidden');
}

async function saveAudioFxSettings() {
    const enhancements = {
        compression: DOM.fxCompression ? DOM.fxCompression.checked : true,
        male_eq: DOM.fxMaleEq ? DOM.fxMaleEq.checked : true,
        deesser: DOM.fxDeesser ? DOM.fxDeesser.checked : true,
        reverb: DOM.fxReverb ? DOM.fxReverb.checked : true,
        loudnorm: DOM.fxLoudnorm ? DOM.fxLoudnorm.checked : true
    };

    DOM.btnSaveAudioFx.disabled = true;
    DOM.btnSaveAudioFx.textContent = 'Đang lưu...';

    try {
        const res = await fetch('/api/config/audio-enhancements', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enhancements })
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể lưu cài đặt âm thanh');
        }
        if (DOM.fxSaveStatus) DOM.fxSaveStatus.classList.remove('hidden');
        setTimeout(() => {
            if (DOM.fxSaveStatus) DOM.fxSaveStatus.classList.add('hidden');
        }, 2500);
    } catch (err) {
        alert('Lỗi khi lưu cấu hình âm thanh: ' + err.message);
    } finally {
        DOM.btnSaveAudioFx.disabled = false;
        DOM.btnSaveAudioFx.textContent = 'Lưu cấu hình';
    }
}

// ==========================================
// Paragraph Takes & Multi-Take Selector (R2.11)
// ==========================================

let takesParagraphs = [];
let currentTakeParaIndex = 0;

function getScriptParagraphs() {
    const fullText = DOM.scriptEditor.value.trim();
    if (!fullText) return [];
    let paras = fullText.split(/\n\s*\n/).map(p => p.trim()).filter(p => p.length > 0);
    if (paras.length <= 1 && fullText.includes('\n')) {
        paras = fullText.split('\n').map(p => p.trim()).filter(p => p.length > 0);
    }
    return paras.length > 0 ? paras : [fullText];
}

async function openParagraphTakesModal() {
    if (!state.currentProject) {
        alert('Vui lòng chọn hoặc tạo một dự án trước.');
        return;
    }

    takesParagraphs = getScriptParagraphs();
    if (takesParagraphs.length === 0) {
        alert('Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi tạo bản thu.');
        return;
    }

    // Determine current paragraph at cursor
    const cursor = DOM.scriptEditor.selectionStart || 0;
    const textBefore = DOM.scriptEditor.value.substring(0, cursor);
    const beforeCount = (textBefore.match(/\n\s*\n/g) || []).length;
    currentTakeParaIndex = Math.min(beforeCount, takesParagraphs.length - 1);

    // Populate dropdown
    DOM.takesParagraphSelect.innerHTML = '';
    takesParagraphs.forEach((para, idx) => {
        const opt = document.createElement('option');
        opt.value = idx;
        const words = para.split(/\s+/).filter(Boolean).length;
        const excerpt = para.length > 30 ? para.substring(0, 30) + '...' : para;
        opt.textContent = `Đoạn ${idx + 1} (${words} từ): "${excerpt}"`;
        if (idx === currentTakeParaIndex) opt.selected = true;
        DOM.takesParagraphSelect.appendChild(opt);
    });

    updateTakesParaPreview();
    DOM.paragraphTakesModal.classList.remove('hidden');
    await loadParagraphTakes(currentTakeParaIndex);
}

function updateTakesParaPreview() {
    const paraText = takesParagraphs[currentTakeParaIndex] || '';
    DOM.takesParaPreview.value = paraText;
}

function closeParagraphTakesModal() {
    DOM.paragraphTakesModal.classList.add('hidden');
}

async function loadParagraphTakes(paraIndex) {
    DOM.paragraphTakesList.innerHTML = '<div style="text-align: center; color: var(--text-muted); padding: 16px;">Đang tải danh sách bản thu...</div>';

    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/paragraph-takes/${paraIndex}`);
        if (!res.ok) throw new Error('Không thể tải danh sách bản thu');
        const data = await res.json();
        const takes = data.takes || [];

        renderParagraphTakes(takes, paraIndex);
    } catch (err) {
        DOM.paragraphTakesList.innerHTML = `<div style="color: var(--danger); padding: 12px;">Lỗi: ${err.message}</div>`;
    }
}

function renderParagraphTakes(takes, paraIndex) {
    DOM.paragraphTakesList.innerHTML = '';
    if (takes.length === 0) {
        DOM.paragraphTakesList.innerHTML = `
            <div style="text-align: center; color: var(--text-muted); padding: 24px; background: var(--bg-surface); border: 1px dashed var(--border-color); border-radius: 6px;">
                Chưa có bản thu nào cho đoạn này.<br>
                Bấm <strong>"🎙️ Tạo Take mới cho đoạn này"</strong> để thu âm giọng đọc và lưu take (tối đa 4 bản).
            </div>
        `;
        return;
    }

    takes.forEach((t) => {
        const card = document.createElement('div');
        card.className = `take-card ${t.is_selected ? 'is-selected' : ''}`;

        const timeStr = t.created_at ? new Date(t.created_at).toLocaleTimeString() : '';

        card.innerHTML = `
            <div class="take-header">
                <span class="take-title">
                    Take #${t.take_number}
                    ${t.is_selected ? '<span class="take-badge-selected">★ Bản chính đang chọn</span>' : ''}
                </span>
                <span class="take-meta">⏱️ ${t.duration ? t.duration.toFixed(1) : 0}s &bull; ${timeStr}</span>
            </div>
            <div class="take-audio-wrapper">
                <audio controls preload="none" src="${t.audio_url}" style="width: 100%;"></audio>
            </div>
            <div class="take-actions">
                <button class="take-select-btn ${t.is_selected ? 'active' : ''}">
                    ${t.is_selected ? '✓ Đang chọn làm bản phát' : '⭐ Chọn Take này'}
                </button>
            </div>
        `;

        const selectBtn = card.querySelector('.take-select-btn');
        if (!t.is_selected) {
            selectBtn.addEventListener('click', async () => {
                await selectParagraphTake(paraIndex, t.id);
            });
        }

        DOM.paragraphTakesList.appendChild(card);
    });
}

async function generateNewTake() {
    if (!state.currentProject) return;
    const text = takesParagraphs[currentTakeParaIndex];
    if (!text) {
        alert('Đoạn văn bản đang trống.');
        return;
    }

    DOM.btnGenerateNewTake.disabled = true;
    DOM.takesLoading.classList.remove('hidden');

    try {
        const preset = DOM.presetSelector ? DOM.presetSelector.value : 'mystery';
        const res = await fetch('/api/tts/paragraph-take', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: state.currentProject.id,
                paragraph_index: currentTakeParaIndex,
                text: text,
                preset: preset
            })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể tạo bản thu mới.');
        }

        const data = await res.json();
        renderParagraphTakes(data.takes, currentTakeParaIndex);
    } catch (err) {
        alert('Lỗi tạo take mới: ' + err.message);
    } finally {
        DOM.btnGenerateNewTake.disabled = false;
        DOM.takesLoading.classList.add('hidden');
    }
}

async function selectParagraphTake(paraIndex, takeId) {
    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/paragraph-takes/${paraIndex}/select?take_id=${takeId}`, {
            method: 'PUT'
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể chọn Take.');
        }
        const data = await res.json();
        renderParagraphTakes(data.takes, paraIndex);
    } catch (err) {
        alert('Lỗi chọn take: ' + err.message);
    }
}

// ==========================================
// 8. Gemini Writing Assistant Actions (R3)
// ==========================================

async function handleSuggestNext() {
    const script = DOM.scriptEditor.value.trim();
    if (!script) {
        alert('Kịch bản đang trống. Vui lòng nhập nội dung hiện tại để Gemini gợi ý đoạn tiếp theo.');
        return;
    }

    const notes = DOM.aiNotes ? DOM.aiNotes.value.trim() : '';
    const origText = DOM.btnSuggestNext.innerHTML;
    DOM.btnSuggestNext.disabled = true;
    DOM.btnSuggestNext.innerHTML = '<strong>⏳ Đang suy nghĩ...</strong><small>Gemini đang tạo 3 ý tưởng nối tiếp</small>';

    try {
        const res = await fetch('/api/gemini/suggest-next', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ script, notes })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể tạo gợi ý từ Gemini');
        }

        const data = await res.json();
        const suggestions = data.suggestions || [];

        DOM.suggestionsList.innerHTML = '';
        suggestions.forEach((text, idx) => {
            const card = document.createElement('div');
            card.className = 'btn-card';
            card.style.textAlign = 'left';
            card.style.cursor = 'pointer';
            card.style.border = '1px solid var(--border-color)';
            card.innerHTML = `
                <div style="font-weight: 600; color: var(--accent); margin-bottom: 6px;">Lựa chọn ${idx + 1}:</div>
                <div style="font-size: 0.9rem; line-height: 1.5; color: var(--text-primary); margin-bottom: 8px;">${escapeHtml(text)}</div>
                <button class="btn-primary" style="font-size: 0.8rem; padding: 4px 10px;">➕ Chèn đoạn này</button>
            `;

            card.addEventListener('click', () => {
                const current = DOM.scriptEditor.value.trim();
                DOM.scriptEditor.value = current ? `${current}\n\n${text}` : text;
                updateStatsDisplay();
                scheduleAutosave();
                DOM.suggestionsModal.classList.add('hidden');
            });

            DOM.suggestionsList.appendChild(card);
        });

        DOM.suggestionsModal.classList.remove('hidden');
    } catch (err) {
        alert('Lỗi gợi ý: ' + err.message);
    } finally {
        DOM.btnSuggestNext.disabled = false;
        DOM.btnSuggestNext.innerHTML = origText;
    }
}

async function handleRewriteScript() {
    const script = DOM.scriptEditor.value.trim();
    if (!script) {
        alert('Kịch bản đang trống. Vui lòng nhập nội dung trước khi yêu cầu viết lại.');
        return;
    }

    const notes = DOM.aiNotes ? DOM.aiNotes.value.trim() : '';
    const targetDuration = state.currentProject ? state.currentProject.target_duration : 90;
    const origText = DOM.btnRewriteScript.innerHTML;
    DOM.btnRewriteScript.disabled = true;
    DOM.btnRewriteScript.innerHTML = '<strong>⏳ Đang viết lại...</strong><small>Đang tối ưu cấu trúc và nhịp kể</small>';

    try {
        const res = await fetch('/api/gemini/rewrite', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ script, notes, target_duration: targetDuration })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể viết lại kịch bản');
        }

        const data = await res.json();
        DOM.rewriteOriginal.value = data.original || script;
        DOM.rewriteResult.value = data.rewritten || '';

        DOM.rewriteModal.classList.remove('hidden');
    } catch (err) {
        alert('Lỗi viết lại: ' + err.message);
    } finally {
        DOM.btnRewriteScript.disabled = false;
        DOM.btnRewriteScript.innerHTML = origText;
    }
}

function handleApplyRewrite() {
    const rewritten = DOM.rewriteResult.value.trim();
    if (rewritten) {
        DOM.scriptEditor.value = rewritten;
        updateStatsDisplay();
        scheduleAutosave();
    }
    DOM.rewriteModal.classList.add('hidden');
}

function handleOpenOutlineModal() {
    const sel = DOM.scriptEditor.value.substring(DOM.scriptEditor.selectionStart, DOM.scriptEditor.selectionEnd).trim();
    DOM.outlineTopic.value = sel || '';
    DOM.outlineLoading.classList.add('hidden');
    DOM.outlineResultSection.classList.add('hidden');
    DOM.btnApplyOutline.classList.add('hidden');
    DOM.outlineModal.classList.remove('hidden');
}

async function handleGenerateOutline() {
    const topic = DOM.outlineTopic.value.trim();
    if (!topic) {
        alert('Vui lòng nhập chủ đề hoặc sự thật cần tạo kịch bản.');
        return;
    }

    const notes = DOM.aiNotes ? DOM.aiNotes.value.trim() : '';
    const duration = parseInt(DOM.outlineDuration.value) || 90;

    DOM.outlineLoading.classList.remove('hidden');
    DOM.outlineResultSection.classList.add('hidden');
    DOM.btnApplyOutline.classList.add('hidden');
    DOM.btnGenerateOutline.disabled = true;

    try {
        const res = await fetch('/api/gemini/outline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, notes, target_duration: duration })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể dựng khung kịch bản');
        }

        const data = await res.json();
        DOM.outlineResult.value = data.draft || '';
        DOM.outlineResultSection.classList.remove('hidden');
        DOM.btnApplyOutline.classList.remove('hidden');
    } catch (err) {
        alert('Lỗi tạo khung: ' + err.message);
    } finally {
        DOM.outlineLoading.classList.add('hidden');
        DOM.btnGenerateOutline.disabled = false;
    }
}

function handleApplyOutline() {
    const draft = DOM.outlineResult.value.trim();
    if (draft) {
        const proceed = DOM.scriptEditor.value.trim() === '' || confirm('Thay thế nội dung kịch bản hiện tại bằng kịch bản vừa dựng?');
        if (proceed) {
            DOM.scriptEditor.value = draft;
            updateStatsDisplay();
            scheduleAutosave();
        }
    }
    DOM.outlineModal.classList.add('hidden');
}

async function handleAutoPace() {
    const script = DOM.scriptEditor.value.trim();
    if (!script) {
        alert('Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi thêm nhịp.');
        return;
    }

    const origText = DOM.btnAutoPace.innerHTML;
    DOM.btnAutoPace.disabled = true;
    DOM.btnAutoPace.innerHTML = '⚡ Đang phân tích nhịp...';

    try {
        const res = await fetch('/api/gemini/auto-pace', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ script })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể tự động thêm nhịp điệu');
        }

        const data = await res.json();
        DOM.autoPaceOriginal.value = data.original || script;
        DOM.autoPaceResult.value = data.paced || '';

        DOM.autoPaceModal.classList.remove('hidden');
    } catch (err) {
        alert('Lỗi thêm nhịp điệu: ' + err.message);
    } finally {
        DOM.btnAutoPace.disabled = false;
        DOM.btnAutoPace.innerHTML = origText;
    }
}

function handleApplyAutoPace() {
    const paced = DOM.autoPaceResult.value.trim();
    if (paced) {
        DOM.scriptEditor.value = paced;
        updateStatsDisplay();
        scheduleAutosave();
    }
    DOM.autoPaceModal.classList.add('hidden');
}

// ==========================================
// 8.5. Fact Checking Actions (R4)
// ==========================================

function renderClaimsList(claims) {
    if (!DOM.claimsList) return;
    DOM.claimsList.innerHTML = '';

    if (!claims || claims.length === 0) {
        DOM.claimsList.innerHTML = '<p class="empty-hint">Bấm "Bóc tách & Kiểm chứng" để phân tích các luận điểm và nguồn tài liệu tham khảo.</p>';
        if (DOM.factcheckDisclaimer) DOM.factcheckDisclaimer.classList.add('hidden');
        return;
    }

    if (DOM.factcheckDisclaimer) DOM.factcheckDisclaimer.classList.remove('hidden');

    claims.forEach((claim, idx) => {
        const isProven = claim.label === 'ĐÃ CHỨNG MINH';
        const card = document.createElement('div');
        card.className = `claim-card ${isProven ? 'status-proven' : 'status-unclear'}`;

        const urlsHtml = (claim.urls && claim.urls.length > 0)
            ? claim.urls.map(u => `<a class="claim-url-link" href="${escapeHtml(u)}" target="_blank" rel="noopener noreferrer">🔗 ${escapeHtml(u)}</a>`).join('')
            : '<span style="color:var(--text-muted); font-style:italic;">Chưa có link nguồn tài liệu</span>';

        card.innerHTML = `
            <div class="claim-header">
                <span class="claim-badge ${isProven ? 'badge-proven' : 'badge-unclear'}">${escapeHtml(claim.label)}</span>
                <select class="claim-label-select" title="Ghi đè nhãn thủ công (R4.7)">
                    <option value="ĐÃ CHỨNG MINH" ${isProven ? 'selected' : ''}>ĐÃ CHỨNG MINH</option>
                    <option value="CHƯA RÕ" ${!isProven ? 'selected' : ''}>CHƯA RÕ</option>
                </select>
            </div>
            <div class="claim-text">${escapeHtml(claim.text || '')}</div>
            <div class="claim-sentence-ref" title="Bấm để tô sáng câu này trong kịch bản">
                🔍 Trích: "${escapeHtml(claim.sentence || '')}"
            </div>
            <div class="claim-evidence">
                💡 ${escapeHtml(claim.evidence || '')}
            </div>
            <div class="claim-urls-section">
                <div style="font-weight: 500; color: var(--text-muted); margin-bottom: 2px;">Nguồn kiểm chứng:</div>
                <div class="claim-urls-list">${urlsHtml}</div>
                <div style="margin-top: 6px; display: flex; gap: 4px;">
                    <input type="text" class="input-new-url" placeholder="Thêm link nguồn (https://...)" style="flex: 1; font-size: 0.75rem; padding: 3px 6px; background: var(--bg-surface); border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 4px;">
                    <button class="btn-secondary btn-add-url" style="font-size: 0.75rem; padding: 2px 8px;">+ Thêm</button>
                </div>
            </div>
            ${!isProven ? `<button class="btn-rewrite-safe" data-id="${claim.id}">🛡️ Sửa câu này cho an toàn</button>` : ''}
        `;

        // Click to highlight sentence in scriptEditor (R4.5)
        const refSentence = card.querySelector('.claim-sentence-ref');
        if (refSentence) {
            refSentence.addEventListener('click', () => {
                highlightSentenceInEditor(claim.sentence);
            });
        }

        // Manual label override (R4.7)
        const labelSelect = card.querySelector('.claim-label-select');
        if (labelSelect) {
            labelSelect.addEventListener('change', () => {
                claim.label = labelSelect.value;
                saveProjectClaims();
                renderClaimsList(state.currentProject.claims);
            });
        }

        // Add custom URL (R4.7)
        const inputUrl = card.querySelector('.input-new-url');
        const btnAddUrl = card.querySelector('.btn-add-url');
        if (btnAddUrl && inputUrl) {
            btnAddUrl.addEventListener('click', () => {
                const val = inputUrl.value.trim();
                if (val) {
                    if (!claim.urls) claim.urls = [];
                    claim.urls.push(val);
                    inputUrl.value = '';
                    saveProjectClaims();
                    renderClaimsList(state.currentProject.claims);
                }
            });
        }

        // Safe rewrite button (R4.6)
        const btnSafe = card.querySelector('.btn-rewrite-safe');
        if (btnSafe) {
            btnSafe.addEventListener('click', () => {
                handleSafeRewrite(claim);
            });
        }

        DOM.claimsList.appendChild(card);
    });
}

function highlightSentenceInEditor(sentence) {
    if (!sentence || !DOM.scriptEditor) return;
    const text = DOM.scriptEditor.value;
    const cleanSentence = sentence.trim();
    let idx = text.indexOf(cleanSentence);

    // If exact match not found (e.g. markup tags inside), search by key words
    if (idx === -1) {
        const words = cleanSentence.split(/\s+/).filter(w => w.length > 3);
        if (words.length > 0) {
            idx = text.indexOf(words[0]);
        }
    }

    if (idx !== -1) {
        DOM.scriptEditor.focus();
        DOM.scriptEditor.setSelectionRange(idx, idx + cleanSentence.length);
        const linesBefore = text.substring(0, idx).split('\n').length;
        const lineHeight = 20;
        DOM.scriptEditor.scrollTop = Math.max(0, (linesBefore - 2) * lineHeight);
    }
}

async function saveProjectClaims() {
    if (!state.currentProject) return;
    try {
        await fetch(`/api/projects/${state.currentProject.id}/claims`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ claims: state.currentProject.claims || [] })
        });
    } catch (err) {
        console.error('Error saving claims:', err);
    }
}

async function handleCheckFacts() {
    if (!state.currentProject) {
        alert('Vui lòng chọn hoặc tạo dự án trước khi kiểm chứng.');
        return;
    }

    const script = DOM.scriptEditor.value.trim();
    if (!script) {
        alert('Kịch bản đang trống. Vui lòng nhập nội dung trước khi kiểm chứng.');
        return;
    }

    // Ensure autosave first
    await executeAutosave();

    DOM.btnCheckFacts.disabled = true;
    DOM.btnCheckFacts.innerHTML = '⏳ Đang kiểm chứng...';
    if (DOM.factcheckLoading) DOM.factcheckLoading.classList.remove('hidden');

    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/factcheck`, {
            method: 'POST'
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể kiểm chứng kịch bản');
        }

        const data = await res.json();
        state.currentProject.claims = data.claims || [];
        renderClaimsList(state.currentProject.claims);
    } catch (err) {
        alert('Lỗi kiểm chứng: ' + err.message);
    } finally {
        DOM.btnCheckFacts.disabled = false;
        DOM.btnCheckFacts.innerHTML = '🔍 Bóc tách & Kiểm chứng';
        if (DOM.factcheckLoading) DOM.factcheckLoading.classList.add('hidden');
    }
}

let currentSafeClaim = null;

async function handleSafeRewrite(claim) {
    currentSafeClaim = claim;
    DOM.safeOrigSentence.value = claim.sentence || claim.text;
    DOM.safeNewSentence.value = 'Đang phân tích câu an toàn...';
    DOM.btnApplySafeRewrite.disabled = true;
    DOM.safeRewriteModal.classList.remove('hidden');

    try {
        const res = await fetch('/api/factcheck/rewrite-sentence', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                claim_text: claim.text,
                sentence: claim.sentence || claim.text,
                reason: claim.evidence || ''
            })
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể viết lại câu an toàn');
        }

        const data = await res.json();
        DOM.safeNewSentence.value = data.safe_sentence || '';
        DOM.btnApplySafeRewrite.disabled = false;
    } catch (err) {
        DOM.safeNewSentence.value = 'Lỗi: ' + err.message;
    }
}

function handleApplySafeRewrite() {
    if (!currentSafeClaim) return;
    const oldSentence = DOM.safeOrigSentence.value.trim();
    const newSentence = DOM.safeNewSentence.value.trim();

    if (newSentence && oldSentence) {
        const editorText = DOM.scriptEditor.value;
        if (editorText.includes(oldSentence)) {
            DOM.scriptEditor.value = editorText.replace(oldSentence, newSentence);
        } else {
            DOM.scriptEditor.value += `\n\n${newSentence}`;
        }
        currentSafeClaim.sentence = newSentence;
        saveProjectClaims();
        updateStatsDisplay();
        scheduleAutosave();
        renderClaimsList(state.currentProject.claims);
    }
    DOM.safeRewriteModal.classList.add('hidden');
}

// ==========================================
// 9. Utility Functions
// ==========================================

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Tab Switching
function setupTabs() {
    DOM.tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            DOM.tabButtons.forEach(b => b.classList.remove('active'));
            DOM.tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetEl = document.getElementById(targetTab);
            if (targetEl) targetEl.classList.add('active');
        });
    });
}

// Phase 15: Workflow steps, collapsible sidebar/panel, pacing "more" toggle.
// Steps reuse the existing handlers (no new backend calls): preview clicks
// #btn-preview-audio, factcheck opens the fact-check tab, export clicks
// #btn-export-project.
function setupWorkflowUI() {
    const layout = document.querySelector('.app-layout');

    const sidebarToggle = document.getElementById('btn-toggle-sidebar');
    if (sidebarToggle && layout) {
        sidebarToggle.addEventListener('click', () => layout.classList.toggle('sidebar-collapsed'));
    }

    const panelToggle = document.getElementById('btn-toggle-panel');
    if (panelToggle && layout) {
        panelToggle.addEventListener('click', () => layout.classList.toggle('panel-collapsed'));
    }

    const moreBtn = document.getElementById('btn-pacing-more');
    const extra = document.querySelector('.pacing-extra');
    if (moreBtn && extra) {
        moreBtn.addEventListener('click', () => {
            const hidden = extra.classList.toggle('hidden');
            moreBtn.textContent = hidden ? '＋ Thêm nhịp ▾' : '－ Thu gọn ▴';
        });
    }

    document.querySelectorAll('.workflow-step').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.workflow-step').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const step = btn.getAttribute('data-step');
            if (step === 'preview') {
                if (DOM.btnPreviewAudio) DOM.btnPreviewAudio.click();
            } else if (step === 'factcheck') {
                if (layout) layout.classList.remove('panel-collapsed');
                const tab = document.querySelector('.tab-btn[data-tab="factcheck-tab"]');
                if (tab) tab.click();
            } else if (step === 'export') {
                if (DOM.btnExportProject) DOM.btnExportProject.click();
            }
        });
    });
}

// ==========================================
// 7. Initialization
// ==========================================

async function init() {
    setupTabs();
    setupCheatsheet();
    setupQuickPacingToolbar();
    setupWorkflowUI();

    // Event Listeners
    DOM.btnNewProject.addEventListener('click', createNewProject);
    DOM.btnRandomLength.addEventListener('click', randomTargetDuration);

    // Audio Menu Dropdown Toggle
    const audioMenuToggle = document.getElementById('btn-audio-menu-toggle');
    const audioMenuDropdown = document.getElementById('audio-menu-dropdown');
    if (audioMenuToggle && audioMenuDropdown) {
        audioMenuToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            audioMenuDropdown.classList.toggle('hidden');
        });

        audioMenuDropdown.addEventListener('click', (e) => {
            const btn = e.target.closest('button');
            if (btn && btn.id !== 'btn-audio-menu-toggle') {
                audioMenuDropdown.classList.add('hidden');
            }
        });

        document.addEventListener('click', (e) => {
            if (!audioMenuDropdown.contains(e.target) && !audioMenuToggle.contains(e.target)) {
                audioMenuDropdown.classList.add('hidden');
            }
        });
    }

    if (DOM.btnPreviewAudio) {
        DOM.btnPreviewAudio.addEventListener('click', () => handleAudioPreview('auto'));
    }
    if (DOM.btnPreviewParagraph) {
        DOM.btnPreviewParagraph.addEventListener('click', () => handleAudioPreview('paragraph'));
    }
    if (DOM.btnPreviewAll) {
        DOM.btnPreviewAll.addEventListener('click', () => handleAudioPreview('full'));
    }
    if (DOM.btnCancelPreview) {
        DOM.btnCancelPreview.addEventListener('click', cancelAudioPreview);
    }
    if (DOM.btnCloseAudio) {
        DOM.btnCloseAudio.addEventListener('click', () => {
            cancelAudioPreview();
            DOM.audioPreviewBar.classList.add('hidden');
        });
    }

    if (DOM.btnSelectVoice) {
        DOM.btnSelectVoice.addEventListener('click', openVoiceModal);
    }
    if (DOM.btnCloseVoiceModal) {
        DOM.btnCloseVoiceModal.addEventListener('click', closeVoiceModal);
    }
    if (DOM.btnCancelVoice) {
        DOM.btnCancelVoice.addEventListener('click', closeVoiceModal);
    }
    if (DOM.btnSaveVoice) {
        DOM.btnSaveVoice.addEventListener('click', saveSelectedVoice);
    }

    if (DOM.btnExportProject) {
        DOM.btnExportProject.addEventListener('click', handleStartExport);
    }
    if (DOM.btnModalPreviewAudio) {
        DOM.btnModalPreviewAudio.addEventListener('click', handleModalAudition);
    }
    if (DOM.btnConfirmStartExport) {
        DOM.btnConfirmStartExport.addEventListener('click', executeActualExport);
    }
    if (DOM.btnCancelPreExport) {
        DOM.btnCancelPreExport.addEventListener('click', closeExportModal);
    }
    if (DOM.btnCloseExportModal) {
        DOM.btnCloseExportModal.addEventListener('click', closeExportModal);
    }
    if (DOM.btnCloseExport) {
        DOM.btnCloseExport.addEventListener('click', closeExportModal);
    }

    // Export History Event Listeners (R5.8, R5.9)
    if (DOM.btnExportHistory) {
        DOM.btnExportHistory.addEventListener('click', openExportHistoryModal);
    }
    if (DOM.btnCloseHistoryModal) {
        DOM.btnCloseHistoryModal.addEventListener('click', closeExportHistoryModal);
    }
    if (DOM.btnCloseHistory) {
        DOM.btnCloseHistory.addEventListener('click', closeExportHistoryModal);
    }
    if (DOM.btnViewHistoryFromModal) {
        DOM.btnViewHistoryFromModal.addEventListener('click', () => {
            closeExportModal();
            openExportHistoryModal();
        });
    }

    // Audio FX Event Listeners (R2.12)
    if (DOM.btnAudioFx) {
        DOM.btnAudioFx.addEventListener('click', openAudioFxModal);
    }
    if (DOM.btnCloseAudioFxModal) {
        DOM.btnCloseAudioFxModal.addEventListener('click', closeAudioFxModal);
    }
    if (DOM.btnCloseAudioFx) {
        DOM.btnCloseAudioFx.addEventListener('click', closeAudioFxModal);
    }
    if (DOM.btnSaveAudioFx) {
        DOM.btnSaveAudioFx.addEventListener('click', saveAudioFxSettings);
    }

    // Paragraph Takes Event Listeners (R2.11)
    if (DOM.btnParagraphTakes) {
        DOM.btnParagraphTakes.addEventListener('click', openParagraphTakesModal);
    }
    if (DOM.btnCloseTakesModal) {
        DOM.btnCloseTakesModal.addEventListener('click', closeParagraphTakesModal);
    }
    if (DOM.btnCloseTakes) {
        DOM.btnCloseTakes.addEventListener('click', closeParagraphTakesModal);
    }
    if (DOM.takesParagraphSelect) {
        DOM.takesParagraphSelect.addEventListener('change', async (e) => {
            currentTakeParaIndex = parseInt(e.target.value, 10) || 0;
            updateTakesParaPreview();
            await loadParagraphTakes(currentTakeParaIndex);
        });
    }
    if (DOM.btnGenerateNewTake) {
        DOM.btnGenerateNewTake.addEventListener('click', generateNewTake);
    }

    // AI Assistant Event Listeners (R3)
    if (DOM.btnSuggestNext) {
        DOM.btnSuggestNext.addEventListener('click', handleSuggestNext);
    }
    if (DOM.btnCloseSuggestionsModal) {
        DOM.btnCloseSuggestionsModal.addEventListener('click', () => DOM.suggestionsModal.classList.add('hidden'));
    }
    if (DOM.btnCancelSuggestions) {
        DOM.btnCancelSuggestions.addEventListener('click', () => DOM.suggestionsModal.classList.add('hidden'));
    }

    if (DOM.btnRewriteScript) {
        DOM.btnRewriteScript.addEventListener('click', handleRewriteScript);
    }
    if (DOM.btnCloseRewriteModal) {
        DOM.btnCloseRewriteModal.addEventListener('click', () => DOM.rewriteModal.classList.add('hidden'));
    }
    if (DOM.btnCancelRewrite) {
        DOM.btnCancelRewrite.addEventListener('click', () => DOM.rewriteModal.classList.add('hidden'));
    }
    if (DOM.btnApplyRewrite) {
        DOM.btnApplyRewrite.addEventListener('click', handleApplyRewrite);
    }

    if (DOM.btnOutlineDraft) {
        DOM.btnOutlineDraft.addEventListener('click', handleOpenOutlineModal);
    }
    if (DOM.btnGenerateOutline) {
        DOM.btnGenerateOutline.addEventListener('click', handleGenerateOutline);
    }
    if (DOM.btnApplyOutline) {
        DOM.btnApplyOutline.addEventListener('click', handleApplyOutline);
    }
    if (DOM.btnCloseOutlineModal) {
        DOM.btnCloseOutlineModal.addEventListener('click', () => DOM.outlineModal.classList.add('hidden'));
    }
    if (DOM.btnCancelOutline) {
        DOM.btnCancelOutline.addEventListener('click', () => DOM.outlineModal.classList.add('hidden'));
    }

    if (DOM.btnAutoPace) {
        DOM.btnAutoPace.addEventListener('click', handleAutoPace);
    }
    if (DOM.btnCloseAutoPaceModal) {
        DOM.btnCloseAutoPaceModal.addEventListener('click', () => DOM.autoPaceModal.classList.add('hidden'));
    }
    if (DOM.btnCancelAutoPace) {
        DOM.btnCancelAutoPace.addEventListener('click', () => DOM.autoPaceModal.classList.add('hidden'));
    }
    if (DOM.btnApplyAutoPace) {
        DOM.btnApplyAutoPace.addEventListener('click', handleApplyAutoPace);
    }

    // Fact Check Event Listeners (R4)
    if (DOM.btnCheckFacts) {
        DOM.btnCheckFacts.addEventListener('click', handleCheckFacts);
    }
    if (DOM.btnCloseSafeRewrite) {
        DOM.btnCloseSafeRewrite.addEventListener('click', () => DOM.safeRewriteModal.classList.add('hidden'));
    }
    if (DOM.btnCancelSafeRewrite) {
        DOM.btnCancelSafeRewrite.addEventListener('click', () => DOM.safeRewriteModal.classList.add('hidden'));
    }
    if (DOM.btnApplySafeRewrite) {
        DOM.btnApplySafeRewrite.addEventListener('click', handleApplySafeRewrite);
    }

    if (DOM.presetSelector) {
        DOM.presetSelector.addEventListener('change', () => {
            if (state.currentProject) {
                state.currentProject.pacing_preset = DOM.presetSelector.value;
                scheduleAutosave();
            }
        });
    }

    DOM.scriptEditor.addEventListener('input', () => {
        updateStatsDisplay();
        scheduleAutosave();
    });

    if (DOM.btnEditTitle) {
        DOM.btnEditTitle.addEventListener('click', () => {
            DOM.projectTitleInput.focus();
            DOM.projectTitleInput.select();
        });
    }

    DOM.projectTitleInput.addEventListener('input', () => {
        scheduleAutosave();
    });

    DOM.projectTitleInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            DOM.projectTitleInput.blur();
        }
    });

    DOM.projectTitleInput.addEventListener('blur', async () => {
        if (state.currentProject) {
            clearTimeout(state.autosaveTimer);
            await executeAutosave();
        }
    });

    // Check system status
    checkSystemStatus();

    // Initial project load
    const projects = await fetchProjects();
    if (projects.length > 0) {
        await loadProject(projects[0].id);
    } else {
        await createNewProject();
    }
}

document.addEventListener('DOMContentLoaded', init);
