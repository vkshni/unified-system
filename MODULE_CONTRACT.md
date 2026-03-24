# Module Interface Contract

Every system integrated into the Unified CLI MUST follow this contract.

## Required Function: `run_shell()`
Every module must expose a `run_shell()` function that:
- Starts an interactive shell with system-specific prompt
- Shows `[system_name]` prefix
- Handles commands in a loop
- Exits cleanly on `exit` command

**Example:**
```python
# In modules/taski/main.py
def run_shell():
    """Interactive shell mode"""
    print("[Entering Task Manager...]")
    while True:
        command = input("[taski] ").strip()
        if command == 'exit':
            break
        # Handle commands...
```

---

## Required Function: `execute_command(args)`
Every module should support direct command execution:
- Takes command + arguments as list
- Executes immediately
- Returns exit code (True = success, False = error)
- No interactive loop

**Example:**
```python
# In modules/taski/main.py
def execute_command(args):
    """Direct command execution"""
    # args = ['add', 'Fix bug', '--priority', 'high']
    if args[0] == 'add':
        # Do the thing
        return True
    return False
```

---

## Module Structure
```
modules/
└── taski/
    ├── main.py          (run_shell(), execute_command())
    ├── commands.py      (command handlers)
    ├── data/            (module's data files)
    └── utils.py         (module-specific helpers)
```

---

## Three Modes of Operation

### 1. Interactive Menu Mode
```bash
$ python main.py
# Shows menu, user types 'taski', enters shell
```

### 2. Shell Mode
```bash
$ python main.py taski
# Directly enters [taski] shell
```

### 3. Direct Execution Mode
```bash
$ python main.py taski add "Fix bug"
# Runs command and exits immediately
```