# SSERA Pro: Smart Secure Email Reply Assistant 🛡️✨

**SSERA** is a privacy-preserving AI assistant that masks sensitive information locally before generating professional email replies.

## 🛡️ The Main Moto
To ensure **100% data confidentiality**, SSERA uses a "Local-First" architecture. It identifies PII (Personally Identifiable Information) using **Microsoft Presidio** on your own computer, ensuring that sensitive data like Bank Details, Aadhar, and Passwords never reach the Cloud AI.

## 🚀 Key Features
- **Context-Aware Masking:** Detects Names, Organizations, IFSC, Aadhar, and Credentials using NLP.
- **Label Preservation:** Masks the values but keeps headers (e.g., `IFSC Code: [IFSC]`) for AI context.
- **Zero-Trust Cloud:** Sends only masked data to the Groq Llama 3 model.
- **Automatic Setup:** Includes a one-click installer for system integration.

## 🛠️ Installation Guide
1. **Load Extension:**
   - Open Chrome -> `chrome://extensions`.
   - Enable **Developer Mode**.
   - Click **Load Unpacked** and select the `extension` folder.
   - **Copy the Extension ID** (e.g., `lodifpl...`).

2. **System Setup:**
   - Download this repository as a ZIP.
   - Extract it to a permanent folder.
   - Open `native-host/com.ssera.privacy.json` and paste your **Extension ID** into `allowed_origins`.
   - Double-click `native-host/INSTALLER.bat` to install dependencies and register the host.

3. **Activation:**
   - Click the SSERA icon in your browser.
   - Click **Verify Connection**.
   - Paste your personal **Groq API Key** and Save.

## 🧪 Technologies Used
- **Python:** Microsoft Presidio, spaCy (`en_core_web_lg`).
- **JavaScript:** Chrome Extensions API, Native Messaging.
- **AI:** Groq (Llama 3-70B).