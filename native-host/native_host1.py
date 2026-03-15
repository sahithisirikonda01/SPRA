# import sys
# import json
# import struct
# import os
# import warnings
# import re

# warnings.filterwarnings("ignore")

# try:
#     from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
#     analyzer = AnalyzerEngine()

#     # --- REFINED PASSWORD RECOGNIZER ---
#     # Only matches strings with at least one digit and one special character (Complexity check)
#     pass_regex = r"(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{6,30}"
#     pass_pattern = Pattern(name="strong_pass", regex=pass_regex, score=0.95)
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="CREDENTIAL", 
#         patterns=[pass_pattern], 
#         context=["password", "pwd", "secret", "temp"]
#     ))

#     # --- INDIAN PII RECOGNIZERS ---
#     analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="AADHAR", patterns=[Pattern(name="aadhar", regex=r"\b\d{4}\s?\d{4}\s?\d{4}\b", score=0.9)], context=["aadhar"]))
#     analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="PAN", patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", score=0.95)], context=["pan"]))
#     analyzer.registry.add_recognizer(PatternRecognizer(supported_entity="IFSC", patterns=[Pattern(name="ifsc", regex=r"\b[A-Z]{4}0[A-Z0-9]{6}\b", score=0.95)], context=["ifsc"]))

# except Exception:
#     sys.exit(1)

# # Words that are ABSOLUTELY FORBIDDEN to be masked
# LABEL_BLACKLIST = [
#     "Dear", "Regards", "Sincerely", "Please", "Kindly", "Name", "Number", "Bank", 
#     "Employee", "ID", "IFSC", "Account", "HR", "Team", "Support", "Confirm", "Update"
# ]

# def get_message():
#     try:
#         raw_length = sys.stdin.buffer.read(4)
#         if len(raw_length) == 0: return None
#         length = struct.unpack('@I', raw_length)[0]
#         message = sys.stdin.buffer.read(length).decode('utf-8')
#         return json.loads(message)
#     except: return None

# def send_message(message):
#     content = json.dumps(message).encode('utf-8')
#     sys.stdout.buffer.write(struct.pack('@I', len(content)))
#     sys.stdout.buffer.write(content)
#     sys.stdout.buffer.flush()

# while True:
#     msg = get_message()
#     if msg:
#         try:
#             text = msg.get("text", "")
#             results = analyzer.analyze(text=text, language='en', score_threshold=0.4)
            
#             entity_map = {}
#             masked_text = text
#             results = sorted(results, key=lambda x: x.start, reverse=True)
            
#             cleaned_results = []
#             if results:
#                 last_start = float('inf')
#                 for res in results:
#                     val = text[res.start:res.end].strip()
#                     clean_val = val.lower().strip(":").strip()
                    
#                     # 1. Skip Blacklisted Labels
#                     if any(label.lower() == clean_val for label in LABEL_BLACKLIST):
#                         continue

#                     if res.end <= last_start:
#                         actual_start = res.start
#                         # 2. Colon Logic: Don't mask the heading "Name:"
#                         if ":" in val:
#                             actual_start += (val.find(":") + 1)
                        
#                         final_secret = text[actual_start:res.end].strip()
#                         if final_secret:
#                             # Avoid masking spaces
#                             actual_start = text.find(final_secret, actual_start)
#                             res.start = actual_start
#                             res.end = actual_start + len(final_secret)
#                             cleaned_results.append(res)
#                             last_start = res.start

#             for res in cleaned_results:
#                 placeholder = f"[{res.entity_type}_{res.start}]"
#                 entity_map[placeholder] = text[res.start:res.end]
#                 masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]
            
#             send_message({"masked_text": masked_text, "entity_map": entity_map})
#         except Exception: pass
#     else: break



# import sys
# import json
# import struct
# import os
# import warnings
# import re

# warnings.filterwarnings("ignore")

# try:
#     from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
#     analyzer = AnalyzerEngine()

#     # --- 1. SMART PASSWORD RECOGNIZER ---
#     # Matches strings with letters, numbers, AND symbols. 
#     # Context-heavy to avoid masking words like "discussed".
#     pass_regex = r"(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{6,30}"
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="PASSWORD", 
#         patterns=[Pattern(name="strong_pass", regex=pass_regex, score=0.95)], 
#         context=["password", "pwd", "temp", "secret"]
#     ))

