// System TTS client (pyttsx3)

document.addEventListener("DOMContentLoaded", () => {
  const synthBtn = document.getElementById("system-synthesize-btn");
  const downloadBtn = document.getElementById("system-download-btn");
  const audioEl = document.getElementById("system-audio");
  const statusEl = document.getElementById("system-status");
  const rateSlider = document.getElementById("system-rate");
  const volumeSlider = document.getElementById("system-volume");
  const rateValue = document.getElementById("rate-value");
  const volumeValue = document.getElementById("volume-value");

  let lastBlobUrl = null;

  // Update rate display
  rateSlider.addEventListener("input", () => {
    rateValue.textContent = rateSlider.value;
  });

  // Update volume display
  volumeSlider.addEventListener("input", () => {
    volumeValue.textContent = volumeSlider.value;
  });

  synthBtn.addEventListener("click", async () => {
    const text = document.getElementById("system-text").value.trim();
    const rate = parseInt(rateSlider.value);
    const volume = parseInt(volumeSlider.value) / 100; // Convert to 0-1 range

    if (!text) {
      statusEl.textContent = "Please enter text to synthesize.";
      return;
    }

    statusEl.textContent = "Synthesizing with system TTS...";
    synthBtn.disabled = true;
    downloadBtn.disabled = true;

    try {
      const resp = await fetch("/api/system/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          rate: rate,
          volume: volume,
        }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: resp.statusText }));
        throw new Error(err.error || "System TTS request failed");
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
        a.download = "system_tts.wav";
        document.body.appendChild(a);
        a.click();
        a.remove();
      };

      statusEl.textContent = "Synthesis complete!";
    } catch (e) {
      console.error("System TTS error:", e);
      statusEl.textContent = "Error: " + e.message;
    } finally {
      synthBtn.disabled = false;
    }
  });
});
