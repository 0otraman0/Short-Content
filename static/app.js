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

    // Video Render & Modal
    btnRenderVideo: document.getElementById('btn-render-video'),
    renderModal: document.getElementById('render-modal'),
    renderModalTitle: document.getElementById('render-modal-title'),
    btnCloseRenderModal: document.getElementById('btn-close-render-modal'),
    btnCancelRender: document.getElementById('btn-cancel-render'),
    renderProgressSection: document.getElementById('render-progress-section'),
    renderStepLabel: document.getElementById('render-step-label'),
    renderProgressBar: document.getElementById('render-progress-bar'),
    renderProgressPercent: document.getElementById('render-progress-percent'),
    renderDurationInfo: document.getElementById('render-duration-info'),
    renderWarningBox: document.getElementById('render-warning-box'),
    renderResultSection: document.getElementById('render-result-section'),
    renderedVideoPlayer: document.getElementById('rendered-video-player'),
    btnDownloadVideo: document.getElementById('btn-download-video'),

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
        if (DOM.btnRenderVideo) {
        DOM.btnRenderVideo.addEventListener('click', handleStartRender);
    }
    if (DOM.btnCloseRenderModal) {
        DOM.btnCloseRenderModal.addEventListener('click', closeRenderModal);
    }
    if (DOM.btnCancelRender) {
        DOM.btnCancelRender.addEventListener('click', closeRenderModal);
    }

    if (DOM.presetSelector) {
            DOM.presetSelector.value = proj.pacing_preset || 'mystery';
        }
        setTargetDuration(proj.target_duration || 90);
        updateStatsDisplay();

        DOM.saveStatus.textContent = 'Đã lưu';
        DOM.saveStatus.className = 'save-status';

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
// 5. System Status & Diagnostics
// ==========================================

async function checkSystemStatus() {
    try {
        const res = await fetch('/api/status');
        if (!res.ok) throw new Error();
        const data = await res.json();

        let statusText = 'Hệ thống sẵn sàng';
        if (data.gpu && data.gpu.has_gpu) {
            statusText += ` (GPU: NVENC)`;
        } else {
            statusText += ` (CPU)`;
        }
        if (!data.ffmpeg) {
            statusText = 'Cảnh báo: Chưa có FFmpeg';
            DOM.systemStatus.querySelector('.status-dot').style.backgroundColor = 'var(--danger)';
        } else {
            DOM.systemStatus.querySelector('.status-dot').style.backgroundColor = 'var(--success)';
        }

        DOM.systemStatus.innerHTML = `<span class="status-dot"></span> ${statusText}`;
        DOM.systemStatus.title = `Model AI: ${data.config.model} | Giọng: ${data.config.voice}`;
    } catch (err) {
        DOM.systemStatus.innerHTML = `<span class="status-dot" style="background:var(--danger)"></span> Mất kết nối server`;
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
// 7. Video Render Pipeline & Modal Controls
// ==========================================

let renderPollTimer = null;

async function handleStartRender() {
    if (!state.currentProject) {
        alert('Vui lòng chọn hoặc tạo một dự án trước.');
        return;
    }

    const script = DOM.scriptEditor.value.trim();
    if (!script) {
        alert('Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi tạo video.');
        return;
    }

    // Check estimated duration
    const { duration } = calculateStats(script);
    if (duration < 60 || duration > 180) {
        const proceed = confirm(
            `Thời lượng kịch bản ước tính là ${duration}s (khuyến nghị cho YouTube Shorts là từ 60 đến 180 giây).\n\nBạn có muốn tiếp tục tạo video không?`
        );
        if (!proceed) return;
    }

    // Ensure latest changes are saved first
    await executeAutosave();

    // Open render modal & reset state
    DOM.renderModal.classList.remove('hidden');
    DOM.renderProgressSection.classList.remove('hidden');
    DOM.renderResultSection.classList.add('hidden');
    DOM.btnDownloadVideo.classList.add('hidden');
    DOM.renderWarningBox.classList.add('hidden');

    DOM.renderStepLabel.textContent = 'Đang khởi động tiến trình...';
    DOM.renderProgressBar.style.width = '5%';
    DOM.renderProgressPercent.textContent = '5%';
    DOM.renderDurationInfo.textContent = '';

    try {
        const res = await fetch(`/api/projects/${state.currentProject.id}/render`, {
            method: 'POST'
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || 'Không thể bắt đầu render');
        }

        const data = await res.json();
        const jobId = data.job_id;

        // Poll render status
        pollRenderProgress(state.currentProject.id, jobId);
    } catch (err) {
        DOM.renderStepLabel.textContent = 'Lỗi: ' + err.message;
        DOM.renderProgressBar.style.background = 'var(--danger)';
    }
}

function pollRenderProgress(projectId, jobId) {
    clearInterval(renderPollTimer);

    renderPollTimer = setInterval(async () => {
        try {
            const res = await fetch(`/api/projects/${projectId}/render-status/${jobId}`);
            if (!res.ok) throw new Error('Mất kết nối với tiến trình render');
            const job = await res.json();

            // Update progress
            DOM.renderProgressBar.style.width = `${job.progress || 5}%`;
            DOM.renderProgressPercent.textContent = `${job.progress || 5}%`;
            DOM.renderStepLabel.textContent = job.step || 'Đang xử lý...';

            if (job.duration) {
                DOM.renderDurationInfo.textContent = `Thời lượng: ${job.duration.toFixed(1)}s`;
            }

            if (job.warning) {
                DOM.renderWarningBox.textContent = '⚠️ ' + job.warning;
                DOM.renderWarningBox.classList.remove('hidden');
            }

            // Completed
            if (job.status === 'completed') {
                clearInterval(renderPollTimer);
                DOM.renderStepLabel.textContent = '🎉 Video đã tạo thành công!';
                DOM.renderProgressBar.style.width = '100%';
                DOM.renderProgressPercent.textContent = '100%';

                // Show player
                if (job.video_url) {
                    DOM.renderResultSection.classList.remove('hidden');
                    DOM.renderedVideoPlayer.src = job.video_url + '?t=' + Date.now();
                    DOM.btnDownloadVideo.href = job.video_url;
                    DOM.btnDownloadVideo.classList.remove('hidden');
                }

                // Refresh sidebar projects
                renderProjectsList();
            }

            // Failed
            if (job.status === 'failed') {
                clearInterval(renderPollTimer);
                DOM.renderStepLabel.textContent = '❌ ' + (job.error || 'Quá trình render thất bại');
                DOM.renderProgressBar.style.background = 'var(--danger)';
            }
        } catch (err) {
            console.error('Polling error:', err);
        }
    }, 1000);
}

function closeRenderModal() {
    clearInterval(renderPollTimer);
    if (DOM.renderedVideoPlayer) {
        DOM.renderedVideoPlayer.pause();
    }
    DOM.renderModal.classList.add('hidden');
}

// ==========================================
// 8. Utility Functions
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

    if (DOM.btnRenderVideo) {
        DOM.btnRenderVideo.addEventListener('click', handleStartRender);
    }
    if (DOM.btnCloseRenderModal) {
        DOM.btnCloseRenderModal.addEventListener('click', closeRenderModal);
    }
    if (DOM.btnCancelRender) {
        DOM.btnCancelRender.addEventListener('click', closeRenderModal);
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
