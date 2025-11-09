// Document Builder - Content Intake Service UI JavaScript

const API_BASE_URL = '/v1/intake';

// Utility Functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(() => alertDiv.remove(), 5000);
}

function showLoading() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = 'loading-spinner';
    document.body.appendChild(spinner);
}

function hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.remove();
}

// Content Block Management
let contentBlocks = [];
let imageAssets = [];

function addContentBlock() {
    const type = document.getElementById('block-type').value;
    const text = document.getElementById('block-text').value;
    const level = document.getElementById('block-level').value || 0;

    if (!text) {
        showAlert('Please enter content text', 'error');
        return;
    }

    const block = {
        type: type,
        level: parseInt(level),
        sequence: contentBlocks.length,
        text: text
    };

    contentBlocks.push(block);
    renderContentBlocks();

    // Clear form
    document.getElementById('block-text').value = '';
    document.getElementById('block-level').value = '0';
}

function removeContentBlock(index) {
    contentBlocks.splice(index, 1);
    // Update sequences
    contentBlocks.forEach((block, i) => block.sequence = i);
    renderContentBlocks();
}

function renderContentBlocks() {
    const container = document.getElementById('content-blocks-list');
    if (!container) return;

    if (contentBlocks.length === 0) {
        container.innerHTML = '<p class="text-secondary">No content blocks added yet.</p>';
        return;
    }

    container.innerHTML = contentBlocks.map((block, index) => `
        <div class="content-block">
            <div class="content-block-header">
                <span class="content-block-type">${block.type} ${block.level > 0 ? `(Level ${block.level})` : ''}</span>
                <div class="content-block-actions">
                    <button class="btn btn-danger" onclick="removeContentBlock(${index})">Remove</button>
                </div>
            </div>
            <p>${block.text.substring(0, 100)}${block.text.length > 100 ? '...' : ''}</p>
        </div>
    `).join('');
}

// Image Management
function addImage() {
    const uri = document.getElementById('image-uri').value;
    const altText = document.getElementById('image-alt').value;
    const format = document.getElementById('image-format').value;

    if (!uri || !altText) {
        showAlert('Please enter image URI and alt text', 'error');
        return;
    }

    const image = {
        uri: uri,
        alt_text: altText,
        format: format,
        width_px: 1920,
        height_px: 1080,
        content_role: 'illustration'
    };

    imageAssets.push(image);
    renderImages();

    // Clear form
    document.getElementById('image-uri').value = '';
    document.getElementById('image-alt').value = '';
}

function removeImage(index) {
    imageAssets.splice(index, 1);
    renderImages();
}

function renderImages() {
    const container = document.getElementById('images-list');
    if (!container) return;

    if (imageAssets.length === 0) {
        container.innerHTML = '<p class="text-secondary">No images added yet.</p>';
        return;
    }

    container.innerHTML = imageAssets.map((image, index) => `
        <div class="content-block">
            <div class="content-block-header">
                <span class="content-block-type">${image.format.toUpperCase()} Image</span>
                <div class="content-block-actions">
                    <button class="btn btn-danger" onclick="removeImage(${index})">Remove</button>
                </div>
            </div>
            <p><strong>Alt:</strong> ${image.alt_text}</p>
            <p><small>${image.uri}</small></p>
        </div>
    `).join('');
}

// Session Creation
async function createSession(event) {
    event.preventDefault();

    if (contentBlocks.length === 0) {
        showAlert('Please add at least one content block', 'error');
        return;
    }

    const formData = {
        content_blocks: contentBlocks,
        images: imageAssets,
        design_intent: {
            purpose: document.getElementById('purpose').value,
            audience: document.getElementById('audience').value,
            tone: document.getElementById('tone').value,
            goals: ['clarity']
        },
        constraints: {
            visual_density: document.getElementById('visual-density').value
        }
    };

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/sessions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create session');
        }

        const session = await response.json();
        showAlert('Session created successfully!', 'success');

        // Redirect to session detail
        setTimeout(() => {
            window.location.href = `/sessions/${session.session_id}`;
        }, 1000);

    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Session Detail
let statusPollInterval = null;

