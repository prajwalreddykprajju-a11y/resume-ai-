// ResumeReady.AI JavaScript Controller

document.addEventListener('DOMContentLoaded', function () {
  
  // 1. File Upload Drag & Drop + File Validation
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const fileInfoCard = document.getElementById('fileInfoCard');
  const fileNameDisplay = document.getElementById('fileNameDisplay');
  const fileSizeDisplay = document.getElementById('fileSizeDisplay');
  const removeFileBtn = document.getElementById('removeFileBtn');
  const analyzeSubmitBtn = document.getElementById('analyzeSubmitBtn');

  if (dropzone && fileInput) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
    });

    dropzone.addEventListener('drop', handleDrop, false);
    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    function handleDrop(e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        fileInput.files = files;
        validateAndDisplayFile(files[0]);
      }
    }

    function handleFileSelect() {
      if (fileInput.files.length > 0) {
        validateAndDisplayFile(fileInput.files[0]);
      }
    }

    function validateAndDisplayFile(file) {
      const allowedExts = ['pdf', 'docx'];
      const ext = file.name.split('.').pop().toLowerCase();
      const maxSizeMB = 10;
      const maxSizeBytes = maxSizeMB * 1024 * 1024;

      if (!allowedExts.includes(ext)) {
        alert('Unsupported file format! Please upload a PDF or DOCX file.');
        fileInput.value = '';
        if (fileInfoCard) fileInfoCard.classList.add('d-none');
        if (analyzeSubmitBtn) analyzeSubmitBtn.disabled = true;
        return;
      }

      if (file.size > maxSizeBytes) {
        alert(`File size exceeds ${maxSizeMB} MB limit! Please choose a smaller file.`);
        fileInput.value = '';
        if (fileInfoCard) fileInfoCard.classList.add('d-none');
        if (analyzeSubmitBtn) analyzeSubmitBtn.disabled = true;
        return;
      }

      // Display file details
      if (fileNameDisplay) fileNameDisplay.textContent = file.name;
      if (fileSizeDisplay) fileSizeDisplay.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
      if (fileInfoCard) fileInfoCard.classList.remove('d-none');
      if (analyzeSubmitBtn) analyzeSubmitBtn.disabled = false;
    }

    if (removeFileBtn) {
      removeFileBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        fileInput.value = '';
        if (fileInfoCard) fileInfoCard.classList.add('d-none');
        if (analyzeSubmitBtn) analyzeSubmitBtn.disabled = true;
      });
    }
  }

  // 2. Upload Form Loading Spinner
  const uploadForm = document.getElementById('uploadForm');
  const loadingOverlay = document.getElementById('loadingOverlay');

  if (uploadForm) {
    uploadForm.addEventListener('submit', function () {
      if (loadingOverlay) loadingOverlay.classList.remove('d-none');
    });
  }

  // 3. Dynamic Target Role Selector AJAX Handler
  const targetRoleSelect = document.getElementById('targetRoleSelect');
  if (targetRoleSelect) {
    targetRoleSelect.addEventListener('change', function () {
      const resumeId = this.getAttribute('data-resume-id');
      const selectedRole = this.value;

      fetch('/api/target_role_analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_id: resumeId, target_role: selectedRole })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // Refresh page or update UI dynamically
          window.location.reload();
        }
      })
      .catch(err => console.error('Role update failed:', err));
    });
  }

});
