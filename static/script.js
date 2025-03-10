document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const uploadButton = document.getElementById('upload-button');
    const input = document.getElementById('custom-input');
    const dropdown = document.getElementById('dropdown-list');

    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            fileName.innerText = '已選擇: ' + file.name;
            uploadButton.classList.add('success');
            fileName.style.display = 'block';
            uploadButton.classList.add('active');
            uploadButton.disabled = false;
            displayPDFPreview(file);
        }
    });

    document.getElementById('upload-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        const fileName = document.getElementById('file-input').files[0].name;
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);
        xhr.responseType = 'blob';
        xhr.onload = function() {
            if (xhr.status === 200) {
                const url = window.URL.createObjectURL(new Blob([xhr.response]));
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = fileName.replace('.pdf', '') + '_RightMargin.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                displayPDFPreview(xhr.response);
            } else {
                alert('上傳失敗');
            }
        };
        xhr.send(formData);
    });

    // Hide file name initially
    fileName.style.display = 'none';
    uploadButton.disabled = true;

    // Prevent double-tap zoom on iOS
    document.addEventListener('touchend', function(event) {
        event.preventDefault();
        event.target.click();
    }, false);

    // Handle iOS file input
    if (navigator.userAgent.match(/iPad|iPhone|iPod/i)) {
        const fileInput = document.getElementById('file-input');
        fileInput.setAttribute('capture', 'camera');
        fileInput.setAttribute('accept', 'application/pdf');
    }

    // Prevent bounce effect on iOS
    document.body.addEventListener('touchmove', function(event) {
        if (event.target.closest('.pdf-preview')) return;
        event.preventDefault();
    }, { passive: false });

    // Fix iOS scroll restoration
    window.onpageshow = function(event) {
        if (event.persisted) {
            window.location.reload();
        }
    };

    // Handle custom dropdown
    input.addEventListener("focus", () => {
        dropdown.style.display = "block";
    });

    input.addEventListener("blur", () => {
        setTimeout(() => dropdown.style.display = "none", 200);
    });

    dropdown.querySelectorAll("div").forEach(option => {
        option.addEventListener("click", () => {
            input.value = option.textContent;
            dropdown.style.display = "none";
        });
    });
});

function displayPDFPreview(file) {
    const fileReader = new FileReader();
    fileReader.onload = function() {
        const typedarray = new Uint8Array(this.result);
        pdfjsLib.getDocument(typedarray).promise.then(function(pdf) {
            pdf.getPage(1).then(function(page) {
                const scale = window.innerWidth <= 768 ? 1.0 : 1.5; // Adjust scale for mobile
                const viewport = page.getViewport({ scale: scale });
                const canvas = document.getElementById('pdf-preview');
                const context = canvas.getContext('2d');
                canvas.height = viewport.height;
                canvas.width = viewport.width;
                canvas.style.display = 'block';

                const renderContext = {
                    canvasContext: context,
                    viewport: viewport
                };
                page.render(renderContext);
            });
        });
    };
    fileReader.readAsArrayBuffer(file);
}