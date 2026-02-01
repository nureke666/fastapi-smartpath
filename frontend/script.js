const API_BASE = 'http://127.0.0.1:8000/api/v1';
const API_V2 = 'http://127.0.0.1:8000/api/v2';

// --- UI Helpers ---

function showToast(message, duration = 3000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

function showLoading(text = 'Loading...') {
    let overlay = document.getElementById('loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner"></div>
            <div id="loading-text" style="font-weight:500; color:#5f6368;">${text}</div>
        `;
        document.body.appendChild(overlay);
    } else {
        document.getElementById('loading-text').innerText = text;
    }
    overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}

// --- Auth Helpers ---

function getToken() {
    return localStorage.getItem('access_token');
}

function setToken(token) {
    localStorage.setItem('access_token', token);
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
}

function checkAuth() {
    if (!getToken()) {
        window.location.href = 'login.html';
    }
}

async function apiRequest(endpoint, method = 'GET', body = null, isV2 = false) {
    const headers = {
        'Content-Type': 'application/json'
    };

    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const baseUrl = isV2 ? API_V2 : API_BASE;
    const config = {
        method,
        headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${baseUrl}${endpoint}`, config);
        
        if (response.status === 401) {
            logout();
            return null;
        }
        
        if (response.status === 429) {
             throw new Error("Too many requests. Please wait a moment.");
        }

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'API Error');
        }

        return await response.json();
    } catch (error) {
        console.error('API Request Failed:', error);
        showToast(error.message); // Use Toast instead of Alert
        throw error;
    }
}

// --- Page Specific Logic ---

// Login / Register
async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    showLoading('Signing in...');
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: new URLSearchParams(formData) // x-www-form-urlencoded
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Login failed');
        }

        const data = await response.json();
        setToken(data.access_token);
        window.location.href = 'index.html';
    } catch (error) {
        showToast(error.message);
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    showLoading('Creating account...');
    try {
        await apiRequest('/auth/register', 'POST', { email, password });
        showToast('Registration successful! Please login.');
        toggleAuthMode();
    } catch (e) {
        // Error handled in apiRequest
    } finally {
        hideLoading();
    }
}

// Dashboard (Index)
async function loadRoadmaps() {
    // showLoading('Loading roadmaps...'); // Optional, might be too flashy for fast loads
    try {
        const roadmaps = await apiRequest('/roadmaps/');
        const container = document.getElementById('roadmap-list');
        container.innerHTML = '';

        if (!roadmaps || roadmaps.length === 0) {
            container.innerHTML = '<p>No roadmaps found. Create one!</p>';
            return;
        }

        roadmaps.forEach(r => {
            const el = document.createElement('div');
            el.className = 'card roadmap-item';
            el.innerHTML = `
                <h3>${r.title}</h3>
                <p style="color: var(--text-secondary); margin-bottom: 16px;">${r.description || 'No description'}</p>
                <div class="actions">
                    <button onclick="startOrViewRoadmap(${r.id})" class="btn btn-secondary">
                        Open <span class="material-icons" style="font-size: 18px;">arrow_forward</span>
                    </button>
                </div>
            `;
            container.appendChild(el);
        });
    } catch (e) {
        console.error(e);
    } finally {
        // hideLoading();
    }
}

async function startOrViewRoadmap(id) {
    window.location.href = `roadmap.html?id=${id}`;
}

// Generate V2
async function handleGenerate(event) {
    event.preventDefault();
    const form = event.target;
    const data = {
        role: form.role.value,
        current_stack: form.current_stack.value,
        goal: form.goal.value,
        hours_per_week: parseInt(form.hours.value),
        learning_style: form.style.value,
        focus: form.focus.value,
        constraints: "free-only"
    };

    showLoading('AI is generating your roadmap...\nThis may take up to 30 seconds.');

    try {
        const result = await apiRequest('/roadmaps/generate', 'POST', data, true); // isV2=true
        console.log(result);
        showToast('Roadmap Generated Successfully!');
        setTimeout(() => {
            window.location.href = 'index.html'; 
        }, 1000);
    } catch (e) {
        // Error handled
    } finally {
        hideLoading();
    }
}

// Roadmap Detail
let currentRoadmapNodes = []; // Store nodes to access resources later
let currentRoadmapTitle = ""; // For chat context

async function loadRoadmapDetail() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    if (!id) return;

    showLoading('Loading details...');
    try {
        let roadmap = await apiRequest(`/roadmaps/${id}`);
        currentRoadmapNodes = roadmap.nodes; // Save for later
        currentRoadmapTitle = roadmap.title;
        renderRoadmap(roadmap);
    } catch (e) {
        console.error(e);
    } finally {
        hideLoading();
    }
}

async function startRoadmap() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    showLoading('Initializing...');
    await apiRequest(`/roadmaps/${id}/start`, 'POST');
    location.reload();
}

