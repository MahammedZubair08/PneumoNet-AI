// Global Variables
const API_URL = 'http://localhost:5000';
let currentThreshold = 0.5;
let currentPrediction = null;
let batchFiles = [];
let apiHealthy = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    checkApiStatus();
    loadTestImages();
    loadCurrentThreshold();
});

// ============= Setup Event Listeners =============
function setupEventListeners() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const batchFileInput = document.getElementById('batchFileInput');

    // Single File Upload
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // Batch File Input
    batchFileInput.addEventListener('change', (e) => {
        batchFiles = Array.from(e.target.files);
        displayBatchFiles();
    });
}

// ============= File Handling =============
function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please select an image file');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('fileName').textContent = '✓ ' + file.name;
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('fileInfo').classList.remove('hidden');
        document.getElementById('predictBtn').disabled = false;
        document.getElementById('clearBtn').style.display = 'inline-block';
        document.getElementById('infoMessage').classList.add('hidden');
        clearResults();
    };
    reader.readAsDataURL(file);
}

function displayBatchFiles() {
    const fileList = document.getElementById('batchFileList');
    fileList.innerHTML = '';
    
    if (batchFiles.length === 0) {
        document.getElementById('batchPredictBtn').style.display = 'none';
        fileList.innerHTML = '<p style="color: #999; font-size: 12px;">No files selected</p>';
        return;
    }

    batchFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <span class="file-item-name">${index + 1}. ${file.name}</span>
            <button class="file-item-remove" onclick="removeBatchFile(${index})">✕</button>
        `;
        fileList.appendChild(item);
    });

    document.getElementById('batchPredictBtn').style.display = 'inline-block';
}

function removeBatchFile(index) {
    batchFiles.splice(index, 1);
    displayBatchFiles();
}

function clearUpload() {
    document.getElementById('fileInput').value = '';
    document.getElementById('fileInfo').classList.add('hidden');
    document.getElementById('predictBtn').disabled = true;
    document.getElementById('clearBtn').style.display = 'none';
    document.getElementById('infoMessage').classList.remove('hidden');
}

// ============= API Calls =============
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            apiHealthy = true;
            showAlert(`API Status: Healthy ✓`, 'info');
            setTimeout(() => clearAlert(), 3000);
        }
    } catch (error) {
        apiHealthy = false;
        showAlert('API is not responding. Make sure the server is running.', 'error');
    }
}

async function predictImage() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files.length) {
        showError('Please select an image first');
        return;
    }

    showLoading(true);
    clearError();

    try {
        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            showError(error.error || 'Prediction failed');
            showLoading(false);
            return;
        }

        const data = await response.json();
        currentPrediction = data;
        displayResults(data);
    } catch (error) {
        console.error('Prediction error:', error);
        showError('Error communicating with API:  ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function batchPredict() {
    if (batchFiles.length === 0) {
        showError('Please select images first');
        return;
    }

    showLoading(true);
    clearError();

    try {
        const formData = new FormData();
        batchFiles.forEach(file => {
            formData.append('images', file);
        });

        const response = await fetch(`${API_URL}/predict-batch`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            showError(error.error || 'Batch prediction failed');
            showLoading(false);
            return;
        }

        const data = await response.json();
        displayBatchResults(data);
    } catch (error) {
        console.error('Batch prediction error:', error);
        showError('Error with batch prediction: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// ============= Results Display =============
function displayResults(data) {
    const prediction = data.prediction;
    const pneumoniaProbability = prediction.pneumonia_probability;
    const classifier = prediction.predicted_class;

    // Show result type
    const resultTypeDiv = document.getElementById('resultType');
    resultTypeDiv.textContent = classifier;
    resultTypeDiv.className = `result-type ${classifier === 'PNEUMONIA' ? 'pneumonia' : 'normal'}`;

    // Update confidence bar
    const confidence = prediction.confidence;
    const confidenceBarFill = document.getElementById('confidenceBarFill');
    confidenceBarFill.style.width = confidence + '%';
    confidenceBarFill.textContent = confidence.toFixed(1) + '%';
    document.getElementById('confidenceText').textContent = `${confidence.toFixed(2)}% confidence`;

    // Update probability circles
    document.getElementById('pneumoniaProb').textContent = (pneumoniaProbability * 100).toFixed(1) + '%';
    document.getElementById('normalProb').textContent = ((1 - pneumoniaProbability) * 100).toFixed(1) + '%';

    // Update detailed info
    document.getElementById('resultFilename').textContent = data.filename;
    document.getElementById('resultThreshold').textContent = prediction.threshold_used.toFixed(2);
    document.getElementById('resultTimestamp').textContent = new Date(data.timestamp).toLocaleString();

    // Show results card
    document.getElementById('resultsCard').classList.remove('hidden');
    document.getElementById('infoMessage').classList.add('hidden');
}

function displayBatchResults(data) {
    const resultsList = document.getElementById('batchResultsList');
    resultsList.innerHTML = '';

    data.predictions.forEach(pred => {
        const item = document.createElement('div');
        const isPositive = pred.predicted_class === 'PNEUMONIA';
        item.className = `batch-result-item ${isPositive ? 'pneumonia' : 'normal'}`;
        item.innerHTML = `
            <div class="batch-result-item-name">${pred.filename}</div>
            <div class="batch-result-item-class">
                ${pred.predicted_class} • ${pred.confidence.toFixed(2)}% confidence
            </div>
        `;
        resultsList.appendChild(item);
    });

    document.getElementById('batchResults').classList.remove('hidden');
    document.getElementById('infoMessage').classList.add('hidden');
    
    showAlert(`Processed ${data.successful_predictions} images successfully`, 'success');
}

function clearResults() {
    document.getElementById('resultsCard').classList.add('hidden');
    document.getElementById('batchResults').classList.add('hidden');
    document.getElementById('infoMessage').classList.remove('hidden');
    clearError();
}

function clearBatchResults() {
    document.getElementById('batchResults').classList.add('hidden');
    document.getElementById('batchFileInput').value = '';
    batchFiles = [];
    displayBatchFiles();
}

function downloadResult() {
    if (!currentPrediction) return;

    const result = {
        filename: currentPrediction.filename,
        prediction: currentPrediction.prediction,
        timestamp: currentPrediction.timestamp,
        analysis_date: new Date().toISOString()
    };

    const dataStr = JSON.stringify(result, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `pneumonia_analysis_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
}

