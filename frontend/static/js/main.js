// Healthcare Predictive Analytics - Main JavaScript
// API interaction and app logic

const API_BASE = '/api';

// ===== API HELPER =====
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ===== AUTH FUNCTIONS =====
async function login(email, password) {
    return apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
    });
}

async function register(name, email, password, role = 'doctor') {
    return apiRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ name, email, password, role })
    });
}

async function logout() {
    return apiRequest('/auth/logout', {
        method: 'POST'
    });
}

// ===== PATIENT FUNCTIONS =====
async function addPatient(patientData) {
    return apiRequest('/patients/', {
        method: 'POST',
        body: JSON.stringify(patientData)
    });
}

async function getPatients(page = 1, search = '') {
    return apiRequest(`/patients/?page=${page}&search=${encodeURIComponent(search)}`);
}

async function getPatient(patientId) {
    return apiRequest(`/patients/${patientId}`);
}

async function getPatientPredictions(patientId) {
    return apiRequest(`/patients/${patientId}/predictions`);
}

async function getStatistics() {
    return apiRequest('/patients/stats');
}

// ===== PREDICTION FUNCTIONS =====
async function predictHeartDisease(data) {
    return apiRequest('/predict/heart', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

async function predictDiabetes(data) {
    return apiRequest('/predict/diabetes', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

async function getPredictionHistory(patientId = null) {
    const url = patientId ? `/predict/history?patient_id=${patientId}` : '/predict/history';
    return apiRequest(url);
}

// ===== UI HELPERS =====
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;font-size:1.5rem;cursor:pointer;color:inherit">&times;</button>
    `;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
}

function showLoading(button) {
    button.classList.add('btn-loading');
    button.disabled = true;
}

function hideLoading(button) {
    button.classList.remove('btn-loading');
    button.disabled = false;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getRiskColor(riskLevel) {
    const colors = {
        'Low': 'var(--risk-low)',
        'Medium': 'var(--risk-medium)',
        'High': 'var(--risk-high)'
    };
    return colors[riskLevel] || 'var(--gray-500)';
}

// ===== FORM VALIDATION =====
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateForm(formData, rules) {
    const errors = {};
    
    for (const [field, rule] of Object.entries(rules)) {
        const value = formData[field];
        
        if (rule.required && !value) {
            errors[field] = `${field} is required`;
        }
        
        if (rule.min && value < rule.min) {
            errors[field] = `${field} must be at least ${rule.min}`;
        }
        
        if (rule.max && value > rule.max) {
            errors[field] = `${field} must not exceed ${rule.max}`;
        }
        
        if (rule.email && !validateEmail(value)) {
            errors[field] = 'Invalid email format';
        }
    }
    
    return {
        isValid: Object.keys(errors).length === 0,
        errors
    };
}

function displayFormErrors(errors) {
    // Clear previous errors
    document.querySelectorAll('.form-error').forEach(el => el.remove());
    
    // Display new errors
    for (const [field, message] of Object.entries(errors)) {
        const input = document.querySelector(`[name="${field}"]`);
        if (input) {
            const error = document.createElement('div');
            error.className = 'form-error shake';
            error.textContent = message;
            input.parentNode.appendChild(error);
            input.classList.add('border-danger');
        }
    }
}

// ===== STORE PREDICTION RESULT =====
function storePredictionResult(result) {
    sessionStorage.setItem('lastPrediction', JSON.stringify(result));
}

function getStoredPrediction() {
    const data = sessionStorage.getItem('lastPrediction');
    return data ? JSON.parse(data) : null;
}

// Export functions for use in other scripts
window.healthcareApp = {
    api: {
        login,
        register,
        logout,
        addPatient,
        getPatients,
        getPatient,
        getPatientPredictions,
        getStatistics,
        predictHeartDisease,
        predictDiabetes,
        getPredictionHistory
    },
    ui: {
        showAlert,
        showLoading,
        hideLoading,
        formatDate,
        getRiskColor,
        validateForm,
        displayFormErrors
    },
    storage: {
        storePredictionResult,
        getStoredPrediction
    }
};