function renderRoadmap(roadmap) {
    document.getElementById('r-title').innerText = roadmap.title;
    document.getElementById('r-desc').innerText = roadmap.description;
    
    const list = document.getElementById('node-list');
    list.innerHTML = '';

    if (!roadmap.nodes || roadmap.nodes.length === 0) {
        list.innerHTML = '<li>No nodes found.</li>';
        return;
    }

    let hasStarted = false;

    roadmap.nodes.forEach(node => {
        const status = node.status ? node.status.toLowerCase() : 'locked';
        if (status !== 'locked') hasStarted = true;

        const li = document.createElement('li');
        li.className = `node-item status-${status}`;
        
        let actionBtns = '';
        let icon = 'lock'; // default

        if (status === 'available') {
            icon = 'play_circle_outline';
            actionBtns = `
                <button class="btn btn-sm btn-secondary" onclick="openLearn(${node.id})" style="margin-right: 10px;">
                    <span class="material-icons" style="font-size: 16px;">menu_book</span> Learn
                </button>
                <button class="btn btn-sm" onclick="openQuiz(${node.id})">
                    <span class="material-icons" style="font-size: 16px;">quiz</span> Take Quiz
                </button>
            `;
        } else if (status === 'completed') {
            icon = 'check_circle';
            actionBtns = `
                <button class="btn btn-sm btn-secondary" onclick="openLearn(${node.id})" style="margin-right: 10px;">
                    <span class="material-icons" style="font-size: 16px;">menu_book</span> Review
                </button>
                <span style="color: #137333; display: inline-flex; align-items: center; gap: 5px;">
                    <span class="material-icons">check</span> Completed
                </span>
            `;
        } else {
            actionBtns = `<span style="color: var(--text-secondary); display: flex; align-items: center; gap: 5px;">
                            <span class="material-icons" style="font-size: 18px;">lock</span> Locked
                         </span>`;
        }

        li.innerHTML = `
            <div class="node-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <span class="status-badge">${status}</span>
                        <h4 style="margin: 8px 0;">${node.title}</h4>
                        <p style="color: var(--text-secondary); font-size: 14px;">${node.description_content || ''}</p>
                    </div>
                </div>
                <div style="margin-top:16px; border-top: 1px solid #f1f3f4; padding-top: 12px;">
                    ${actionBtns}
                </div>
            </div>
        `;
        list.appendChild(li);
    });

    if (!hasStarted) {
        const header = document.querySelector('.roadmap-header');
        // Check if button already exists to avoid dupes
        if (!document.getElementById('start-btn')) {
            const startBtn = document.createElement('button');
            startBtn.id = 'start-btn';
            startBtn.className = 'btn';
            startBtn.innerHTML = '<span class="material-icons">rocket_launch</span> Start This Career Path';
            startBtn.onclick = startRoadmap;
            header.appendChild(startBtn);
        }
    }
}

// Learn Modal Logic
function openLearn(nodeId) {
    const node = currentRoadmapNodes.find(n => n.id === nodeId);
    if (!node) return;

    const modal = document.getElementById('learn-modal');
    const title = document.getElementById('learn-title');
    const content = document.getElementById('learn-content');

    title.innerText = node.title;
    
    let html = '';
    
    // Summary
    if (node.summary) {
        html += `
            <div style="margin-bottom: 24px;">
                <h3 style="font-size: 18px; margin-bottom: 10px;">Summary</h3>
                <p style="line-height: 1.6; color: var(--text-color);">${node.summary}</p>
            </div>
        `;
    } else {
        html += `<p style="color: var(--text-secondary);">No summary available.</p>`;
    }

    // Resources
    if (node.resources && node.resources.length > 0) {
        html += `<h3 style="font-size: 18px; margin-bottom: 10px;">Resources</h3>`;
        html += `<ul style="padding-left: 20px;">`;
        node.resources.forEach(res => {
            html += `
                <li style="margin-bottom: 10px;">
                    <a href="${res.url}" target="_blank" style="color: var(--google-blue); text-decoration: none; font-weight: 500;">
                        ${res.title} <span class="material-icons" style="font-size: 14px; vertical-align: middle;">open_in_new</span>
                    </a>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
                        ${res.type} • ${res.level || 'General'}
                    </div>
                    ${res.why_this ? `<div style="font-size: 13px; margin-top: 4px; color: #444;">💡 ${res.why_this}</div>` : ''}
                </li>
            `;
        });
        html += `</ul>`;
    } else {
        html += `<p style="color: var(--text-secondary);">No specific resources found.</p>`;
    }

    content.innerHTML = html;
    modal.style.display = 'block';
}

function closeLearn() {
    document.getElementById('learn-modal').style.display = 'none';
}


// Quiz Logic
let currentQuizNodeId = null;
let currentQuestions = [];

async function openQuiz(nodeId) {
    currentQuizNodeId = nodeId;
    const modal = document.getElementById('quiz-modal');
    const content = document.getElementById('quiz-content');
    
    content.innerHTML = '<div class="spinner" style="margin: 20px auto;"></div>';
    modal.style.display = 'block';

    try {
        const questions = await apiRequest(`/quiz/node/${nodeId}`);
        currentQuestions = questions;
        renderQuiz(questions);
    } catch (e) {
        content.innerHTML = '<p>Error loading quiz.</p>';
    }
}