#     # --- 2. USERNAME RECOGNIZER ---
#     # Catches sahithi_test01
#     user_regex = r"\b[A-Za-z0-9_]{5,25}\b"
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="USERNAME",
#         patterns=[Pattern(name="user_pattern", regex=user_regex, score=0.85)],
#         context=["username", "login", "user"]
#     ))

#     # --- 3. INDIAN AADHAR (12 Digits with spaces) ---
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="AADHAR", 
#         patterns=[Pattern(name="aadhar", regex=r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b", score=0.95)], 
#         context=["aadhar", "uid", "unique id"]
#     ))

#     # --- 4. INDIAN PAN ---
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="PAN", 
#         patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", score=0.95)], 
#         context=["pan", "income tax", "pancard"]
#     ))

#     # --- 5. BANK ACCOUNT (9-18 digits) ---
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="BANK_ACCOUNT", 
#         patterns=[Pattern(name="acc", regex=r"\b\d{9,18}\b", score=0.8)], 
#         context=["account", "savings", "acc no", "bank account"]
#     ))

#     # --- 6. EMPLOYEE ID ---
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="EMP_ID", 
#         patterns=[Pattern(name="emp", regex=r"\b[A-Z]{2,4}\d{4,8}\b", score=0.9)], 
#         context=["employee", "emp", "id"]
#     ))

#     # --- 7. BANK NAME RECOGNIZER ---
#     bank_regex = r"\b(State Bank of India|HDFC|ICICI|Axis|Punjab National Bank|Bank of Baroda)\b"
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="BANK_NAME",
#         patterns=[Pattern(name="bank_name", regex=bank_regex, score=0.9)],
#         context=["bank", "branch"]
#     ))

# except Exception:
#     sys.exit(1)

# # These words will NEVER be masked, preventing "Subject:" or "Hi" from disappearing
# LABEL_BLACKLIST = [
#     "Subject", "Documents", "Verification", "Dear", "Sir", "As", "Requested", "Sharing",
#     "Personal", "Details", "Name", "Date", "Birth", "Aadhar", "Number", "PAN", "Address",
#     "Road", "Flat", "Please", "Know", "Additional", "Sincerely", "Hi", "Hello", "Thanks",
#     "Regards", "Login", "Credentials", "Project", "Portal", "Username", "Password",
#     "Temporary", "Registered", "Email", "Discussed", "Support", "Team", "Bank", "Employee",
#     "ID", "IFSC", "Account", "HR", "Salary", "Transfer", "Processing", "Kindly", "Confirm",
#     "Updated", "Payroll", "System"
# ]

# def get_message():
#     try:
#         raw_length = sys.stdin.buffer.read(4)
#         if len(raw_length) == 0: return None
#         length = struct.unpack('@I', raw_length)[0]
#         return json.loads(sys.stdin.buffer.read(length).decode('utf-8'))
#     except: return None

# def send_message(message):
#     content = json.dumps(message).encode('utf-8')
#     sys.stdout.buffer.write(struct.pack('@I', len(content)))
#     sys.stdout.buffer.write(content)
#     sys.stdout.buffer.flush()

# while True:
#     msg = get_message()
#     if msg:
#         try:
#             text = msg.get("text", "")
#             # Higher threshold to avoid guessing
#             results = analyzer.analyze(text=text, language='en', score_threshold=0.45)
            
#             entity_map = {}
#             masked_text = text
#             results = sorted(results, key=lambda x: x.start, reverse=True)
            
#             cleaned_results = []
#             if results:
#                 last_start = float('inf')
#                 for res in results:
#                     val = text[res.start:res.end].strip()
#                     clean_val = val.lower().strip(":").strip()
                    
#                     # 1. Skip Blacklisted Labels
#                     if any(label.lower() == clean_val for label in LABEL_BLACKLIST):
#                         continue

#                     if res.end <= last_start:
#                         actual_start = res.start
#                         # 2. Advanced Colon Logic: Only mask the portion AFTER the colon
#                         if ":" in val:
#                             colon_pos = val.find(":")
#                             actual_start += (colon_pos + 1)
                        
#                         final_secret = text[actual_start:res.end].strip()
                        
