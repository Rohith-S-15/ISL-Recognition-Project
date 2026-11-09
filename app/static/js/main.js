// Main JavaScript for ISL Similarity Studio dashboard

// Utility function to show alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    const typeClass = type === 'danger' ? 'alert-danger-custom' : 
                      type === 'success' ? 'alert-success-custom' : 'alert-info-custom';
    alertDiv.className = `alert ${typeClass} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Initialize tooltips and active nav
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Activate nav links based on current page
    const currentLocation = location.pathname;
    const menuItems = document.querySelectorAll('.navbar-nav .nav-link');
    menuItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentLocation || 
            (currentLocation.startsWith(href) && href !== '/')) {
            item.classList.add('active');
        }
    });
});

// API helper
const API = {
    async get(endpoint) {
        try {
            const response = await fetch(endpoint);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    },

    async post(endpoint, data) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    },

    async upload(endpoint, file) {
        try {
            const formData = new FormData();
            formData.append('file', file);
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return null;
        }
    }
};

// Loading spinner
function showLoadingSpinner(message = 'Processing...') {
    return `
        <div class="text-center">
            <div class="spinner-border" role="status" style="color: var(--accent-light);">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2" style="color: var(--text-secondary);">${message}</p>
        </div>
    `;
}

// Confidence helpers
function getConfidenceClass(confidence) {
    if (confidence >= 0.85) return 'high';
    if (confidence >= 0.7) return 'medium';
    return 'low';
}

function getConfidencePercentage(confidence) {
    return (confidence * 100).toFixed(1) + '%';
}

// Create badge
function createBadge(text, type = 'accent') {
    return `<span class="badge bg-${type}">${text}</span>`;
}

// Export results as CSV
function exportResultsAsCSV(results) {
    let csv = 'Video Name,Recognized Word,Processing Time,Date\n';
    
    results.forEach(result => {
        const word = (result.generated_sentence || '').replace(/"/g, '""');
        csv += `"${result.video_name}","${word}",${result.processing_time},"${result.timestamp}"\n`;
    });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'isl_similarity_results.csv';
    a.click();
}
