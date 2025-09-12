// Chat functionality for the AI chatbot

let currentSessionId = "session_" + Date.now();
let isTyping = false;
let currentAudio = null; // Track current playing audio

// Initialize chat when page loads
document.addEventListener("DOMContentLoaded", function () {
  console.log("Chat initialized");
  initializeChat();
  setupEventListeners();
});

function setupEventListeners() {
  // Character count for input
  const messageInput = document.getElementById("message-input");
  const charCount = document.getElementById("char-count");

  messageInput.addEventListener("input", function () {
    charCount.textContent = this.value.length;
  });

  // Auto-resize textarea (if we switch to textarea later)
  messageInput.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = this.scrollHeight + "px";
  });
}

function initializeChat() {
  // Show welcome message and get a random starter
  setTimeout(() => {
    getRandomStarter();
  }, 1000);
}

async function sendMessage() {
  const messageInput = document.getElementById("message-input");
  const message = messageInput.value.trim();

  if (!message) return;

  // Clear input and reset character count
  messageInput.value = "";
  document.getElementById("char-count").textContent = "0";

  // Add user message to chat
  addMessageToChat("user", message);

  // Show typing indicator
  showTypingIndicator();

  try {
    // Send message to backend
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
        session_id: currentSessionId,
      }),
    });

    const data = await response.json();

    // Hide typing indicator
    hideTypingIndicator();

    if (data.status === "success") {
      // Generate TTS in parallel with adding message to chat
      if (isTTSEnabled()) {
        generateAndPlayTTS(data.response);
      }
      // Add AI response to chat
      addMessageToChat("assistant", data.response);
    } else {
      // Show error message
      addMessageToChat(
        "assistant",
        "Sorry, I encountered an error. Please try again."
      );
      console.error("Chat error:", data.error);
    }
  } catch (error) {
    hideTypingIndicator();
    addMessageToChat(
      "assistant",
      "Sorry, I'm having trouble connecting. Please try again."
    );
    console.error("Network error:", error);
  }
}

async function getRandomStarter() {
  try {
    const response = await fetch("/api/chat/starter", {
      method: "GET",
    });

    const data = await response.json();

    if (data.status === "success") {
      // Generate TTS in parallel with adding message to chat
      if (isTTSEnabled()) {
        generateAndPlayTTS(data.starter);
      }
      // Clear welcome message and add starter
      clearWelcomeMessage();
      addMessageToChat("assistant", data.starter);
    }
  } catch (error) {
    console.error("Error getting random starter:", error);
    // Fallback starter
    clearWelcomeMessage();
    addMessageToChat(
      "assistant",
      "Hey there! What would you like to chat about today? 😊"
    );
  }
}

function addMessageToChat(role, content) {
  const chatMessages = document.getElementById("chat-messages");

  // Create message element
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}`;

  const messageContent = document.createElement("div");
  messageContent.className = "message-content";
  messageContent.textContent = content;

  const messageTime = document.createElement("div");
  messageTime.className = "message-time";
  messageTime.textContent = new Date().toLocaleTimeString();

  messageContent.appendChild(messageTime);
  messageDiv.appendChild(messageContent);

  // Add to chat
  chatMessages.appendChild(messageDiv);

  // Scroll to bottom
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Add animation
  messageDiv.style.opacity = "0";
  messageDiv.style.transform = "translateY(20px)";

  setTimeout(() => {
    messageDiv.style.transition = "all 0.3s ease";
    messageDiv.style.opacity = "1";
    messageDiv.style.transform = "translateY(0)";
  }, 100);
}

function showTypingIndicator() {
  const chatMessages = document.getElementById("chat-messages");

  // Remove existing typing indicator
  const existingTyping = chatMessages.querySelector(".typing-indicator");
  if (existingTyping) {
    existingTyping.remove();
  }

  // Create typing indicator
  const typingDiv = document.createElement("div");
  typingDiv.className = "message assistant";
  typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;

  chatMessages.appendChild(typingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
  const typingIndicator = document.querySelector(".typing-indicator");
  if (typingIndicator) {
    typingIndicator.parentElement.remove();
  }
}

function clearWelcomeMessage() {
  const welcomeMessage = document.querySelector(".welcome-message");
  if (welcomeMessage) {
    welcomeMessage.remove();
  }
}

function clearChat() {
  if (confirm("Are you sure you want to clear the conversation?")) {
    // Clear UI
    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML =
      '<div class="welcome-message text-center p-4"><div class="spinner-border text-primary mb-3" role="status"><span class="visually-hidden">Loading...</span></div><p class="text-muted">Starting fresh conversation...</p></div>';

    // Clear backend memory
    fetch("/api/chat/clear", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: currentSessionId,
      }),
    })
      .then(() => {
        // Get new random starter
        setTimeout(() => {
          getRandomStarter();
        }, 1000);
      })
      .catch((error) => {
        console.error("Error clearing chat:", error);
      });

    // Generate new session ID
    currentSessionId = "session_" + Date.now();
  }
}

function handleKeyPress(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
}

// TTS Functions
function isTTSEnabled() {
  const ttsCheckbox = document.getElementById("tts-enabled");
  return ttsCheckbox ? ttsCheckbox.checked : false;
}

function getSelectedVoice() {
  const voiceSelect = document.getElementById("voice-select");
  return voiceSelect ? voiceSelect.value : "Kore";
}

async function generateAndPlayTTS(text) {
  try {
    // Stop any currently playing audio
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }

    // Show TTS loading indicator
    showTTSLoadingIndicator();

    // Generate TTS audio
    const response = await fetch("/api/chat/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
        voice_name: getSelectedVoice(),
      }),
    });

    if (!response.ok) {
      console.error("TTS generation failed:", response.statusText);
      hideTTSLoadingIndicator();
      return;
    }

    // Hide loading indicator
    hideTTSLoadingIndicator();

    // Create audio element and play
    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);

    currentAudio = new Audio(audioUrl);
    currentAudio.play().catch((error) => {
      console.error("Audio play failed:", error);
    });

    // Clean up URL when audio ends
    currentAudio.addEventListener("ended", () => {
      URL.revokeObjectURL(audioUrl);
      currentAudio = null;
    });
  } catch (error) {
    console.error("TTS error:", error);
    hideTTSLoadingIndicator();
  }
}

function showTTSLoadingIndicator() {
  // Add a small audio icon to indicate TTS is generating
  const chatMessages = document.getElementById("chat-messages");
  const lastMessage = chatMessages.lastElementChild;
  if (lastMessage && lastMessage.classList.contains("assistant")) {
    const audioIcon = document.createElement("div");
    audioIcon.className = "tts-loading";
    audioIcon.innerHTML = '<i class="fas fa-volume-up text-primary"></i>';
    audioIcon.style.cssText =
      "position: absolute; right: 10px; top: 10px; font-size: 12px; opacity: 0.7;";
    lastMessage.style.position = "relative";
    lastMessage.appendChild(audioIcon);
  }
}

function hideTTSLoadingIndicator() {
  const ttsLoading = document.querySelector(".tts-loading");
  if (ttsLoading) {
    ttsLoading.remove();
  }
}

// Export functions for global access
window.sendMessage = sendMessage;
window.getRandomStarter = getRandomStarter;
window.clearChat = clearChat;
window.handleKeyPress = handleKeyPress;