#                         # 3. Validation: Only mask if it's not a common word and length > 2
#                         if final_secret and len(final_secret) > 2:
#                             # Final check against blacklist for the trimmed secret
#                             if final_secret.lower() in [l.lower() for l in LABEL_BLACKLIST]:
#                                 continue
                                
#                             res.start = text.find(final_secret, actual_start)
#                             res.end = res.start + len(final_secret)
#                             cleaned_results.append(res)
#                             last_start = res.start

#             for res in cleaned_results:
#                 # Use simple labels for AI context
#                 label = res.entity_type
#                 placeholder = f"[{label}_{res.start}]"
#                 entity_map[placeholder] = text[res.start:res.end]
#                 masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]
            
#             send_message({"masked_text": masked_text, "entity_map": entity_map})
#         except Exception: pass
#     else: break





## main




# import sys
# import json
# import struct
# import os
# import warnings
# import re

# # Silence warnings for a clean communication pipe
# warnings.filterwarnings("ignore")

# try:
#     from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
#     # Initialize the engine using the Large Spacy Model for best context awareness
#     analyzer = AnalyzerEngine(default_score_threshold=0.35)

#     # --- 1. INDIAN FINANCIAL RECOGNIZERS (Regex + Context) ---
#     # Aadhar Card
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="AADHAR", 
#         patterns=[Pattern(name="aadhar", regex=r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b", score=0.95)], 
#         context=["aadhar", "uid", "identity"]
#     ))

#     # PAN Card
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="PAN", 
#         patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", score=0.95)], 
#         context=["pan", "tax", "income"]
#     ))

#     # IFSC Code
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="IFSC", 
#         patterns=[Pattern(name="ifsc", regex=r"\b[A-Z]{4}0[A-Z0-9]{6}\b", score=0.95)], 
#         context=["ifsc", "bank code", "transfer"]
#     ))

#     # Bank Account Number (Context-dependent to avoid masking years)
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="BANK_ACCOUNT", 
#         patterns=[Pattern(name="acc", regex=r"\b\d{9,18}\b", score=0.8)], 
#         context=["account", "savings", "acc no", "bank account", "number"]
#     ))

#     # --- 2. SMART PASSWORD RECOGNIZER ---
#     # Only masks strings that have letters AND numbers/symbols
#     pass_regex = r"(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{7,25}"
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="PASSWORD", 
#         patterns=[Pattern(name="strong_pass", regex=pass_regex, score=0.9)], 
#         context=["password", "pwd", "credentials", "secret"]
#     ))

# except Exception as e:
#     sys.exit(1)

# # List of words that provide context but must NOT be masked
# LABEL_BLACKLIST = {
#     "subject", "dear", "sir", "name", "aadhar", "pan", "number", "ifsc", "account", 
#     "bank", "hr", "team", "regards", "sincerely", "thanks", "hi", "registered", 
#     "phone", "mobile", "date", "birth", "address", "login", "username", "password"
# }

# def get_message():
#     try:
#         raw_length = sys.stdin.buffer.read(4)
#         if len(raw_length) == 0: return None
#         length = struct.unpack('@I', raw_length)[0]
#         return json.loads(sys.stdin.buffer.read(length).decode('utf-8'))
#     except: return None

# def send_message(message):
#     content = json.dumps(message).encode('utf-8')
#     sys.stdout.buffer.write(struct.pack('@I', len(content)))
#     sys.stdout.buffer.write(content)
#     sys.stdout.buffer.flush()

# while True:
#     msg = get_message()
#     if msg:
#         try:
#             text = msg.get("text", "")
#             # We run analysis. Presidio uses spaCy to find PERSON and ORG
#             results = analyzer.analyze(text=text, language='en')
            
#             entity_map = {}
#             masked_text = text
#             results = sorted(results, key=lambda x: x.start, reverse=True)
            
#             cleaned_results = []
#             last_start = float('inf')

#             for res in results:
#                 # 1. Handle Overlaps (Crucial for examiners)
#                 if res.end > last_start:
#                     continue

#                 val = text[res.start:res.end].strip()
#                 clean_val = val.lower().strip(":").strip()
                
#                 # 2. Blacklist Protection
#                 if clean_val in LABEL_BLACKLIST:
#                     continue