// ============= Test Images =============
async function loadTestImages() {
    try {
        const response = await fetch('/api/test-images');
        if (!response.ok) return;
        
        const images = await response.json();
        const grid = document.getElementById('testImagesGrid');
        grid.innerHTML = '';

        images.forEach((imageName, index) => {
            const card = document.createElement('div');
            card.className = 'test-image-card';
            card.onclick = () => loadTestImage(imageName);
            card.innerHTML = `
                <img src="/test_images/${imageName}" alt="${imageName}" onerror="this.src='/static/img/placeholder.png'">
                <p>${imageName.substring(0, 20)}...</p>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.log('Could not load test images list');
    }
}

async function loadTestImage(imageName) {
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');

    // Load and display the test image
    const imgPath = `/test_images/${imageName}`;
    previewImage.src = imgPath;
    document.getElementById('fileName').textContent = '✓ ' + imageName;
    document.getElementById('fileInfo').classList.remove('hidden');
    document.getElementById('predictBtn').disabled = false;
    document.getElementById('clearBtn').style.display = 'inline-block';
    document.getElementById('infoMessage').classList.add('hidden');
    clearResults();

    // Create a blob from the test image for prediction
    try {
        const response = await fetch(imgPath);
        const blob = await response.blob();
        const file = new File([blob], imageName, { type: blob.type });
        
        // Create a DataTransfer object to set the file
        const dt = new DataTransfer();
        dt.items.add(file);
        fileInput.files = dt.files;
    } catch (error) {
        console.log('Will predict using form');
    }
}

// ============= Threshold Management =============
function openThresholdModal() {
    document.getElementById('thresholdModal').classList.remove('hidden');
    document.getElementById('thresholdSlider').value = currentThreshold;
    document.getElementById('thresholdInput').value = currentThreshold.toFixed(2);
    updateThresholdDisplay(currentThreshold);
}

function closeThresholdModal() {
    document.getElementById('thresholdModal').classList.add('hidden');
}

function updateThresholdDisplay(value) {
    const numValue = parseFloat(value);
    document.getElementById('thresholdInfo').textContent = `Current: ${numValue.toFixed(2)}`;
}

function updateThresholdSlider(value) {
    const numValue = Math.max(0, Math.min(1, parseFloat(value)));
    document.getElementById('thresholdSlider').value = numValue;
    updateThresholdDisplay(numValue);
}

async function applyThreshold() {
    const newThreshold = parseFloat(document.getElementById('thresholdSlider').value);
    
    try {
        const response = await fetch(`${API_URL}/threshold`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ threshold: newThreshold })
        });

        if (response.ok) {
            currentThreshold = newThreshold;
            showAlert(`Threshold updated to ${newThreshold.toFixed(2)}`, 'success');
            closeThresholdModal();
            setTimeout(() => clearAlert(), 3000);
        } else {
            showError('Failed to update threshold');
        }
    } catch (error) {
        showError('Error updating threshold: ' + error.message);
    }
}

async function loadCurrentThreshold() {
    try {
        const response = await fetch(`${API_URL}/threshold`);
        if (response.ok) {
            const data = await response.json();
            currentThreshold = data.current_threshold;
        }
    } catch (error) {
        console.log('Could not load current threshold');
    }
}

// ============= UI Helpers =============
function showLoading(show) {
    document.getElementById('loadingSpinner').classList.toggle('hidden', !show);
}

function showAlert(message, type = 'info') {
    const alert = document.getElementById('statusAlert');
    alert.textContent = message;
    alert.className = `alert alert-${type}`;
}

function clearAlert() {
    document.getElementById('statusAlert').classList.add('alert-hidden');
}

function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    errorAlert.textContent = message;
    errorAlert.classList.remove('hidden');
}

function clearError() {
    document.getElementById('errorAlert').classList.add('hidden');
}

// ============= Utility Functions =============
function convertImageToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeThresholdModal();
    }
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const modal = document.getElementById('thresholdModal');
    if (e.target === modal) {
        closeThresholdModal();
    }
});
