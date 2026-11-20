/**
 * CodeAlpha AI Internship - Task 2: Chatbot for FAQs
 * Client-Side Messaging and Interaction Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const chatMessages = document.getElementById("chatMessages");
    const typingIndicator = document.getElementById("typingIndicator");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const themeToggleBtn = document.getElementById("themeToggleBtn");
    const browseFaqBtn = document.getElementById("browseFaqBtn");
    const faqModal = document.getElementById("faqModal");
    const closeModalBtn = document.getElementById("closeModalBtn");
    const faqSearchInput = document.getElementById("faqSearchInput");
    const faqItems = document.querySelectorAll(".faq-item");
    const initTime = document.getElementById("initTime");

    let isBotTyping = false;

    // Set initial timestamp
    if (initTime) {
        initTime.textContent = getCurrentTime();
    }

    // --- 1. Theme Management ---
    const savedTheme = localStorage.getItem("codealpha_chat_theme") || "dark-theme";
    document.body.className = savedTheme;

    themeToggleBtn.addEventListener("click", () => {
        const isDark = document.body.classList.contains("dark-theme");
        const nextTheme = isDark ? "light-theme" : "dark-theme";
        document.body.className = nextTheme;
        localStorage.setItem("codealpha_chat_theme", nextTheme);
    });

    // --- 2. Form Submission ---
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text || isBotTyping) return;

        sendMessage(text);
        userInput.value = "";
    });

    // --- 3. Chip / Suggestion Clicks ---
    document.addEventListener("click", (e) => {
        const chip = e.target.closest(".chip");
        if (chip) {
            const query = chip.getAttribute("data-query") || chip.textContent.trim();
            if (query && !isBotTyping) {
                sendMessage(query);
            }
        }
    });

    let chatHistory = [];

    // --- 4. Send Message & Receive Response ---
    async function sendMessage(text) {
        // 1. Render User Message
        appendUserMessage(text);
        scrollToBottom();

        // 2. Show Typing Indicator
        setTyping(true);
        scrollToBottom();

        // Add user turn to history
        chatHistory.push({ role: "user", text: text });

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: text,
                    history: chatHistory.slice(-6)
                })
            });

            const data = await response.json();

            // Simulate slight natural pause for realism
            await new Promise((resolve) => setTimeout(resolve, 350));

            setTyping(false);

            if (!response.ok || data.status !== "success") {
                appendBotMessage({
                    answer: data.message || "I encountered an issue processing your question. Please try again.",
                    category: null,
                    confidence: 0,
                    suggestions: []
                });
            } else {
                appendBotMessage(data.data);
                if (data.data && data.data.answer) {
                    chatHistory.push({ role: "assistant", text: data.data.answer });
                }
            }

            scrollToBottom();

        } catch (err) {
            console.error("Chat API error:", err);
            setTyping(false);
            appendBotMessage({
                answer: "Connection error: Unable to reach the NLP service. Please check if the server is running.",
                category: null,
                confidence: 0,
                suggestions: []
            });
            scrollToBottom();
        }
    }

    // --- 5. Message Renderers ---
    function appendUserMessage(text) {
        const row = document.createElement("div");
        row.className = "message-row user-row";
        row.innerHTML = `
            <div class="msg-avatar user-avatar-small">👤</div>
            <div class="msg-bubble-wrap">
                <div class="msg-bubble user-bubble">${escapeHtml(text)}</div>
                <div class="msg-meta">
                    <span class="msg-time">${getCurrentTime()}</span>
                </div>
            </div>
        `;
        chatMessages.appendChild(row);
    }

    function appendBotMessage(data) {
        const row = document.createElement("div");
        row.className = "message-row bot-row";

        let metaHtml = `<span class="msg-time">${getCurrentTime()}</span>`;
        if (data.category) {
            metaHtml += `<span class="category-badge">${escapeHtml(data.category)}</span>`;
        }
        if (data.confidence && data.confidence > 0) {
            const isHigh = data.confidence >= 40;
            const badgeClass = isHigh ? "confidence-badge" : "confidence-badge confidence-moderate";
            metaHtml += `<span class="${badgeClass}">${data.confidence}% Match</span>`;
        }

        // Suggestions markup
        let suggestionsHtml = "";
        if (data.suggestions && data.suggestions.length > 0) {
            suggestionsHtml = `
                <div class="followup-suggestions">
                    <span class="followup-title">Related questions:</span>
                    <div class="suggestion-chips">
                        ${data.suggestions.map(s => `<button class="chip" data-query="${escapeHtml(s)}">${escapeHtml(s)}</button>`).join("")}
                    </div>
                </div>
            `;
        }

        row.innerHTML = `
            <div class="msg-avatar bot-avatar-small">🤖</div>
            <div class="msg-bubble-wrap">
                <div class="msg-bubble bot-bubble">
                    <p>${formatMessageContent(data.answer)}</p>
                    ${suggestionsHtml}
                </div>
                <div class="msg-meta">
                    ${metaHtml}
                </div>
            </div>
        `;

        chatMessages.appendChild(row);
    }

    function setTyping(typing) {
        isBotTyping = typing;
        typingIndicator.style.display = typing ? "flex" : "none";
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getCurrentTime() {
        return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatMessageContent(text) {
        if (!text) return "";
        // Convert line breaks to paragraphs or <br>
        const safe = escapeHtml(text);
        return safe.replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br>");
    }

    // --- 6. Clear Chat Conversation ---
    clearChatBtn.addEventListener("click", () => {
        chatHistory = [];
        chatMessages.innerHTML = `
            <div class="message-row bot-row">
                <div class="msg-avatar bot-avatar-small">🤖</div>
                <div class="msg-bubble-wrap">
                    <div class="msg-bubble bot-bubble">
                        <p><strong>Chat conversation reset.</strong></p>
                        <p>Ask me anything about CodeAlpha internship guidelines, tasks, or submission rules!</p>
                    </div>
                    <div class="msg-meta">
                        <span class="msg-time">${getCurrentTime()}</span>
                    </div>
                </div>
            </div>
            <div class="suggestions-container">
                <span class="suggestions-label">Popular Questions:</span>
                <div class="suggestion-chips">
                    <button class="chip" data-query="How many tasks do I need to complete to get the certificate?">Minimum Tasks Required</button>
                    <button class="chip" data-query="What is the required GitHub repository naming format?">GitHub Repo Naming</button>
                    <button class="chip" data-query="How do I submit my completed project?">Project Submission Form</button>
                    <button class="chip" data-query="What perks and benefits will I receive from this internship?">Internship Perks & LOR</button>
                </div>
            </div>
        `;
        userInput.focus();
    });

    // --- 7. FAQ Modal Browse & Filter ---
    function openFaqModal() {
        faqModal.style.display = "flex";
        faqSearchInput.value = "";
        filterFaqList("");
        faqSearchInput.focus();
    }

    function closeFaqModal() {
        faqModal.style.display = "none";
        browseFaqBtn.focus();
    }

    browseFaqBtn.addEventListener("click", openFaqModal);
    closeModalBtn.addEventListener("click", closeFaqModal);

    faqModal.addEventListener("click", (e) => {
        if (e.target === faqModal) {
            closeFaqModal();
        }
    });

    // Escape closes the dialog; Tab is trapped inside it while open.
    document.addEventListener("keydown", (e) => {
        if (faqModal.style.display === "none") return;

        if (e.key === "Escape") {
            closeFaqModal();
            return;
        }

        if (e.key === "Tab") {
            const focusable = faqModal.querySelectorAll(
                "button, input, [tabindex]:not([tabindex='-1'])"
            );
            if (!focusable.length) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        }
    });

    // Filter FAQs on typing
    faqSearchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        filterFaqList(query);
    });

    function filterFaqList(query) {
        faqItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (!query || text.includes(query)) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }
        });
    }

    // Clicking an FAQ in modal asks it in chat
    faqItems.forEach(item => {
        item.addEventListener("click", () => {
            const question = item.getAttribute("data-question");
            closeFaqModal();
            if (question) {
                sendMessage(question);
            }
        });
    });
});
