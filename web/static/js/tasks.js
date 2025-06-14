/**
 * Tasks Page JavaScript - Read-Only Monitoring Mode
 * Handles task monitoring and log viewing (admin controls disabled for security)
 */

// Global state
let isRefreshing = false;
let runningTasksCount = 0;
let readOnlyMode = false;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function () {
    initializePage();
    setupAutoRefresh();
    addFadeInAnimations();
});

/**
 * Initialize the tasks page
 */
function initializePage() {
    // Set initial data from global data
    if (window.TERRASCAN_TASKS_DATA) {
        runningTasksCount = window.TERRASCAN_TASKS_DATA.runningTasksCount || 0;
        readOnlyMode = window.TERRASCAN_TASKS_DATA.readOnlyMode || false;
    } else {
        // Fallback: get from DOM
        const statsElement = document.querySelector('.stats-card .text-warning');
        if (statsElement) {
            runningTasksCount = parseInt(statsElement.textContent) || 0;
        }
        readOnlyMode = true; // Default to read-only for safety
    }

    // Setup event listeners
    setupEventListeners();

    // Show read-only mode status
    if (readOnlyMode) {
        console.log('Tasks page initialized in READ-ONLY mode');
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Refresh button (always available)
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshAllData);
    }

    // Admin controls only in non-read-only mode
    if (!readOnlyMode) {
        const runAllBtn = document.getElementById('run-all-btn');
        if (runAllBtn) {
            runAllBtn.addEventListener('click', runAllTasks);
        }
    }
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' :
        type === 'error' ? 'alert-danger' : 'alert-info';

    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show toast-notification`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

/**
 * Run a single task (disabled in read-only mode)
 */
function runTask(taskName) {
    if (readOnlyMode) {
        showNotification('❌ Task execution disabled. Admin-only control via environment variables.', 'error');
        return;
    }

    const spinner = document.getElementById(`spinner-${taskName}`);
    const button = event.target.closest('button');
    const taskCard = document.querySelector(`[data-task-name="${taskName}"]`);

    if (!button || !spinner) {
        console.error('Task elements not found:', taskName);
        return;
    }

    // Show loading state
    spinner.style.display = 'inline-block';
    button.disabled = true;
    button.classList.add('btn-loading');
    taskCard.classList.add('updating');

    fetch(`/api/tasks/${taskName}/run`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`✅ Task "${taskName}" started successfully! 
                            Duration: ${data.duration.toFixed(1)}s, 
                            Records: ${data.records_processed}`, 'success');

                // Mark task as running
                taskCard.classList.add('task-running');

                // Refresh data after a short delay
                setTimeout(() => refreshAllData(), 2000);
            } else {
                showNotification(`❌ Failed to run task "${taskName}": ${data.error}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error running task:', error);
            showNotification(`❌ Error running task "${taskName}": ${error.message}`, 'error');
        })
        .finally(() => {
            // Reset button state
            spinner.style.display = 'none';
            button.disabled = false;
            button.classList.remove('btn-loading');
            taskCard.classList.remove('updating');
        });
}

/**
 * Toggle task active/inactive status (disabled in read-only mode)
 */
