let selectedText = "";
let localVault = {};

// --- 1. Robust Message Sender ---
function callExtension(action, data, callback) {
    if (!chrome.runtime?.id) {
        alert("SSERA: Extension reloaded. Please refresh this page to continue.");
        return;
    }
    chrome.runtime.sendMessage({ action, ...data }, callback);
}

document.addEventListener("mouseup", (e) => {
    const t = window.getSelection().toString().trim();
    if (t.length > 5) {
        selectedText = t;
        renderShieldIcon(e.pageX, e.pageY);
    }
});

function renderShieldIcon(x, y) {
    let icon = document.getElementById("s-icon") || document.createElement("div");
    icon.id = "s-icon"; icon.innerHTML = "🛡️";
    icon.style.left = `${x+5}px`; icon.style.top = `${y+5}px`;
    document.body.appendChild(icon);
    icon.onclick = () => { icon.remove(); showShieldPanel(); };
}

function showShieldPanel() {
    if (document.getElementById("s-panel")) document.getElementById("s-panel").remove();
    const panel = document.createElement("div");
    panel.id = "s-panel";
    panel.innerHTML = `
        <div id="s-header">SSERA Privacy Shield <span id="s-close">×</span></div>
        <div id="s-body">
            <button id="s-mask-btn">1. Analyze (Local Presidio)</button>
            <div id="s-mask-box" style="display:none;">
                <div class="s-label">SHIELDED PREVIEW:</div>
                <div id="s-preview"></div>
                <button id="s-gen-btn">2. Generate Reply (Groq)</button>
            </div>
            <div id="s-res-box" style="display:none;">
                <div class="s-label">UNMASKED REPLY:</div>
                <div id="s-result"></div>
                <button id="s-copy">Copy to Email</button>
            </div>
        </div>
    `;
    document.body.appendChild(panel);
    document.getElementById("s-close").onclick = () => panel.remove();

    document.getElementById("s-mask-btn").onclick = () => {
        document.getElementById("s-mask-btn").innerText = "Analyzing Context...";
        callExtension("ANALYZE_PII", { text: selectedText }, (res) => {
            if (res?.success) {
                localVault = res.data.entity_map;
                document.getElementById("s-preview").innerText = res.data.masked_text;
                document.getElementById("s-mask-box").style.display = "block";
                document.getElementById("s-mask-btn").innerText = "Scan Complete ✓";
            } else {
                alert("Privacy Engine not found. Click the SSERA icon in your browser to setup.");
            }
        });
    };

    document.getElementById("s-gen-btn").onclick = () => {
        document.getElementById("s-gen-btn").innerText = "AI Thinking...";
        callExtension("GENERATE_REPLY", { text: document.getElementById("s-preview").innerText }, (res) => {
            if (res?.success) {
                let final = res.data;
                for (let p in localVault) { final = final.replaceAll(p, localVault[p]); }
                document.getElementById("s-result").innerText = final;
                document.getElementById("s-res-box").style.display = "block";
                document.getElementById("s-gen-btn").innerText = "Generated!";
            } else {
                alert("Error: " + (res?.error || "Check your API Key settings."));
            }
        });
    };

    document.getElementById("s-copy").onclick = () => {
        navigator.clipboard.writeText(document.getElementById("s-result").innerText);
        alert("Copied!");
    };
}