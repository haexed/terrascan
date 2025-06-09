// 🌍 Terrascan - Shared JavaScript Functions

// Task Management Functions
function runTask(taskName) {
    if (confirm(`Run task: ${taskName}?`)) {
        const button = event.target;
        const originalText = button.innerHTML;

        // Show loading state
        button.innerHTML = '<span class="loading"></span> Running...';
        button.disabled = true;

        fetch(`/api/run_task/${taskName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Task completed! Processed ${data.records_processed} records in ${data.duration.toFixed(1)}s`);
                    window.location.reload();
                } else {
                    alert(`Task failed: ${data.error}`);
                }
            })
            .catch(error => {
                alert(`Error: ${error}`);
            })
            .finally(() => {
                // Restore button state
                button.innerHTML = originalText;
                button.disabled = false;
            });
    }
}

function viewSource(taskName) {
    fetch(`/api/task_source/${taskName}`)
        .then(response => response.json())
        .then(data => {
            if (data.source_code) {
                showSourceModal(data);
            } else {
                alert(`Error: ${data.error}`);
            }
        })
        .catch(error => alert(`Error fetching source: ${error}`));
}

function showSourceModal(data) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
        background: rgba(0,0,0,0.8); z-index: 1000; display: flex; 
        align-items: center; justify-content: center;
    `;

    modal.innerHTML = `
        <div style="background: white; width: 90%; height: 90%; border-radius: 10px; padding: 20px; overflow: auto;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>📄 ${data.task_name} - Source Code</h2>
                <button onclick="this.closest('.source-modal').remove()" style="background: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">✖️ Close</button>
            </div>
            <p><strong>File:</strong> ${data.file_path}</p>
            <p><strong>Function:</strong> ${data.function_name}</p>
            <p><strong>Command:</strong> ${data.command}</p>
            <hr>
            <pre style="background: #f8f9fa; padding: 20px; border-radius: 5px; overflow: auto; font-family: 'Monaco', 'Menlo', monospace; font-size: 14px; line-height: 1.4;">${escapeHtml(data.source_code)}</pre>
        </div>
    `;

    modal.className = 'source-modal';
    modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
    document.body.appendChild(modal);
}

// Log Management Functions
function toggleLogDetails(element) {
    const content = element.nextElementSibling;
    const isExpanded = content.classList.contains('expanded');

    if (isExpanded) {
        content.classList.remove('expanded');
        element.querySelector('.toggle-icon').textContent = '▶️';
    } else {
        content.classList.add('expanded');
        element.querySelector('.toggle-icon').textContent = '▼';
    }
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatCurrency(cents) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(cents / 100);
}

function formatDuration(seconds) {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${(seconds % 60).toFixed(0)}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

// Auto-refresh functionality
function enableAutoRefresh(intervalSeconds = 30) {
    if (typeof autoRefreshInterval !== 'undefined') {
        clearInterval(autoRefreshInterval);
    }

    window.autoRefreshInterval = setInterval(() => {
        // Only refresh if user is actively viewing the page
        if (!document.hidden) {
            window.location.reload();
        }
    }, intervalSeconds * 1000);
}

// Page-specific initialization
document.addEventListener('DOMContentLoaded', function () {
    // Add click handlers for expandable log items
    document.querySelectorAll('.log-header').forEach(header => {
        header.addEventListener('click', () => toggleLogDetails(header));
    });

    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;
            }
        });
    });

    // Auto-refresh for dashboard and system pages
    if (window.location.pathname === '/' || window.location.pathname === '/system') {
        enableAutoRefresh(30); // Refresh every 30 seconds
    }

    // Initialize operational page if we're on it
    initOperationalPage();
});

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary success message
        const notification = document.createElement('div');
        notification.textContent = 'Copied to clipboard!';
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; 
            background: #28a745; color: white; 
            padding: 10px 20px; border-radius: 5px; 
            z-index: 1001; animation: fadeInOut 2s ease-in-out;
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    }).catch(() => {
        alert('Failed to copy to clipboard');
    });
}

// Add fade animation for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateX(100%); }
        20% { opacity: 1; transform: translateX(0); }
        80% { opacity: 1; transform: translateX(0); }
        100% { opacity: 0; transform: translateX(100%); }
    }
`;
document.head.appendChild(style);

// Operational Costs Page Functions
function refreshRailwayData() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (!refreshBtn) return;

    const originalText = refreshBtn.innerHTML;

    refreshBtn.innerHTML = '<span class="loading"></span> Refreshing...';
    refreshBtn.disabled = true;

    fetch('/api/railway/refresh', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(result => {
            if (result.success && result.data) {
                alert('✅ Railway data refreshed successfully!');
                // Reload page to show updated data
                window.location.reload();
            } else {
                alert('⚠️ Error refreshing Railway data: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Railway refresh error:', error);
            alert('❌ Network error while refreshing Railway data');
        })
        .finally(() => {
            refreshBtn.innerHTML = originalText;
            refreshBtn.disabled = false;
        });
}

function updateDaysRemaining() {
    const daysRemainingEl = document.getElementById('days-remaining');
    if (!daysRemainingEl) return;

    // Calculate days remaining in current month
    const now = new Date();
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    const daysRemaining = lastDay.getDate() - now.getDate();

    daysRemainingEl.textContent = daysRemaining;
}

// Initialize operational page
function initOperationalPage() {
    if (window.location.pathname === '/operational') {
        updateDaysRemaining();

        // Update days remaining daily
        setInterval(updateDaysRemaining, 24 * 60 * 60 * 1000);
    }
} 