function toggleTask(taskName, checkbox) {
    if (readOnlyMode) {
        showNotification('❌ Task toggle disabled. Admin-only control via environment variables.', 'error');
        // Revert checkbox
        checkbox.checked = !checkbox.checked;
        return;
    }

    const taskCard = document.querySelector(`[data-task-name="${taskName}"]`);

    if (!taskCard) {
        console.error('Task card not found:', taskName);
        return;
    }

    taskCard.classList.add('updating');

    fetch(`/api/tasks/${taskName}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`🔄 ${data.message}`, 'success');

                // Update task card styling
                const runButton = taskCard.querySelector('.run-button');

                if (data.active) {
                    taskCard.classList.remove('task-inactive');
                    taskCard.classList.add('task-active');
                    if (runButton) runButton.disabled = false;
                } else {
                    taskCard.classList.remove('task-active');
                    taskCard.classList.add('task-inactive');
                    if (runButton) runButton.disabled = true;
                }
            } else {
                showNotification(`❌ Failed to toggle task: ${data.error}`, 'error');
                // Revert checkbox
                checkbox.checked = !checkbox.checked;
            }
        })
        .catch(error => {
            console.error('Error toggling task:', error);
            showNotification(`❌ Error toggling task: ${error.message}`, 'error');
            checkbox.checked = !checkbox.checked;
        })
        .finally(() => {
            taskCard.classList.remove('updating');
        });
}

/**
 * Show task logs in modal (always available)
 */
function showTaskLogs(taskName) {
    const modal = new bootstrap.Modal(document.getElementById('logsModal'));
    const modalTitle = document.querySelector('#logsModal .modal-title');
    const logsContent = document.getElementById('logs-content');

    if (!modal || !modalTitle || !logsContent) {
        console.error('Modal elements not found');
        return;
    }

    modalTitle.textContent = `Task Logs: ${taskName}`;
    logsContent.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';

    modal.show();

    fetch(`/api/tasks/${taskName}/logs`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let html = '';

                if (data.logs.length === 0) {
                    html = '<div class="text-center text-muted py-4">No logs found for this task</div>';
                } else {
                    data.logs.forEach(log => {
                        const statusClass = log.exit_code === 0 ? 'log-success' :
                            log.exit_code === null ? 'log-running' : 'log-error';
                        const statusText = log.exit_code === 0 ? 'Success' :
                            log.exit_code === null ? 'Running' : 'Failed';
                        const badgeClass = log.exit_code === 0 ? 'bg-success' :
                            log.exit_code === null ? 'bg-warning' : 'bg-danger';

                        html += `
                        <div class="log-entry ${statusClass}">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <strong>${log.started_at}</strong>
                                    <span class="badge bg-light text-dark ms-2">${log.triggered_by || 'system'}</span>
                                </div>
                                <span class="badge ${badgeClass}">
                                    ${statusText}
                                </span>
                            </div>
                            ${log.records_processed ? `<div class="small text-muted mt-1">Records processed: ${log.records_processed}</div>` : ''}
                            ${log.stderr ? `<div class="small text-danger mt-2"><strong>Error:</strong> ${escapeHtml(log.stderr)}</div>` : ''}
                            ${log.stdout ? `<div class="small text-muted mt-2"><strong>Output:</strong> ${escapeHtml(log.stdout.substring(0, 500))}${log.stdout.length > 500 ? '...' : ''}</div>` : ''}
                        </div>
                    `;
                    });
                }

                logsContent.innerHTML = html;
            } else {
                logsContent.innerHTML = `<div class="alert alert-danger">Failed to load logs: ${data.error}</div>`;
            }
        })
        .catch(error => {
            console.error('Error loading logs:', error);
            logsContent.innerHTML = `<div class="alert alert-danger">Error loading logs: ${error.message}</div>`;
        });
}

/**
 * Run all active tasks (disabled in read-only mode)
 */
function runAllTasks() {
    if (readOnlyMode) {
        showNotification('❌ Bulk task execution disabled. Admin-only control via environment variables.', 'error');
        return;
    }

    if (isRefreshing) return;

    const button = document.getElementById('run-all-btn');
    if (!button) return;

    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Running...';

    // Get all active tasks
    const activeTasks = Array.from(document.querySelectorAll('.task-active[data-task-name]'))
        .map(card => card.dataset.taskName);

    if (activeTasks.length === 0) {
        showNotification('No active tasks to run', 'info');
        resetRunAllButton(button);
        return;
    }

    let completed = 0;
    let successful = 0;
    const total = activeTasks.length;

    activeTasks.forEach(taskName => {
        fetch(`/api/tasks/${taskName}/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) successful++;
                completed++;

                if (completed === total) {
                    showNotification(`🚀 Started ${successful}/${total} tasks successfully`, 'success');
                    setTimeout(() => refreshAllData(), 3000);
                    resetRunAllButton(button);
                }
            })
            .catch(error => {
                console.error('Error running task:', taskName, error);
                completed++;

                if (completed === total) {
                    resetRunAllButton(button);
                }
            });
    });
}

/**
 * Reset run all button state
 */
function resetRunAllButton(button) {
    button.disabled = false;
    button.innerHTML = '<i class="fas fa-play-circle"></i> Run All Active';
}

/**
 * Refresh all data by reloading the page
 */
function refreshAllData() {
    if (isRefreshing) return;

    isRefreshing = true;
    const button = document.getElementById('refresh-btn');

    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    }

    // Reload the page to get fresh data
    setTimeout(() => {
        window.location.reload();
    }, 1000);
}

/**
 * Setup auto-refresh for running tasks status
 */
function setupAutoRefresh() {
    // Check task status every 30 seconds
    setInterval(() => {
        if (!isRefreshing) {
            checkTaskStatus();
        }
    }, 30000);
}

/**
 * Check if task status has changed
 */
function checkTaskStatus() {
    fetch('/api/tasks/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const currentRunningTasks = data.status.running_tasks || 0;

                // If running tasks count changed, refresh page
                if (currentRunningTasks !== runningTasksCount) {
                    console.log('Running tasks count changed, refreshing page');
                    refreshAllData();
                }
            }
        })
        .catch(error => {
            console.log('Status check failed:', error);
        });
}

/**
 * Add fade-in animation to task cards
 */
function addFadeInAnimations() {
    const taskCards = document.querySelectorAll('.task-card');
    taskCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Utility function to format time
 */
function formatTime(dateString) {
    if (!dateString) return 'Never';

    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    // If less than a minute ago
    if (diff < 60000) {
        return 'Just now';
    }

    // If less than an hour ago
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    }

    // If less than a day ago
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }

    // Otherwise show the date
    return date.toLocaleDateString();
}

// Export functions for global access (but with read-only restrictions)
window.runTask = runTask;
window.toggleTask = toggleTask;
window.showTaskLogs = showTaskLogs;
window.runAllTasks = runAllTasks;
window.refreshAllData = refreshAllData; 
