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
            target_duration: state.currentProject.target_duration || 90
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
// 6. Utility Functions
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