#                 # 3. Structural Protection (Label vs Value)
#                 # If "Name: Rahul", move start to after the colon
#                 actual_start = res.start
#                 if ":" in val:
#                     actual_start += (val.find(":") + 1)
                
#                 final_secret = text[actual_start:res.end].strip()

#                 # 4. Final Quality Check
#                 if final_secret and len(final_secret) > 2:
#                     if final_secret.lower() in LABEL_BLACKLIST:
#                         continue
                        
#                     res.start = text.find(final_secret, actual_start)
#                     res.end = res.start + len(final_secret)
#                     cleaned_results.append(res)
#                     last_start = res.start

#             # 5. The Masking Process
#             for res in cleaned_results:
#                 label = res.entity_type
#                 # Clean up labels for display
#                 if label == "PERSON": label = "NAME"
                
#                 placeholder = f"[{label}_{res.start}]"
#                 entity_map[placeholder] = text[res.start:res.end]
#                 masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]
            
#             send_message({"masked_text": masked_text, "entity_map": entity_map})
#         except Exception: pass
#     else: break



#2nd main
# import sys
# import json
# import struct
# import os
# import warnings
# import re

# # Silence warnings to keep the communication pipe clean for Chrome
# warnings.filterwarnings("ignore")

# try:
#     from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
#     # Initialize Engine (Uses en_core_web_lg for context)
#     analyzer = AnalyzerEngine()

#     # --- 1. SMART ORGANIZATION RECOGNIZER (Improved Suffix Logic) ---
#     # This regex is case-insensitive (?i) and handles dots/spaces/variations
#     # It catches "TechNova Pvt Ltd", "technova pvt. ltd.", "G.N.I.T.S Pvt.Ltd."
#     org_suffix_regex = r"(?i)\b[A-Z0-9&.\-']+(?:\s+[A-Z0-9&.\-']+)*\s+(?:Pvt\.?\s*Ltd\.?|pvt\.?\s*ltd\.?|Ltd\.?|Limited|Corp\.?|Corporation|Inc\.?|Incorporated)\b"
    
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="ORG",
#         patterns=[Pattern(name="org_suffix_flexible", regex=org_suffix_regex, score=0.95)],
#         context=["company", "organization", "office", "employer", "firm", "work"]
#     ))

#     # --- 2. PRECISE INDIAN RECOGNIZERS ---
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="AADHAR", 
#         patterns=[Pattern(name="aadhar", regex=r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b", score=0.95)], 
#         context=["aadhar", "uid", "identity"]
#     ))

#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="PAN_CARD", 
#         patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", score=0.95)], 
#         context=["pan", "tax", "pancard"]
#     ))

#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="IFSC_CODE", 
#         patterns=[Pattern(name="ifsc", regex=r"\b[A-Z]{4}0[A-Z0-9]{6}\b", score=0.95)], 
#         context=["ifsc", "bank code", "transfer"]
#     ))

#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="ACCOUNT_NUMBER", 
#         patterns=[Pattern(name="acc", regex=r"\b\d{9,18}\b", score=0.8)], 
#         context=["account", "savings", "acc no", "bank"]
#     ))

#     # --- 3. SMART PASSWORD RECOGNIZER ---
#     pass_regex = r"(?=.*\d)(?=.*[@#$!%*?&])[A-Za-z\d@#$!%*?&]{6,30}"
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="PASSWORD", 
#         patterns=[Pattern(name="complex_pass", regex=pass_regex, score=0.95)], 
#         context=["password", "pwd", "temp", "secret", "credentials"]
#     ))

# except Exception as e:
#     # Silent exit if libraries are missing
#     sys.exit(1)

# # Common words that provide context and should NOT be hidden
# SAFE_CONTEXT_WORDS = {
#     "dear", "regards", "sincerely", "thanks", "hello", "hi", "subject", 
#     "please", "kindly", "organization", "company", "limited", "private", "pvt", "ltd"
# }

# # Mapping for cleaner labels in the UI
# LABEL_MAP = {
#     "PERSON": "NAME",
#     "PHONE_NUMBER": "PHONE",
#     "EMAIL_ADDRESS": "EMAIL",
#     "LOCATION": "ADDRESS",
#     "ORG": "ORGANIZATION",
#     "AADHAR": "AADHAR_NO",
#     "PAN_CARD": "PAN_NO"
# }

