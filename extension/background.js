chrome.runtime.onInstalled.addListener(() => {
    chrome.tabs.create({ url: 'setup.html' });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "ANALYZE_PII") {
        chrome.runtime.sendNativeMessage('com.ssera.privacy', { text: request.text }, (res) => {
            if (chrome.runtime.lastError) {
                sendResponse({ success: false, error: chrome.runtime.lastError.message });
            } else {
                sendResponse({ success: true, data: res });
            }
        });
        return true; 
    }

    if (request.action === "GENERATE_REPLY") {
        chrome.storage.local.get(['groq_api_key'], (result) => {
            if (!result.groq_api_key) {
                sendResponse({ success: false, error: "Setup API Key in the extension window." });
                return;
            }
            fetch("https://api.groq.com/openai/v1/chat/completions", {
                method: "POST",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${result.groq_api_key}` },
                body: JSON.stringify({
                    model: "llama-3.3-70b-versatile",
                    messages: [
                        { role: "system", content: "Professional assistant. Use placeholders like [NAME] exactly as provided. Write a reply to the sender." },
                        { role: "user", content: `Reply to: ${request.text}` }
                    ]
                })
            })
            .then(r => r.json())
            .then(d => sendResponse({ success: true, data: d.choices[0].message.content }))
            .catch(e => sendResponse({ success: false, error: e.message }));
        });
        return true;
    }
});