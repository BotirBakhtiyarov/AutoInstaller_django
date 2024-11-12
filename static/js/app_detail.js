function openModal(imageSrc) {
    var modal = document.getElementById("imageModal");
    var modalImg = document.getElementById("zoomedImage");
    modal.style.display = "block";
    modalImg.src = imageSrc;
}

function closeModal() {
    var modal = document.getElementById("imageModal");
    modal.style.display = "none";
}


// DOWNLOAD
function installApp() {
    var appName = "{{ app.name }}";
    var installUrl = "myapp://install/" + encodeURIComponent(appName);
    window.location.href = installUrl;
}

function openDownloadMenu() {
    // Show the download menu
    document.getElementById('downloadMenu').style.display = 'block';
}

function closeDownloadMenu() {
    // Hide the download menu
    document.getElementById('downloadMenu').style.display = 'none';
}

function downloadZip() {
    // Trigger download of the ZIP file
    var zipUrl = "{{ host_url }}{{MEDIA_URL}}{{ app.zip_path }}";
    window.location.href = zipUrl;
}

function copyToClipboard() {
    var link = document.querySelector(".textlink");
    link.select();
    link.setSelectionRange(0, 99999);
    document.execCommand("copy");
}