# def get_message():
#     try:
#         raw_length = sys.stdin.buffer.read(4)
#         if len(raw_length) == 0: return None
#         length = struct.unpack('@I', raw_length)[0]
#         return json.loads(sys.stdin.buffer.read(length).decode('utf-8'))
#     except: return None

# def send_message(message):
#     content = json.dumps(message).encode('utf-8')
#     sys.stdout.buffer.write(struct.pack('@I', len(content)))
#     sys.stdout.buffer.write(content)
#     sys.stdout.buffer.flush()

# while True:
#     msg = get_message()
#     if msg:
#         try:
#             text = msg.get("text", "")
#             # threshold=0.4 is best for balancing PII detection vs common speech
#             results = analyzer.analyze(text=text, language='en', score_threshold=0.4)
            
#             entity_map = {}
#             masked_text = text
#             # Sort reverse to avoid index shifting during string manipulation
#             results = sorted(results, key=lambda x: x.start, reverse=True)
            
#             cleaned_results = []
#             last_start = float('inf')

#             for res in results:
#                 # 1. Prevent Overlaps (Conflict handling)
#                 if res.end > last_start: continue

#                 val = text[res.start:res.end].strip()
#                 clean_val = val.lower().strip(":").strip()

#                 # 2. Safety Check: Don't mask structural words
#                 if clean_val in SAFE_CONTEXT_WORDS: continue

#                 # 3. Structural Colon Protection (Label Awareness)
#                 # Example: "Name: Rahul" -> Mask only "Rahul"
#                 actual_start = res.start
#                 if ":" in val:
#                     colon_pos = val.find(":")
#                     actual_start += (colon_pos + 1)
                
#                 final_secret = text[actual_start:res.end].strip()

#                 # 4. Final Validation: Don't mask very short strings or blacklisted words
#                 if final_secret and len(final_secret) > 2:
#                     if final_secret.lower() in SAFE_CONTEXT_WORDS: continue
                    
#                     res.start = text.find(final_secret, actual_start)
#                     res.end = res.start + len(final_secret)
#                     cleaned_results.append(res)
#                     last_start = res.start

#             # Apply mapping and build masked text
#             for res in cleaned_results:
#                 raw_type = res.entity_type
#                 pretty_label = LABEL_MAP.get(raw_type, raw_type)
                
#                 # Generate unique ID to handle cases where multiple names exist
#                 placeholder = f"[{pretty_label}]"
                
#                 entity_map[placeholder] = text[res.start:res.end]
#                 masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]
            
#             send_message({"masked_text": masked_text, "entity_map": entity_map})
#         except Exception: pass
#     else: break



# import sys
# import json
# import struct
# import os
# import warnings
# import re

# # Silence warnings to keep the communication pipe clean
# warnings.filterwarnings("ignore")

# try:
#     from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
#     # Initialize Engine (Uses en_core_web_lg for context)
#     analyzer = AnalyzerEngine()

#     # --- 1. IMPROVED FINANCIAL RECOGNIZER (Indian & Global Format) ---
#     # This regex is now "Greedy" - it captures everything from the symbol 
#     # until the end of the number string, handling 4,85,00,000 correctly.
#     financial_regex = r"(?i)(?:[\$₹£€]\s?[\d,]+(?:\.\d+)?|\b[\d,]+(?:\.\d+)?\s?(?:INR|USD|EUR|GBP|Rupees|Dollars|rs\.?)\b)"
    
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="MONEY",
#         patterns=[Pattern(name="greedy_financial", regex=financial_regex, score=0.95)],
#         context=["revenue", "cost", "profit", "amount", "salary", "balance", "total", "expenditure"]
#     ))

#     # --- 2. SMART ORGANIZATION RECOGNIZER ---
#     org_suffix_regex = r"(?i)\b[A-Z0-9&.\-']+(?:\s+[A-Z0-9&.\-']+)*\s+(?:Pvt\.?\s*Ltd\.?|pvt\.?\s*ltd\.?|Ltd\.?|Limited|Corp\.?|Corporation|Inc\.?|Incorporated)\b"
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="ORG",
#         patterns=[Pattern(name="org_suffix", regex=org_suffix_regex, score=0.95)],
#         context=["company", "employer", "firm"]
#     ))