function renderQuiz(questions) {
    const container = document.getElementById('quiz-content');
    container.innerHTML = '';

    if (!questions || questions.length === 0) {
        container.innerHTML = '<p>No questions for this module. Auto-completing...</p>';
        submitQuiz([]); // Auto submit empty
        return;
    }

    questions.forEach((q, idx) => {
        const qDiv = document.createElement('div');
        qDiv.className = 'question-block';
        qDiv.style.marginBottom = '24px';
        qDiv.innerHTML = `<p style="font-weight: 500; margin-bottom: 12px;">${idx+1}. ${q.text}</p>`;
        
        const optsDiv = document.createElement('div');
        q.options.forEach((opt, optIdx) => {
            const btn = document.createElement('button');
            btn.className = 'btn option-btn';
            btn.innerText = opt;
            btn.onclick = () => selectOption(idx, optIdx, btn);
            optsDiv.appendChild(btn);
        });
        
        qDiv.appendChild(optsDiv);
        container.appendChild(qDiv);
    });

    const submitBtn = document.createElement('button');
    submitBtn.className = 'btn';
    submitBtn.style.marginTop = '20px';
    submitBtn.style.width = '100%';
    submitBtn.innerHTML = 'Submit Answers';
    submitBtn.onclick = submitQuizAnswers;
    container.appendChild(submitBtn);
}

let userAnswers = {}; // { questionIndex: optionIndex }

function selectOption(qIdx, optIdx, btnElement) {
    userAnswers[qIdx] = optIdx;
    // Visually update
    const parent = btnElement.parentElement;
    Array.from(parent.children).forEach(c => c.classList.remove('selected'));
    btnElement.classList.add('selected');
}

async function submitQuizAnswers() {
    const payload = currentQuestions.map((q, idx) => ({
        question_id: q.id,
        selected_option_index: userAnswers[idx] !== undefined ? userAnswers[idx] : -1
    }));

    showLoading('Checking answers...');
    try {
        const result = await apiRequest(`/quiz/node/${currentQuizNodeId}/submit`, 'POST', payload);
        
        if (result.passed) {
            showToast(result.message || 'Quiz Passed! Module Completed.');
            document.getElementById('quiz-modal').style.display = 'none';
            // Wait a bit before reloading so user sees the toast
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            // Failed
            showToast(result.message || 'You did not pass. Try again.', 4000);
            // Do NOT close modal, let them try again
        }

    } catch (e) {
        // Error handled by apiRequest (shows toast)
    } finally {
        hideLoading();
    }
}

function closeQuiz() {
    document.getElementById('quiz-modal').style.display = 'none';
}

// --- Chat Logic ---
function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    if (chatWindow.style.display === 'flex') {
        chatWindow.style.display = 'none';
    } else {
        chatWindow.style.display = 'flex';
    }
}

function handleChatKey(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Add user message to UI
    addMessageToChat(message, 'user');
    input.value = '';

    // Show typing indicator (fake)
    const typingId = addMessageToChat('Thinking...', 'ai');

    try {
        const response = await apiRequest('/chat/ask', 'POST', {
            message: message,
            context_topic: currentRoadmapTitle || "General Programming"
        });

        // Remove typing indicator and add real response
        document.getElementById(typingId).remove();
        const msgId = addMessageToChat(response.reply, 'ai', response.message_id);

    } catch (e) {
        document.getElementById(typingId).innerText = "Error: " + e.message;
    }
}

function addMessageToChat(text, sender, messageId = null) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    let contentHtml = text;
    
    // Add like/dislike buttons for AI messages
    if (sender === 'ai' && messageId) {
        contentHtml += `
            <div style="margin-top: 8px; display: flex; gap: 10px; justify-content: flex-end;">
                <span class="material-icons" style="font-size: 16px; cursor: pointer; color: #aaa;" onclick="likeMessage(${messageId}, true, this)">thumb_up</span>
                <span class="material-icons" style="font-size: 16px; cursor: pointer; color: #aaa;" onclick="likeMessage(${messageId}, false, this)">thumb_down</span>
            </div>
        `;
    }
    
    msgDiv.innerHTML = contentHtml;
    
    // Generate a random ID for typing indicator removal
    const id = 'msg-' + Math.random().toString(36).substr(2, 9);
    msgDiv.id = id;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight; // Auto scroll to bottom
    return id;
}

async function likeMessage(msgId, isLiked, btnElement) {
    try {
        await apiRequest(`/chat/${msgId}/like?is_liked=${isLiked}`, 'POST');
        
        // Visual feedback
        const parent = btnElement.parentElement;
        Array.from(parent.children).forEach(c => c.style.color = '#aaa'); // Reset
        btnElement.style.color = isLiked ? '#1a73e8' : '#d93025'; // Blue or Red
        
        showToast('Thanks for feedback!');
    } catch (e) {
        console.error(e);
    }
}
