// topics.js - Topic Suggestion UI for Short-Content.
// Loads AFTER static/app.js. No dependency on app.js internals:
// "Dung chu de nay" only puts hook + fact into #script-editor,
// then the user presses the existing "Dung khung tu dau" button.
//
// Wire-up (see README-TOPIC-INTEGRATION.md):
//   1. Add the HTML snippet (button + #topics-list) inside #gemini-tab.
//   2. Add <script src="/static/topics.js"></script> after app.js in index.html.

(function () {
  const listEl = document.getElementById("topics-list");
  const btnEl = document.getElementById("btn-suggest-topics");
  if (!listEl || !btnEl) return; // HTML snippet not added yet: do nothing.

  async function loadTopics() {
    listEl.innerHTML = "<p class='empty-hint'>Dang tai chu de...</p>";
    try {
      const res = await fetch("/api/topics?only_unused=true");
      const data = await res.json();
      if (!data.success) throw new Error(data.detail || "Khong tai duoc chu de.");
      renderTopics(data.topics || [], data);
    } catch (e) {
      listEl.innerHTML = "<p class='empty-hint'>Loi: " + e.message + "</p>";
    }
  }

  function renderTopics(topics, meta) {
    if (!topics.length) {
      listEl.innerHTML = "<p class='empty-hint'>Da dung het chu de. Them chu de moi vao data/topics.json nhe.</p>";
      return;
    }
    const head = document.createElement("p");
    head.className = "empty-hint";
    head.textContent = "Con " + meta.unused + "/" + meta.total + " chu de chua dung. Bam 1 chu de de dung.";
    listEl.innerHTML = "";
    listEl.appendChild(head);

    topics.forEach(function (t) {
      const card = document.createElement("div");
      card.className = "topic-card";
      card.style.cssText = "border:1px solid var(--border-color);border-radius:8px;padding:10px;margin:8px 0;";
      card.innerHTML =
        "<strong>#" + t.id + " - " + escapeHtml(t.hook) + "</strong>" +
        "<p style='font-size:0.85rem;margin:6px 0;'>" + escapeHtml(t.fact) + "</p>" +
        "<p style='font-size:0.75rem;color:var(--text-muted);margin:0 0 8px;'>Nguon: " + escapeHtml(t.source) + "</p>";

      const useBtn = document.createElement("button");
      useBtn.className = "btn-secondary";
      useBtn.textContent = "✍️ Dùng chủ đề này";
      useBtn.onclick = function () {
        const editor = document.getElementById("script-editor");
        if (editor) {
          editor.value = t.hook + " " + t.fact;
          editor.focus();
          editor.scrollIntoView({ behavior: "smooth", block: "center" });
        }
        alert("Da dua hook + fact vao khung viet. Bam 'Dung khung tu dau' de Gemini viet kich ban, roi nho kiem chung lai con so truoc khi xuat.");
      };

      const doneBtn = document.createElement("button");
      doneBtn.className = "btn-secondary";
      doneBtn.style.marginLeft = "8px";
      doneBtn.textContent = "✅ Đã dùng";
      doneBtn.onclick = async function () {
        await fetch("/api/topics/" + t.id + "/use", { method: "POST" });
        loadTopics();
      };

      card.appendChild(useBtn);
      card.appendChild(doneBtn);
      listEl.appendChild(card);
    });
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  btnEl.addEventListener("click", loadTopics);
})();