#     # --- 3. ESSENTIAL INDIAN ID RECOGNIZERS ---
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="AADHAR", 
#         patterns=[Pattern(name="aa", regex=r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b", score=0.95)], 
#         context=["aadhar", "uid"]
#     ))
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="PAN", 
#         patterns=[Pattern(name="pan", regex=r"\b[A-Z]{5}\d{4}[A-Z]{1}\b", score=0.95)], 
#         context=["pan", "pancard"]
#     ))
#     analyzer.registry.add_recognizer(PatternRecognizer(
#         supported_entity="IFSC", 
#         patterns=[Pattern(name="ifsc", regex=r"\b[A-Z]{4}0[A-Z0-9]{6}\b", score=0.95)], 
#         context=["ifsc", "bank"]
#     ))

# except Exception:
#     sys.exit(1)

# # Context labels that should remain visible so the AI understands the email structure
# SAFE_CONTEXT_WORDS = {
#     "dear", "regards", "sincerely", "thanks", "hello", "hi", "subject", "please", 
#     "kindly", "revenue", "profit", "costs", "expense", "estimate", "projected",
#     "operating", "summary", "internal", "confidential", "q1", "q2", "q3", "q4"
# }

# LABEL_MAP = {
#     "PERSON": "NAME",
#     "PHONE_NUMBER": "PHONE",
#     "ORG": "ORGANIZATION",
#     "MONEY": "FINANCIAL_VALUE",
#     "LOCATION": "ADDRESS"
# }

# def get_message():
#     try:
#         raw_length = sys.stdin.buffer.read(4)
#         if len(raw_length) == 0: return None
#         length = struct.unpack('@I', raw_length)[0]
#         return json.loads(sys.stdin.buffer.read(length).decode('utf-8'))
#     except: return None

# def send_message(message):
#     content = json.dumps(message).encode('utf-8')
#     sys.stdout.buffer.write(struct.pack('@I', len(content)))
#     sys.stdout.buffer.write(content)
#     sys.stdout.buffer.flush()

# while True:
#     msg = get_message()
#     if msg:
#         try:
#             text = msg.get("text", "")
#             results = analyzer.analyze(text=text, language='en', score_threshold=0.4)
            
#             entity_map = {}
#             masked_text = text
#             results = sorted(results, key=lambda x: x.start, reverse=True)
            
#             cleaned_results = []
#             last_start = float('inf')

#             for res in results:
#                 if res.end > last_start: continue

#                 val = text[res.start:res.end].strip()
#                 clean_val = val.lower().strip(":").strip()

#                 if clean_val in SAFE_CONTEXT_WORDS: continue

#                 # Colon Protection Logic
#                 actual_start = res.start
#                 if ":" in val:
#                     colon_pos = val.find(":")
#                     actual_start += (colon_pos + 1)
                
#                 final_secret = text[actual_start:res.end].strip()

#                 if final_secret and len(final_secret) >= 1:
#                     if final_secret.lower() in SAFE_CONTEXT_WORDS: continue
                    
#                     res.start = text.find(final_secret, actual_start)
#                     res.end = res.start + len(final_secret)
#                     cleaned_results.append(res)
#                     last_start = res.start

#             for res in cleaned_results:
#                 pretty_label = LABEL_MAP.get(res.entity_type, res.entity_type)
#                 placeholder = f"[{pretty_label}]"
#                 entity_map[placeholder] = text[res.start:res.end]
#                 masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]
            
#             send_message({"masked_text": masked_text, "entity_map": entity_map})
#         except Exception: pass
#     else: break

import sys
import json
import struct
import warnings
import re

warnings.filterwarnings("ignore")

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern

analyzer = AnalyzerEngine(default_score_threshold=0.6)

# ---------------------------------------------------
# 1. UNIQUE IDENTIFIERS (HIGH RISK PII)
# ---------------------------------------------------

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="AADHAR",
        patterns=[Pattern("aadhar", r"\b\d{4}\s\d{4}\s\d{4}\b", 0.95)],
        context=["aadhar","uid","identity"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PAN",
        patterns=[Pattern("pan", r"\b[A-Z]{5}\d{4}[A-Z]\b", 0.95)],
        context=["pan","tax"]
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
        patterns=[Pattern("empid", r"\bEMP\d{3,6}\b", 0.9)],
        context=["employee","emp","staff"]
    )
)