async function loadSession(sessionId) {
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`);

        if (!response.ok) {
            throw new Error('Session not found');
        }

        const session = await response.json();
        renderSessionDetail(session);

        // Start polling if status indicates processing
        if (session.status && ['layout_queued', 'layout_processing'].includes(session.status)) {
            startStatusPolling(sessionId);
        } else if (session.status === 'layout_complete') {
            // Load artifacts immediately if already complete
            if (typeof window.loadArtifacts === 'function') {
                window.loadArtifacts(sessionId);
            }
        }

    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function checkSessionStatus(sessionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/check-status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            // If 404 or other error, stop polling to avoid spam
            if (response.status === 404) {
                stopStatusPolling();
            }
            return;
        }

        const session = await response.json();
        renderSessionDetail(session);

        // Stop polling if status is final
        if (session.status && !['layout_queued', 'layout_processing'].includes(session.status)) {
            stopStatusPolling();
            // Reload artifacts when complete
            if (session.status === 'layout_complete') {
                // Trigger artifacts reload - use window.loadArtifacts if available, otherwise fetch directly
                if (typeof window.loadArtifacts === 'function') {
                    window.loadArtifacts(sessionId);
                } else {
                    // Fallback: fetch artifacts directly
                    fetch(`/v1/intake/sessions/${sessionId}/artifacts`)
                        .then(r => r.json())
                        .then(data => {
                            const container = document.getElementById('artifacts-list');
                            if (container && data.artifacts && data.artifacts.length > 0) {
                                container.innerHTML = data.artifacts.map(artifact => `
                                    <div class="content-block">
                                        <p><strong>Type:</strong> ${artifact.type}</p>
                                        <p><strong>ID:</strong> ${artifact.artifact_id}</p>
                                        <p><strong>Status:</strong> <span class="status-badge status-${artifact.status}">${artifact.status}</span></p>
                                    </div>
                                `).join('');
                            }
                        })
                        .catch(err => console.error('Error loading artifacts:', err));
                }
            }
        }

    } catch (error) {
        console.error('Error checking session status:', error);
        // Stop polling on repeated errors to avoid spam
        stopStatusPolling();
    }
}

function startStatusPolling(sessionId) {
    // Clear any existing polling
    stopStatusPolling();
    
    // Poll every 2 seconds
    statusPollInterval = setInterval(() => {
        checkSessionStatus(sessionId);
    }, 2000);
}

function stopStatusPolling() {
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
}

function renderSessionDetail(session) {
    const container = document.getElementById('session-detail');
    if (!container) return;

    const statusClass = `status-${session.status.replace('_', '-')}`;

    container.innerHTML = `
        <div class="card">
            <div class="card-header">Session Information</div>
            <p><strong>Session ID:</strong> ${session.session_id}</p>
            <p><strong>Status:</strong> <span class="status-badge ${statusClass}">${session.status}</span></p>
            <p><strong>Created:</strong> ${new Date(session.created_at).toLocaleString()}</p>
            ${session.proposal_id ? `<p><strong>Proposal ID:</strong> ${session.proposal_id}</p>` : ''}
        </div>
    `;

    // Enable submit button if status is ready or draft
    const submitBtn = document.getElementById('submit-session-btn');
    if (submitBtn && ['draft', 'ready'].includes(session.status)) {
        submitBtn.disabled = false;
    }
}

// Submit Session
async function submitSession(sessionId) {
    if (!confirm('Submit this session for layout generation?')) {
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ layout_mode: 'rule_only' })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit session');
        }

        showAlert('Session submitted successfully!', 'success');

        // Reload session and start polling
        setTimeout(() => {
            loadSession(sessionId);
            startStatusPolling(sessionId);
        }, 1000);

    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on session detail page
    const sessionIdMeta = document.querySelector('meta[name="session-id"]');
    if (sessionIdMeta) {
        const sessionId = sessionIdMeta.content;
        loadSession(sessionId);
    }

    // Render initial empty states
    renderContentBlocks();
    renderImages();
});

// Clean up polling when page unloads
window.addEventListener('beforeunload', () => {
    stopStatusPolling();
});
