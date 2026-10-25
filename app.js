// Interaction controller for the agent interface
document.addEventListener("DOMContentLoaded", () => {
  // 1. Signature Hero Reveal Motion
  const heroSection = document.querySelector(".hero-section");
  if (heroSection) {
    requestAnimationFrame(() => {
      heroSection.classList.add("is-revealed");
    });
  }

  // 2. Showcase Output Index: Live Sheet Swapper
  const sheetButtons = document.querySelectorAll(".sheet-selector-btn");
  const sheets = document.querySelectorAll(".live-sheet");

  sheetButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-sheet");

      sheetButtons.forEach((b) => b.classList.remove("active"));
      sheets.forEach((s) => s.classList.remove("is-visible"));

      btn.classList.add("active");
      const targetSheet = document.getElementById("sheet-" + targetId);
      if (targetSheet) {
        targetSheet.classList.add("is-visible");
      }
    });
  });

  // 3. Interactive Terminal: Real Python Runtime Connection
  const textInput = document.getElementById("agentPromptInput");
  const submitBtn = document.getElementById("agentSubmitBtn");
  const outputBox = document.getElementById("agentOutputBox");
  const clearBtn = document.getElementById("agentClearBtn");
  const promptChips = document.querySelectorAll(".prompt-chip");

  let lastReplyText = "";

  // Prompt Chips Handler
  promptChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const query = chip.getAttribute("data-query");
      if (textInput && query) {
        textInput.value = query;
        textInput.focus();
        executeQuery();
      }
    });
  });

  // Clear Console Handler
  if (clearBtn && outputBox) {
    clearBtn.addEventListener("click", () => {
      outputBox.innerHTML = "<span class=\"output-placeholder\">Ready for dispatch. Select a chip above or type an instruction to invoke the agent loop.</span>";
      lastReplyText = "";
      if (textInput) {
        textInput.value = "";
        textInput.focus();
      }
    });
  }

  // Copy to Clipboard
  window.copyResponseContent = function () {
    if (!lastReplyText) return;
    navigator.clipboard.writeText(lastReplyText).then(() => {
      const copyBtn = document.getElementById("copyOutputBtn");
      if (copyBtn) {
        const originalText = copyBtn.innerText;
        copyBtn.innerText = "Copied";
        setTimeout(() => {
          copyBtn.innerText = originalText;
        }, 1500);
      }
    });
  };

  async function executeQuery() {
    if (!textInput || !outputBox) return;
    const val = textInput.value.trim();
    if (!val) return;

    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.5";
    outputBox.innerHTML = "<span style=\"color: var(--muted);\">Executing instruction through NVIDIA inference pipeline...</span>";

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: val })
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      lastReplyText = data.reply || data.error || "";

      let imageBlock = "";
      if (data.image_url) {
        imageBlock = `
          <div class="output-image-wrap">
            <img src="${data.image_url}" alt="Generated artifact">
          </div>
        `;
      }

      outputBox.innerHTML = `
        <div class="output-meta-bar">
          <span class="output-type-badge">${data.title || "Agent Output"}</span>
          <button id="copyOutputBtn" class="output-copy-btn" onclick="copyResponseContent()">Copy</button>
        </div>
        <div class="output-rendered-text">${escapeHtml(lastReplyText)}</div>
        ${imageBlock}
      `;
    } catch (err) {
      outputBox.innerHTML = `
        <div class="output-meta-bar">
          <span class="output-type-badge" style="color: #ff6b6b;">Connection Error</span>
        </div>
        <div class="output-rendered-text">${escapeHtml(err.message)}</div>
      `;
    } finally {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
    }
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  if (submitBtn) {
    submitBtn.addEventListener("click", executeQuery);
  }

  if (textInput) {
    textInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey || !e.shiftKey)) {
        e.preventDefault();
        executeQuery();
      }
    });
  }
});
