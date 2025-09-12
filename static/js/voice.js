// Voice TTS client for Gemini 2.5 TTS

document.addEventListener("DOMContentLoaded", () => {
  const synthBtn = document.getElementById("synthesize-btn");
  const downloadBtn = document.getElementById("download-btn");
  const audioEl = document.getElementById("tts-audio");
  const statusEl = document.getElementById("tts-status");

  let lastBlobUrl = null;

  synthBtn.addEventListener("click", async () => {
    const text = document.getElementById("tts-text").value.trim();
    const voice = document.getElementById("voice-name").value;
    const model = document.getElementById("model-name").value;

    if (!text) {
      statusEl.textContent = "Please enter text to synthesize.";
      return;
    }

    statusEl.textContent = "Synthesizing...";
    synthBtn.disabled = true;
    downloadBtn.disabled = true;

    try {
      const resp = await fetch("/api/voice/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice_name: voice, model }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: resp.statusText }));
        throw new Error(err.error || "TTS request failed");
      }

      // Respect the server-provided content type
      const contentType = resp.headers.get("Content-Type") || "audio/wav";
      const arrayBuf = await resp.arrayBuffer();
      const blob = new Blob([arrayBuf], { type: contentType });

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
        a.download = "tts.wav";
        document.body.appendChild(a);
        a.click();
        a.remove();
      };

      statusEl.textContent = "Done.";
    } catch (e) {
      console.error("TTS error:", e);
      statusEl.textContent = "Error: " + e.message;
    } finally {
      synthBtn.disabled = false;
    }
  });
});
