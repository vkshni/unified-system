# Code Duplication Report

## ID Generation
**Found in:** All 6 systems  
**Pattern:**
- IDGenerator: Uses incremental IDs (using `counter.json`)
- PennyTracker: Uses `uuid.uuid4()`
- TaskManager: Uses `uuid.uuid4()`
- PasswordManager: Uses `uuid.uuid4()`
- URLShortener: Uses `uuid.uuid4()`
- SnippetManager: Uses incremental timestamp ID (e.g. 23032026_00003)

**Action Needed:** Create unified ID generator that supports both methods (Incremental and UUID)

---

## File Operations
**Found in:** All 6 systems  
**Pattern:**
```python
# This appears 4+ times:
with open('file.json', 'r') as f:
    data = json.load(f)

# This appears 4+ times:
with open('file.json', 'w') as f:
    json.dump(data, f, indent=4)

# In PennyTracker and TaskManager:
with open('file.csv', 'r') as f:
    reader = csv.reader(f)

with open('file.csv', 'w') as f:
    writer = csv.writer(f)

with open('file.csv', 'a') as f:
    writer = csv.writer(f)
```

**Action Needed:** Create `read_json()`,`write_json()` and `read_csv()`, `write_csv()`, `append_csv()` functions

---

## Input Validation
**Found in:** PennyTracker (Amount, Date), TaskManager (States, Date), URLShortener (URL), SnippetManager (Access level, tag)  
**Patterns:**
- Empty Fields: Used everywhere (in all 6)
- Amount: Checks `if amount > 0`
- Date: Check format `DD-MM-YYYYTHH:MM:SS`
- URL: Checks `if 0 < len(URL) < 2000`, has `.`, has `https:\\` or `http:\\`
- States (TaskManager): `TODO`,`IN_PROGRESS`,`DONE`,`CANCELLED`
- Access level: `PUBLIC` or `LOCKED`
- Tag: No spaces and lowercase values only (system automatically rectifies)

**Action Needed:** Create validator module with reusable functions

---
## Display/UI Functions
**Found in:** All 6  
**Patterns:**
- Headers: In all 6
- Menus: in only PasswordManager (after login)
- CLI commands: in rest all

**Action Needed:** Incorporate both menu and CLI command method