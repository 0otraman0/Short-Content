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
    audioPlayer: document.getElementById('audio-player'),
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
                <button class="btn-icon btn-dup" data-id="${proj.id}" title="Nhân bản">📋</button>
                <button class="btn-icon btn-del" data-id="${proj.id}" title="Xóa">🗑️</button>
            </div>
        `;

        // Click to open
        item.querySelector('.project-info').addEventListener('click', () => {
            loadProject(proj.id);
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
// 4. Interactive Cheatsheet Insertion
// ==========================================

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

async function handleAudioPreview() {
    const textarea = DOM.scriptEditor;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;

    let targetText = "";
    if (start !== end) {
        // Highlighted text
        targetText = textarea.value.substring(start, end).trim();
    } else {
        // Paragraph around cursor or full text if short
        const fullText = textarea.value.trim();
        if (!fullText) {
            alert('Vui lòng nhập hoặc bôi đen một đoạn kịch bản cần nghe thử.');
            return;
        }

        // Find current paragraph around cursor
        const beforeCursor = textarea.value.substring(0, start);
        const afterCursor = textarea.value.substring(start);
        const paraStart = beforeCursor.lastIndexOf('\n') + 1;
        const paraEndRel = afterCursor.indexOf('\n');
        const paraEnd = paraEndRel === -1 ? textarea.value.length : start + paraEndRel;

        targetText = textarea.value.substring(paraStart, paraEnd).trim();
        if (!targetText) {
            targetText = fullText.split('\n\n')[0].trim();
        }
    }

    if (!targetText) {
        alert('Vui lòng bôi đen một đoạn văn bản để nghe thử.');
        return;
    }

    const originalBtnText = DOM.btnPreviewAudio.textContent;
    DOM.btnPreviewAudio.disabled = true;
    DOM.btnPreviewAudio.textContent = '⏳ Đang tổng hợp...';

    try {
        const preset = DOM.presetSelector ? DOM.presetSelector.value : 'mystery';
        const res = await fetch('/api/tts/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: targetText,
                preset: preset
            })
        });

        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || 'Lỗi từ máy chủ TTS');
        }

        const data = await res.json();
        if (data.audio_url) {
            DOM.audioPreviewBar.classList.remove('hidden');
            DOM.audioPreviewLabel.textContent = `🔊 Nghe thử (${data.duration.toFixed(1)}s):`;
            DOM.audioPlayer.src = data.audio_url;
            DOM.audioPlayer.play().catch(e => console.log('Autoplay blocked:', e));
        }
    } catch (err) {
        alert('Lỗi nghe thử: ' + err.message);
    } finally {
        DOM.btnPreviewAudio.disabled = false;
        DOM.btnPreviewAudio.textContent = originalBtnText;
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

    // Check estimated duration
    const { duration } = calculateStats(script);
    if (duration < 60 || duration > 180) {
        const proceed = confirm(
            `Thời lượng kịch bản ước tính là ${duration}s (khuyến nghị cho YouTube Shorts là từ 60 đến 180 giây).\n\nBạn có muốn tiếp tục xuất gói tài nguyên không?`
        );
        if (!proceed) return;
    }

    // Safety check for unverified claims (R4.8)
    const claims = state.currentProject.claims || [];
    const unclearClaims = claims.filter(c => c.label === 'CHƯA RÕ');
    if (unclearClaims.length > 0) {
        const proceedSafety = confirm(
            `⚠️ CẢNH BÁO AN TOÀN KIỂM CHỨNG (R4.8):\n\n` +
            `Dự án hiện có ${unclearClaims.length} luận điểm vẫn đang được gắn nhãn "CHƯA RÕ":\n` +
            unclearClaims.map((c, i) => `  ${i + 1}. "${c.text || c.sentence}"`).join('\n') +
            `\n\nBạn có chắc chắn muốn xuất gói tài nguyên này không?`
        );
        if (!proceedSafety) return;
    }

    // Ensure latest changes are saved first
    await executeAutosave();

    // Open export modal & reset state
    DOM.exportModal.classList.remove('hidden');
    DOM.exportProgressSection.classList.remove('hidden');
    DOM.exportResultSection.classList.add('hidden');
    DOM.exportWarningBox.classList.add('hidden');

    if (unclearClaims.length > 0) {
        DOM.exportWarningBox.textContent = `⚠️ Lưu ý: Kịch bản chứa ${unclearClaims.length} luận điểm chưa được chứng minh đầy đủ.`;
        DOM.exportWarningBox.classList.remove('hidden');
    }

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
    DOM.exportModal.classList.add('hidden');
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

// ==========================================
// 7. Initialization
// ==========================================

async function init() {
    setupTabs();
    setupCheatsheet();

    // Event Listeners
    DOM.btnNewProject.addEventListener('click', createNewProject);
    DOM.btnRandomLength.addEventListener('click', randomTargetDuration);

    if (DOM.btnPreviewAudio) {
        DOM.btnPreviewAudio.addEventListener('click', handleAudioPreview);
    }
    if (DOM.btnCloseAudio) {
        DOM.btnCloseAudio.addEventListener('click', () => {
            DOM.audioPlayer.pause();
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
    if (DOM.btnCloseExportModal) {
        DOM.btnCloseExportModal.addEventListener('click', closeExportModal);
    }
    if (DOM.btnCloseExport) {
        DOM.btnCloseExport.addEventListener('click', closeExportModal);
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

    DOM.projectTitleInput.addEventListener('input', () => {
        scheduleAutosave();
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
