document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    if (!chatInput) return; // Not on dashboard page

    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');
    const actionBtns = document.querySelectorAll('.action-btn');
    const chipBtns = document.querySelectorAll('.chip-btn');
    const taskTypeInput = document.getElementById('task-type');
    const currentModeBadge = document.getElementById('current-mode-badge');
    const errorMessage = document.getElementById('error-message');
    const charCount = document.getElementById('char-count');
    const clearChatBtn = document.getElementById('clear-chat-btn');

    // Auto-expand Textarea & Char Counter
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + 'px';
        if (charCount) {
            charCount.textContent = `${chatInput.value.length} chars`;
        }
    });

    // Handle Mode Switcher Cards
    actionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            actionBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const taskType = btn.dataset.task;
            taskTypeInput.value = taskType;
            
            if (btn.dataset.prompt) {
                chatInput.value = btn.dataset.prompt;
                chatInput.dispatchEvent(new Event('input'));
            }
            
            // Update UI badge mode indicator
            let modeText = 'Mode: General Chat';
            let badgeClass = 'badge badge-primary';

            if (taskType === 'structured') {
                modeText = 'Mode: Structured Format';
                badgeClass = 'badge badge-success';
            } else if (taskType === 'json') {
                modeText = 'Mode: JSON Auto-Refinement';
                badgeClass = 'badge badge-warning';
            } else if (taskType === 'cot') {
                modeText = 'Mode: Chain-of-Thought';
                badgeClass = 'badge badge-primary';
            }
            
            currentModeBadge.textContent = modeText;
            currentModeBadge.className = badgeClass;
            chatInput.focus();
        });
    });

    // Quick Preset Chips
    chipBtns.forEach(chip => {
        chip.addEventListener('click', () => {
            if (chip.dataset.preset) {
                chatInput.value = chip.dataset.preset;
                chatInput.dispatchEvent(new Event('input'));
                chatInput.focus();
            }
        });
    });

    // Clear Chat Action
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            chatHistory.innerHTML = `
                <div class="chat-bubble bot-bubble">
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <span class="badge badge-primary">PromptGenius Assistant</span>
                    </div>
                    <p>Chat cleared! Select a mode or type a new prompt to continue.</p>
                </div>
            `;
        });
    }

    // Keyboard navigation (Enter to send, Shift+Enter for newline)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendBtn.click();
        }
    });

    // Send Button Click Handler
    sendBtn.addEventListener('click', async () => {
        const prompt = chatInput.value.trim();
        const taskType = taskTypeInput.value;
        
        if (!prompt) return;

        // 1. Render User Message
        appendMessage(prompt, 'user');
        
        // 2. Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        if (charCount) charCount.textContent = '0 chars';
        errorMessage.classList.add('hidden');
        
        // 3. Render Typing Indicator
        const typingId = showTypingIndicator();
        
        // 4. Disable controls during API call
        chatInput.disabled = true;
        sendBtn.disabled = true;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, task_type: taskType })
            });

            // Remove typing indicator
            const typingElem = document.getElementById(typingId);
            if (typingElem) typingElem.remove();

            const contentType = response.headers.get('content-type');
            let data = {};

            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                if (response.status === 401 || response.redirected) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error(`Server error (${response.status}). If using Render, ensure GEMINI_API_KEY is set under Environment Variables.`);
            }

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                throw new Error(data.error || 'Failed to generate AI response.');
            }

            // 5. Append Assistant Response based on payload type
            if (data.type === 'cot') {
                appendCoTMessage(data.baseline_html, data.cot_html, data.status);
            } else {
                appendBotMessage(data.html, data.status, data.success);
            }

        } catch (error) {
            const typingElem = document.getElementById(typingId);
            if (typingElem) typingElem.remove();

            errorMessage.textContent = error.message;
            errorMessage.classList.remove('hidden');
        } finally {
            // Re-enable controls
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });

    function appendMessage(text, sender) {
        const div = document.createElement('div');
        div.className = `chat-bubble ${sender}-bubble`;
        div.textContent = text;
        chatHistory.appendChild(div);
        scrollToBottom();
    }

    function appendBotMessage(html, statusText, isSuccess) {
        const div = document.createElement('div');
        div.className = `chat-bubble bot-bubble markdown-body`;
        div.innerHTML = html;
        
        // Enhance Code Blocks with Copy Buttons
        enhanceCodeBlocks(div);

        if (statusText) {
            const statusDiv = document.createElement('div');
            statusDiv.className = `status-bar`;
            statusDiv.style.color = isSuccess !== false ? 'var(--accent-emerald)' : 'var(--accent-rose)';
            statusDiv.innerHTML = `${isSuccess !== false ? '✅' : '⚠️'} ${statusText}`;
            div.appendChild(statusDiv);
        }
        
        chatHistory.appendChild(div);
        scrollToBottom();
    }
    
    function appendCoTMessage(baselineHtml, cotHtml, statusText) {
        const div = document.createElement('div');
        div.className = `chat-bubble bot-bubble`;
        
        div.innerHTML = `
            <p style="margin-bottom: 1rem; color: var(--text-secondary); font-size: 0.92rem;">
                Processed using <strong>Baseline Zero-Shot</strong> vs. <strong>Chain-of-Thought (Step-by-Step) Reasoning</strong>:
            </p>
            <div class="cot-comparison">
                <div class="cot-panel markdown-body">
                    <h4>Direct Baseline</h4>
                    <div>${baselineHtml}</div>
                </div>
                <div class="cot-panel markdown-body" style="border-color: rgba(99, 102, 241, 0.3); background: rgba(99, 102, 241, 0.04);">

                    <h4>🧠 Chain-of-Thought</h4>
                    <div>${cotHtml}</div>
                </div>
            </div>
            <div class="status-bar" style="color: var(--accent-emerald);">
                ${statusText}
            </div>
        `;
        
        enhanceCodeBlocks(div);
        chatHistory.appendChild(div);
        scrollToBottom();
    }

    function enhanceCodeBlocks(container) {
        const pres = container.querySelectorAll('pre');
        pres.forEach(pre => {
            const wrapper = document.createElement('div');
            wrapper.className = 'code-wrapper';
            
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.textContent = 'Copy';
            
            copyBtn.addEventListener('click', () => {
                const codeText = pre.querySelector('code')?.innerText || pre.innerText;
                navigator.clipboard.writeText(codeText).then(() => {
                    copyBtn.textContent = 'Copied!';
                    copyBtn.style.color = '#6ee7b7';
                    setTimeout(() => {
                        copyBtn.textContent = 'Copy';
                        copyBtn.style.color = '';
                    }, 2000);
                });
            });

            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(pre);
            wrapper.appendChild(copyBtn);
        });
    }

    function showTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.className = `chat-bubble bot-bubble`;
        div.id = id;
        div.innerHTML = `
            <div class="typing-indicator">
                <span style="font-size: 0.85rem; color: var(--text-muted); margin-right: 0.5rem;">Gemini AI is thinking</span>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chatHistory.appendChild(div);
        scrollToBottom();
        return id;
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});
