/**
 * CPBFI Helpdesk Chatbot Widget
 * Drop-in script — zero dependencies, self-contained.
 *
 * Usage: <script src="https://your-server.com/widget/chatbot.js"></script>
 */
(function () {
    'use strict';

    // --- Auto-detect API base URL from script src ---
    const scripts = document.querySelectorAll('script[src]');
    let API_BASE = '';
    for (const s of scripts) {
        if (s.src.includes('chatbot.js')) {
            const url = new URL(s.src);
            API_BASE = url.origin;
            break;
        }
    }
    if (!API_BASE) API_BASE = window.location.origin;

    const API = {
        start: () => API_BASE + '/api/session/start',
        chat: () => API_BASE + '/api/chat',
    };

    // --- Load CSS ---
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = API_BASE + '/widget/chatbot.css';
    document.head.appendChild(cssLink);

    // --- Session Management ---
    const SESSION_KEY = 'cpbfi_cb_session';

    function getSession() {
        try { return sessionStorage.getItem(SESSION_KEY); } catch { return null; }
    }
    function setSession(id) {
        try { sessionStorage.setItem(SESSION_KEY, id); } catch { /* noop */ }
    }

    // --- Build DOM ---
    function createWidget() {
        // Bubble
        const bubble = document.createElement('button');
        bubble.className = 'cpbfi-cb-bubble';
        bubble.innerHTML = '💬';
        bubble.setAttribute('aria-label', 'Open chat');
        bubble.id = 'cpbfi-cb-bubble';
        document.body.appendChild(bubble);

        // Panel
        const panel = document.createElement('div');
        panel.className = 'cpbfi-cb-panel';
        panel.id = 'cpbfi-cb-panel';
        panel.innerHTML = `
            <div class="cpbfi-cb-header">
                <div class="cpbfi-cb-header-icon">🎓</div>
                <div class="cpbfi-cb-header-info">
                    <div class="cpbfi-cb-header-title">CPBFI Helpdesk</div>
                    <div class="cpbfi-cb-header-subtitle">We typically reply instantly</div>
                </div>
                <button class="cpbfi-cb-header-close" id="cpbfi-cb-close" aria-label="Close chat">✕</button>
            </div>
            <div class="cpbfi-cb-messages" id="cpbfi-cb-messages"></div>
            <div class="cpbfi-cb-input-area">
                <input class="cpbfi-cb-input" id="cpbfi-cb-input"
                       type="text" placeholder="Type a message..."
                       autocomplete="off" />
                <button class="cpbfi-cb-send" id="cpbfi-cb-send" aria-label="Send">➤</button>
            </div>
            <div class="cpbfi-cb-powered">Powered by CPBFI</div>
        `;
        document.body.appendChild(panel);

        return { bubble, panel };
    }

    // --- Markdown-lite parser ---
    function parseMd(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/_(.+?)_/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    // --- Render Functions ---
    function addMessage(container, role, text, buttons) {
        // Message bubble
        if (text) {
            const msg = document.createElement('div');
            msg.className = `cpbfi-cb-msg cpbfi-cb-msg-${role}`;
            msg.innerHTML = parseMd(text);
            container.appendChild(msg);
        }

        // Buttons
        if (buttons && buttons.length > 0 && role === 'bot') {
            const btnWrap = document.createElement('div');
            btnWrap.className = 'cpbfi-cb-buttons';
            buttons.forEach(b => {
                const btn = document.createElement('button');
                btn.className = 'cpbfi-cb-btn';
                btn.textContent = b.text;
                btn.dataset.cb = b.cb;
                btn.addEventListener('click', () => handleButtonClick(b.cb, b.text));
                btnWrap.appendChild(btn);
            });
            container.appendChild(btnWrap);
        }

        scrollToBottom(container);
    }

    function showTyping(container) {
        const typing = document.createElement('div');
        typing.className = 'cpbfi-cb-typing';
        typing.id = 'cpbfi-cb-typing';
        typing.innerHTML = `
            <div class="cpbfi-cb-typing-dot"></div>
            <div class="cpbfi-cb-typing-dot"></div>
            <div class="cpbfi-cb-typing-dot"></div>
        `;
        container.appendChild(typing);
        scrollToBottom(container);
    }

    function hideTyping() {
        const t = document.getElementById('cpbfi-cb-typing');
        if (t) t.remove();
    }

    function scrollToBottom(container) {
        requestAnimationFrame(() => {
            container.scrollTop = container.scrollHeight;
        });
    }

    function disableOldButtons() {
        const buttons = document.querySelectorAll('.cpbfi-cb-buttons');
        buttons.forEach((wrap, idx) => {
            if (idx < buttons.length - 1) {
                wrap.querySelectorAll('.cpbfi-cb-btn').forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.4';
                    btn.style.cursor = 'default';
                    btn.style.pointerEvents = 'none';
                });
            }
        });
    }

    // --- API Calls ---
    let sessionId = getSession();
    let isSending = false;

    async function startSession(container) {
        try {
            const res = await fetch(API.start(), { method: 'POST' });
            const data = await res.json();
            sessionId = data.session_id;
            setSession(sessionId);
            addMessage(container, 'bot', data.message.text, data.message.buttons);
        } catch (err) {
            addMessage(container, 'bot', '⚠️ Could not connect to the server. Please try again later.', []);
            console.error('CPBFI Chatbot: session start failed', err);
        }
    }

    async function sendChat(container, message, callbackData) {
        if (isSending) return;
        isSending = true;

        const sendBtn = document.getElementById('cpbfi-cb-send');
        if (sendBtn) sendBtn.disabled = true;

        // Show user message
        if (message) {
            addMessage(container, 'user', message, null);
        }
        if (callbackData && !message) {
            // Button click — don't show user bubble
        }

        disableOldButtons();
        showTyping(container);

        try {
            const body = { session_id: sessionId };
            if (message) body.message = message;
            if (callbackData) body.callback_data = callbackData;

            const res = await fetch(API.chat(), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await res.json();

            hideTyping();

            if (data.text === 'Session expired. Please refresh the page.') {
                sessionId = null;
                try { sessionStorage.removeItem(SESSION_KEY); } catch { }
                await startSession(container);
                return;
            }

            addMessage(container, 'bot', data.text, data.buttons);
        } catch (err) {
            hideTyping();
            addMessage(container, 'bot', '⚠️ Something went wrong. Please try again.', []);
            console.error('CPBFI Chatbot: send failed', err);
        } finally {
            isSending = false;
            if (sendBtn) sendBtn.disabled = false;
        }
    }

    function handleButtonClick(cb, text) {
        const container = document.getElementById('cpbfi-cb-messages');
        if (!container || !sessionId) return;
        // Show what user clicked in a subtle way
        addMessage(container, 'user', text, null);
        sendChat(container, null, cb);
    }

    // --- Init ---
    function init() {
        const { bubble, panel } = createWidget();
        const container = document.getElementById('cpbfi-cb-messages');
        const input = document.getElementById('cpbfi-cb-input');
        const sendBtn = document.getElementById('cpbfi-cb-send');
        const closeBtn = document.getElementById('cpbfi-cb-close');
        let isOpen = false;

        // Toggle chat
        function openChat() {
            isOpen = true;
            panel.classList.add('cb-open');
            bubble.classList.add('cb-hidden');
            input.focus();

            if (!sessionId) {
                startSession(container);
            }
        }

        function closeChat() {
            isOpen = false;
            panel.classList.remove('cb-open');
            bubble.classList.remove('cb-hidden');
        }

        bubble.addEventListener('click', openChat);
        closeBtn.addEventListener('click', closeChat);

        // Send message
        function send() {
            const text = input.value.trim();
            if (!text || !sessionId) return;
            input.value = '';
            sendChat(container, text, null);
        }

        sendBtn.addEventListener('click', send);
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
            }
        });

        // Close on Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && isOpen) closeChat();
        });
    }

    // Wait for DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