# ---------------------------------------------------
# 2. FINANCIAL & BANKING DATA
# ---------------------------------------------------

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="BANK_ACCOUNT",
        patterns=[Pattern("bank", r"\b\d{9,18}\b", 0.85)],
        context=["account","bank","balance"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="IFSC",
        patterns=[Pattern("ifsc", r"\b[A-Z]{4}0[A-Z0-9]{6}\b", 0.95)],
        context=["ifsc","bank"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="CREDIT_CARD",
        patterns=[Pattern("card", r"\b(?:\d[ -]*?){13,16}\b", 0.95)],
        context=["card","credit","debit"]
    )
)

# strict money detection
money_regex = r"(₹\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?)"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="MONEY",
        patterns=[Pattern("money", money_regex, 0.9)],
        context=["revenue","salary","profit","amount","balance"]
    )
)

# ---------------------------------------------------
# 3. ACCESS CREDENTIALS
# ---------------------------------------------------

# strict password detection (must contain symbol + number)
password_regex = r"(?=.*[0-9])(?=.*[@#$%^&+=!]).{8,25}"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PASSWORD",
        patterns=[Pattern("password", password_regex, 0.9)],
        context=["password","pwd","secret"]
    )
)

# login username/email
analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="LOGIN_ID",
        patterns=[Pattern("login", r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b", 0.95)],
        context=["login","username","email"]
    )
)

# API key detection
analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="API_KEY",
        patterns=[Pattern("apikey", r"\b[A-Za-z0-9]{32,45}\b", 0.9)],
        context=["api","token","secret"]
    )
)

# ---------------------------------------------------
# 4. CORPORATE DATA
# ---------------------------------------------------

org_regex = r"\b[A-Z][A-Za-z]+\s(?:Solutions|Technologies|Systems|Labs|Corp|Ltd|Pvt\.?\s*Ltd\.?)"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="ORGANIZATION",
        patterns=[Pattern("org", org_regex, 0.9)],
        context=["company","organization"]
    )
)

project_regex = r"\b(Project|Deal)\s[A-Z][A-Za-z]+\b"

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PROJECT",
        patterns=[Pattern("project", project_regex, 0.9)],
        context=["project","deal"]
    )
)

# ---------------------------------------------------
# 5. CONTACT / DIGITAL FOOTPRINT
# ---------------------------------------------------

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="PHONE_NUMBER",
        patterns=[Pattern("phone", r"\b[6-9]\d{4}\s?\d{5}\b", 0.95)],
        context=["phone","contact"]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="IP_ADDRESS",
        patterns=[Pattern("ip", r"\b(?:\d{1,3}\.){3}\d{1,3}\b", 0.95)]
    )
)

analyzer.registry.add_recognizer(
    PatternRecognizer(
        supported_entity="MAC_ADDRESS",
        patterns=[Pattern("mac", r"\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b", 0.95)]
    )
)

# ---------------------------------------------------
# PIPELINE
# ---------------------------------------------------

def mask_text(text):

    results = analyzer.analyze(text=text, language="en")

    # remove overlaps
    results = sorted(results, key=lambda x: (x.start, -x.end))
    filtered = []
    last_end = -1

    for r in results:
        if r.start >= last_end:
            filtered.append(r)
            last_end = r.end

    masked = text
    entity_map = {}

    for i, r in enumerate(sorted(filtered, key=lambda x: x.start, reverse=True)):

        value = text[r.start:r.end]
        label = r.entity_type

        placeholder = f"[{label}_{i}]"

        entity_map[placeholder] = value

        masked = masked[:r.start] + placeholder + masked[r.end:]

    return masked, entity_map


# ---------------------------------------------------
# STDIN PIPE
# ---------------------------------------------------

def get_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        return None
    length = struct.unpack("@I", raw_length)[0]
    return json.loads(sys.stdin.buffer.read(length).decode("utf-8"))


def send_message(message):
    encoded = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("@I", len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


while True:

    msg = get_message()
    if msg is None:
        break

    text = msg.get("text", "")

    masked, entity_map = mask_text(text)

    send_message({
        "masked_text": masked,
        "entity_map": entity_map
    })