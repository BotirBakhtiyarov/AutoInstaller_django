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

function downloadZip() {
    // Trigger download of the ZIP file
    var zipUrl = document.getElementById('zip-url').value;
    zipUrl = zipUrl.replace('http://', 'https://');
    window.location.href = zipUrl;
    console.log('ZIP URL: ',zipUrl)
}

function installApp() {
    var appName = document.getElementById('app-name').value;
    var installUrl = "myapp://install/" + appName;
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

function copyToClipboard() {
    var link = document.querySelector(".textlink");
    link.select();
    link.setSelectionRange(0, 99999);
    document.execCommand("copy");
}