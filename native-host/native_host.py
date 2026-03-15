import sys
import json
import struct
import warnings
import re

warnings.filterwarnings("ignore")

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern

# Initialize analyzer
analyzer = AnalyzerEngine(default_score_threshold=0.6)

# =====================================================
# 1. UNIQUE IDENTIFIERS
# =====================================================

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="AADHAR",
        patterns=[Pattern("aadhar", r"\b\d{4}\s\d{4}\s\d{4}\b", 0.95)],
        context=["aadhar", "uid"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PAN",
        patterns=[Pattern("pan", r"\b[A-Z]{5}\d{4}[A-Z]\b", 0.95)],
        context=["pan", "tax"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PASSPORT",
        patterns=[Pattern("passport", r"\b[A-Z][0-9]{7}\b", 0.95)],
        context=["passport"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="EMPLOYEE_ID",
        patterns=[Pattern("emp", r"\bEMP\d{3,6}\b", 0.9)],
        context=["employee", "emp"]
    )
)

# =====================================================
# 2. FINANCIAL DATA
# =====================================================

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="BANK_ACCOUNT",
        patterns=[Pattern("account", r"\b\d{9,18}\b", 0.85)],
        context=["account", "bank"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="IFSC",
        patterns=[Pattern("ifsc", r"\b[A-Z]{4}0[A-Z0-9]{6}\b", 0.95)],
        context=["ifsc", "bank"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="CREDIT_CARD",
        patterns=[Pattern("card", r"\b(?:\d[ -]*?){13,16}\b", 0.95)],
        context=["credit", "card", "debit"]
    )
)

money_regex = r"(?:₹|Rs\.?)\s?\d{1,3}(?:,\d{2})*(?:,\d{3})|\b\d{1,3}(?:,\d{2})+(?:,\d{3})\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="MONEY",
        patterns=[Pattern("money", money_regex, 0.9)],
        context=["salary", "revenue", "amount", "profit"]
    )
)

# =====================================================
# 3. ACCESS CREDENTIALS
# =====================================================

password_regex = r"(?i)(?:password|pwd|passcode)\s*[:=]\s*([A-Za-z0-9@#$%^&*!]{8,25})"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PASSWORD",
        patterns=[Pattern("password", password_regex, 0.99)]
    )
)

email_regex = r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="LOGIN_ID",
        patterns=[Pattern("email", email_regex, 0.95)],
        context=["login", "email", "username"]
    )
)

api_regex = r"\b[A-Za-z0-9]{32,45}\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="API_KEY",
        patterns=[Pattern("api", api_regex, 0.9)],
        context=["api", "token", "secret"]
    )
)

# =====================================================
# 4. CORPORATE DATA
# =====================================================

org_regex = r"\b[A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+)*\s(?:Solutions|Technologies|Systems|Labs|Corp|Ltd|Pvt\.?\s*Ltd\.?)"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="ORGANIZATION",
        patterns=[Pattern("org", org_regex, 0.9)],
        context=["company", "organization"]
    )
)

project_regex = r"\b(Project|Deal)\s[A-Z][A-Za-z]+\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PROJECT",
        patterns=[Pattern("project", project_regex, 0.9)]
    )
)

# =====================================================
# 5. CONTACT / DIGITAL FOOTPRINT
# =====================================================

phone_regex = r"\b[6-9]\d{4}\s?\d{5}\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PHONE_NUMBER",
        patterns=[Pattern("phone", phone_regex, 0.95)],
        context=["phone", "contact", "mobile"]
    )
)

ip_regex = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="IP_ADDRESS",
        patterns=[Pattern("ip", ip_regex, 0.95)]
    )
)

mac_regex = r"\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="MAC_ADDRESS",
        patterns=[Pattern("mac", mac_regex, 0.95)]
    )
)

# =====================================================
# MASKING ENGINE
# =====================================================

def mask_text(text):

    results = analyzer.analyze(text=text, language="en")

    # remove overlapping detections
    results = sorted(results, key=lambda x: (x.start, x.end))

    filtered = []
    last_end = -1

    for r in results:
        if r.start >= last_end:
            filtered.append(r)
            last_end = r.end

    masked_text = text
    entity_map = {}

    for i, r in enumerate(sorted(filtered, key=lambda x: x.start, reverse=True)):

        value = text[r.start:r.end]

        label = r.entity_type

        placeholder = f"[{label}_{i}]"

        entity_map[placeholder] = value

        masked_text = (
            masked_text[:r.start] +
            placeholder +
            masked_text[r.end:]
        )

    return masked_text, entity_map


# =====================================================
# STDIN PIPE COMMUNICATION
# =====================================================

def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None

    length = struct.unpack("@I", raw_length)[0]

    data = sys.stdin.buffer.read(length)

    return json.loads(data.decode("utf-8"))


def send_message(message):

    encoded = json.dumps(message).encode("utf-8")

    sys.stdout.buffer.write(struct.pack("@I", len(encoded)))

    sys.stdout.buffer.write(encoded)

    sys.stdout.buffer.flush()


# =====================================================
# MAIN LOOP
# =====================================================

while True:

    msg = get_message()

    if msg is None:
        break

    text = msg.get("text", "")

    masked_text, entity_map = mask_text(text)

    send_message({
        "masked_text": masked_text,
        "entity_map": entity_map
    })