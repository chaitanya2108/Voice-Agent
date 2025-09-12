// Google Gemini TTS client

document.addEventListener("DOMContentLoaded", () => {
  const synthBtn = document.getElementById("gemini-synthesize-btn");
  const downloadBtn = document.getElementById("gemini-download-btn");
  const audioEl = document.getElementById("gemini-audio");
  const statusEl = document.getElementById("gemini-status");

  let lastBlobUrl = null;

  synthBtn.addEventListener("click", async () => {
    const text = document.getElementById("gemini-text").value.trim();
    const speaker1Name = document.getElementById("speaker1-name").value.trim();
    const speaker1Voice = document.getElementById("speaker1-voice").value;
    const speaker2Name = document.getElementById("speaker2-name").value.trim();
    const speaker2Voice = document.getElementById("speaker2-voice").value;

    if (!text) {
      statusEl.textContent = "Please enter text to synthesize.";
      return;
    }

    if (!speaker1Name || !speaker2Name) {
      statusEl.textContent = "Please enter speaker names.";
      return;
    }

    statusEl.textContent = "Synthesizing with Gemini TTS...";
    synthBtn.disabled = true;
    downloadBtn.disabled = true;

    try {
      const resp = await fetch("/api/gemini/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          speaker1_name: speaker1Name,
          speaker1_voice: speaker1Voice,
          speaker2_name: speaker2Name,
          speaker2_voice: speaker2Voice,
        }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: resp.statusText }));
        throw new Error(err.error || "Gemini TTS request failed");
      }

      const arrayBuf = await resp.arrayBuffer();
      const blob = new Blob([arrayBuf], { type: "audio/wav" });

      if (lastBlobUrl) URL.revokeObjectURL(lastBlobUrl);
      lastBlobUrl = URL.createObjectURL(blob);
      audioEl.src = lastBlobUrl;
      audioEl.play().catch(() => {
        /* autoplay might be blocked */
      });

      // Enable download
      downloadBtn.disabled = false;
      downloadBtn.onclick = () => {
        const a = document.createElement("a");
        a.href = lastBlobUrl;
        a.download = "gemini_tts.wav";
        document.body.appendChild(a);
        a.click();
        a.remove();
      };

      statusEl.textContent = "Synthesis complete!";
    } catch (e) {
      console.error("Gemini TTS error:", e);
      statusEl.textContent = "Error: " + e.message;
    } finally {
      synthBtn.disabled = false;
    }
  });
});
