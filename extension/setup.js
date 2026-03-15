function moveStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => step.classList.remove('active'));
    const targetStep = document.getElementById('step' + stepNumber);
    if (targetStep) targetStep.classList.add('active');
}

// STEP 1 Logic
document.getElementById('btn-continue').onclick = () => {
    // DIRECT DOWNLOAD LINK (Fixed: Added /archive/refs/heads/main.zip for direct download)
    const downloadUrl = "https://github.com/sahithisirikonda01/SPRA/archive/refs/heads/main.zip";
    window.open(downloadUrl, '_blank');

    moveStep(2);
    startUIProgress();
};

// STEP 2 Logic: Simulated Progress
function startUIProgress() {
    let width = 0;
    const bar = document.getElementById('progress-bar');
    const status = document.getElementById('status-text');
    const verifyBtn = document.getElementById('btn-verify');

    const interval = setInterval(() => {
        if (width >= 85) {
            clearInterval(interval);
            status.innerText = "Please run INSTALLER.bat from the downloaded folder.";
            verifyBtn.style.display = "block"; // Show verify button only when ready
        } else {
            width += 5;
            if (bar) bar.style.width = width + "%";
        }
    }, 400);
}

// Verify if Native Host is actually installed in the Registry
document.getElementById('btn-verify').onclick = () => {
    chrome.runtime.sendNativeMessage('com.ssera.privacy', { text: "ping" }, (response) => {
        if (chrome.runtime.lastError) {
            alert("Connection Failed! Ensure you ran INSTALLER.bat and restarted Chrome.");
            console.log("Native Messaging Error:", chrome.runtime.lastError.message);
        } else {
            const bar = document.getElementById('progress-bar');
            if (bar) bar.style.width = "100%";
            document.getElementById('status-text').innerText = "System Linked Successfully!";
            setTimeout(() => moveStep(3), 1000);
        }
    });
};

// STEP 3 Logic: Save API Key
document.getElementById('btn-finish').onclick = () => {
    const key = document.getElementById('groq-key').value;
    if (key.startsWith('gsk_')) {
        chrome.storage.local.set({ groq_api_key: key }, () => {
            alert("SSERA Pro is now active! Refresh your Gmail tab.");
            window.close();
        });
    } else {
        alert("Please enter a valid Groq API Key (starts with gsk_).");
    }
};