// topics.js - Topic Suggestion modal for Short-Content.
// Opens like the voice modal: a centered overlay listing all unused topics
// plus a form to add a new one. Triggered by #btn-topics-toolbar in the
// editor toolbar. No dependency on app.js internals:
// "Dung chu de nay" only puts hook + fact into #script-editor, closes the
// modal, then the user presses the existing "Dung khung tu dau" button.

(function () {
  const modalEl = document.getElementById("topics-modal");
  const listEl = document.getElementById("topics-modal-list");
  const countEl = document.getElementById("topics-count");
  const openBtn = document.getElementById("btn-topics-toolbar");
  const closeBtn = document.getElementById("btn-close-topics-modal");
  const cancelBtn = document.getElementById("btn-cancel-topics");
  const newBtn = document.getElementById("btn-new-topic");
  const formEl = document.getElementById("new-topic-form");
  const hookInput = document.getElementById("new-topic-hook");
  const factInput = document.getElementById("new-topic-fact");
  const sourceInput = document.getElementById("new-topic-source");
  const saveBtn = document.getElementById("btn-save-new-topic");
  const statusEl = document.getElementById("new-topic-status");
  if (!modalEl || !listEl || !openBtn) return; // Modal HTML not added yet: do nothing.

  function openModal() {
    modalEl.classList.remove("hidden");
    loadTopics();
  }

  function closeModal() {
    modalEl.classList.add("hidden");
    if (formEl) formEl.classList.add("hidden");
    if (newBtn) newBtn.textContent = "＋ Tạo chủ đề mới";
    if (statusEl) statusEl.textContent = "";
  }

  async function loadTopics() {
    listEl.innerHTML = "<p class='empty-hint'>Đang tải chủ đề...</p>";
    try {
      const res = await fetch("/api/topics?only_unused=true");
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "Không tải được chủ đề.");
      renderTopics(data.topics || [], data);
    } catch (e) {
      listEl.innerHTML = "<p class='empty-hint'>Lỗi: " + escapeHtml(e.message) + "</p>";
    }
  }

  function renderTopics(topics, meta) {
    if (countEl) countEl.textContent = "Còn " + meta.unused + "/" + meta.total + " chủ đề chưa dùng.";
    if (!topics.length) {
      listEl.innerHTML = "<p class='empty-hint'>Đã dùng hết chủ đề. Bấm '＋ Tạo chủ đề mới' để thêm chủ đề của bạn.</p>";
      return;
    }
    listEl.innerHTML = "";

    topics.forEach(function (t) {
      const card = document.createElement("div");
      card.className = "topic-card";
      card.style.cssText = "border:1px solid var(--border-color);border-radius:8px;padding:12px;margin:0;";
      card.innerHTML =
        "<strong>#" + escapeHtml(t.id) + " - " + escapeHtml(t.hook) + "</strong>" +
        "<p style='font-size:0.85rem;margin:6px 0;'>" + escapeHtml(t.fact) + "</p>" +
        "<p style='font-size:0.75rem;color:var(--text-muted);margin:0 0 8px;'>Nguồn: " + escapeHtml(t.source) + "</p>";

      const useBtn = document.createElement("button");
      useBtn.className = "btn-secondary";
      useBtn.textContent = "✍️ Dùng chủ đề này";
      useBtn.onclick = function () {
        const editor = document.getElementById("script-editor");
        if (editor) {
          editor.value = t.hook + " " + t.fact;
          editor.focus();
        }
        closeModal();
      };

      const doneBtn = document.createElement("button");
      doneBtn.className = "btn-secondary";
      doneBtn.style.marginLeft = "8px";
      doneBtn.textContent = "✅ Đã dùng";
      doneBtn.onclick = async function () {
        await fetch("/api/topics/" + encodeURIComponent(t.id) + "/use", { method: "POST" });
        loadTopics();
      };

      card.appendChild(useBtn);
      card.appendChild(doneBtn);
      listEl.appendChild(card);
    });
  }

  async function saveNewTopic() {
    const hook = hookInput.value.trim();
    const fact = factInput.value.trim();
    const source = sourceInput.value.trim();
    if (!hook || !fact) {
      statusEl.textContent = "Nhập hook và fact rồi mới lưu.";
      return;
    }
    saveBtn.disabled = true;
    statusEl.textContent = "Đang lưu...";
    try {
      const res = await fetch("/api/topics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hook: hook, fact: fact, source: source }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) throw new Error((data && data.detail) || "Không lưu được chủ đề.");
      hookInput.value = "";
      factInput.value = "";
      sourceInput.value = "";
      formEl.classList.add("hidden");
      newBtn.textContent = "＋ Tạo chủ đề mới";
      statusEl.textContent = "Đã thêm chủ đề #" + data.topic.id + ".";
      loadTopics();
    } catch (e) {
      statusEl.textContent = "Lỗi: " + e.message;
    } finally {
      saveBtn.disabled = false;
    }
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  openBtn.addEventListener("click", openModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);
  modalEl.addEventListener("click", function (e) {
    if (e.target === modalEl) closeModal();
  });
  if (newBtn) {
    newBtn.addEventListener("click", function () {
      const hidden = formEl.classList.toggle("hidden");
      newBtn.textContent = hidden ? "＋ Tạo chủ đề mới" : "－ Đóng form";
      if (!hidden) hookInput.focus();
    });
  }
  if (saveBtn) saveBtn.addEventListener("click", saveNewTopic);
})();
