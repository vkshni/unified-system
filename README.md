# Unified CLI System v1.0

A modular command-line platform integrating 6 independent micro-systems into a single, cohesive interface. Built as part of a 7-week systems engineering learning project.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Systems](#-integrated-systems)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
  - [ID Generator](#1-id-generator-idgen)
  - [Penny Tracker](#2-penny-tracker-penny)
  - [Task Manager](#3-task-manager-taski)
  - [Password Manager](#4-password-manager-shield)
  - [URL Shortener](#5-url-shortener-shorturl)
  - [Snippet Manager](#6-snippet-manager-snippet)
- [Architecture](#-architecture)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This project demonstrates **modular system design** by combining 6 previously standalone CLI tools into one unified platform. Each system maintains its independence while sharing common utilities and authentication.

### Key Features

✅ **Unified Interface** - One entry point for all systems  
✅ **Modular Architecture** - Systems work independently  
✅ **Shared Utilities** - No code duplication  
✅ **Centralized Authentication** - Single master password  
✅ **Three Usage Modes** - Menu, Shell, Direct command  
✅ **Professional CLI UX** - Consistent patterns across all systems  

---

## 🧩 Integrated Systems

| System | Command | Description | Auth Required |
|--------|---------|-------------|---------------|
| **ID Generator** | `idgen` | Generate prefixed IDs with counters | ❌ No |
| **Penny Tracker** | `penny` | Track and categorize expenses | ❌ No |
| **Task Manager** | `taski` | Manage tasks with state transitions | ❌ No |
| **Password Manager** | `shield` | Securely store passwords | 🔒 Yes |
| **URL Shortener** | `shorturl` | Shorten and track URLs | ❌ No |
| **Snippet Manager** | `snippet` | Store code snippets and commands | 🔒 Yes |

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd unified-cli-system

# Install dependencies
pip install colorama tabulate

# First-time setup (for protected systems)
python main.py init
```

When prompted, create a master password:
- Minimum 6 characters
- Must contain both letters and numbers
- Used for: penny, shield, snippet

---

## 🚀 Quick Start

### Three Ways to Use the System

#### 1️⃣ Interactive Menu Mode
```bash
python main.py
```
Shows all available systems and prompts you to choose one.

#### 2️⃣ Shell Mode
```bash
python main.py taski
[taski] add "Buy groceries"
[taski] list
[taski] exit
```
Enters a system's interactive shell for multiple commands.

#### 3️⃣ Direct Command Mode
```bash
python main.py taski add "Buy groceries" --note "Milk, eggs"
```
Executes a single command and exits immediately.

---

## 📖 Usage Guide

### General Commands

```bash
# Show help
python main.py help

# Initialize system (first-time)
python main.py init

# Enter interactive menu
python main.py

# Get help for a specific system
python main.py taski help
```

---

## 1. ID Generator (`idgen`)

Generate unique IDs with custom prefixes, counters, and formatting.

### Features
- Multiple ID types with different formats
- Configurable prefixes, padding, and increments
- Random password generation

### Commands

#### Add ID Type
```bash
python main.py idgen add --name TASK --start 1 --step 1 --prefix T --padding 3
```
Creates a new ID type: `T001`, `T002`, `T003`...

#### Generate ID
```bash
python main.py idgen generate TASK
```
Output: `T001`

#### List All ID Types
```bash
python main.py idgen list
```

#### Update ID Type
```bash
python main.py idgen update TASK --step 5 --padding 4
```

#### Reset Counter
```bash
python main.py idgen reset TASK
```

#### Generate Password
```bash
python main.py idgen genpass --length 16
```

#### Delete ID Type
```bash
python main.py idgen delete TASK --force
```

### Shell Mode Example
```bash
python main.py idgen
[idgen] add --name USER --start 1000 --step 1 --prefix U --padding 4
[idgen] generate USER
[idgen] generate USER
[idgen] list
[idgen] exit
```

---

## 2. Penny Tracker (`penny`)

Track expenses with categories and date-based filtering.

🔒 **Authentication Required**

### Features
- Add, view, edit, and delete expenses
- Filter by category or date range
- Monthly summary with category breakdown
- CSV storage

### Commands

#### Add Expense
```bash
python main.py penny add --amount 150 --category food --date 06-04-2026 --note "Lunch"
```

#### View All Expenses
```bash
python main.py penny view
```

#### Filter by Category
```bash
python main.py penny filter --category food
```

#### Filter by Date Range
```bash
python main.py penny filter --from 01-04-2026 --to 07-04-2026
```

#### Monthly Summary
```bash
python main.py penny summary --month 4 --year 2026
```

#### Edit Expense
```bash
python main.py penny edit 1 --amount 200 --note "Updated lunch cost"
```

#### Delete Expense
```bash
python main.py penny delete 1
```

### Shell Mode Example
```bash
python main.py penny
[penny] add --amount 50 --category transport --date 06-04-2026
[penny] view
[penny] summary --month 4 --year 2026
[penny] exit
```

### Common Categories
- `food` - Meals, groceries
- `transport` - Travel, fuel
- `entertainment` - Movies, games
- `bills` - Utilities, rent
- `shopping` - Clothing, electronics
- `health` - Medical, fitness
- `education` - Books, courses
- `other` - Miscellaneous

---

## 3. Task Manager (`taski`)

Manage tasks with state transitions and priorities.

### Features
- Add tasks with titles and notes
- State transitions: TODO → IN_PROGRESS → DONE
- Filter tasks by state, date, or title
- Update and delete tasks

### Commands

#### Add Task
```bash
python main.py taski add "Buy groceries" --note "Milk, eggs, bread"
```

#### List All Tasks
```bash
python main.py taski list
```

#### Advance Task State
```bash
python main.py taski advance 1 in_progress
python main.py taski advance 1 done
```

#### Update Task
```bash
python main.py taski update 2 --title "Buy groceries and fruits" --note "Updated list"
```

#### Delete Task
```bash
python main.py taski delete 3
```

#### Filter Tasks
```bash
python main.py taski filter state TODO
python main.py taski filter created_on "06-04-2026"
```

### Shell Mode Example
```bash
python main.py taski
[taski] add "Learn Python" --note "Complete tutorial"
[taski] list
[taski] advance 1 in_progress
[taski] filter state IN_PROGRESS
[taski] exit
```

### Task States
- `TODO` - Not started
- `IN_PROGRESS` - Currently working on
- `DONE` - Completed
- `CANCELLED` - Abandoned

### State Transition Rules
- Cannot skip states (TODO → DONE not allowed)
- Cannot modify DONE tasks
- Cannot reverse transitions
- Flow: TODO → IN_PROGRESS → DONE

---

## 4. Password Manager (`shield`)

Securely store and manage passwords with master password protection.

🔒 **Authentication Required**

### Features
- Store passwords with service name and label
- Multiple accounts per service
- Master password verification to view passwords
- Update and delete credentials

### Commands

#### Add Password
```bash
python main.py shield add --service github --username john@email.com --password pass123
python main.py shield add --service gmail --username john@gmail.com --password abc123 --label personal
```

#### List Stored Services
```bash
python main.py shield list
```

#### Get Password (requires verification)
```bash
python main.py shield get github
python main.py shield get gmail --label personal
```
*Prompts for master password before displaying*

#### Update Password
```bash
python main.py shield update github --password newpass456
python main.py shield update github --username newemail@example.com
```

#### Delete Password
```bash
python main.py shield delete github
python main.py shield delete gmail --label personal --force
```

### Shell Mode Example
```bash
python main.py shield
[shield] add --service twitter --username @john --password tw123
[shield] list
[shield] get twitter
[shield] update twitter --password newtwpass
[shield] exit
```

### Security Features
- Master password hashing (SHA-256)
- Password verification required to view
- Session timeout (1 hour)
- Lockout after 3 failed attempts (30 seconds)

---

## 5. URL Shortener (`shorturl`)

Shorten URLs and track visit counts.

### Features
- Generate short codes for long URLs
- Resolve short codes to original URLs
- Track visit counts
- List all shortened URLs

### Commands

#### Shorten URL
```bash
python main.py shorturl shorten "https://example.com/very/long/path/to/page"
```
Output: `Created: short.ly/abc123`

#### Resolve Short Code
```bash
python main.py shorturl resolve abc123
```
Output: `→ https://example.com/very/long/path/to/page`

#### List All URLs
```bash
python main.py shorturl list
```

### Shell Mode Example
```bash
python main.py shorturl
[shorturl] shorten "https://github.com/user/repo"
[shorturl] list
[shorturl] resolve xyz789
[shorturl] exit
```

### Notes
- URLs must start with `http://` or `https://`
- Duplicate URLs return existing short code
- Short codes are automatically generated (6 characters)
- Visit count increments on each resolve

---

## 6. Snippet Manager (`snippet`)

Store and manage code snippets, commands, and notes.

🔒 **Authentication Required** (for locked snippets)

### Features
- Store snippets with title, content, and tags
- Lock snippets with master password protection
- Archive snippets (hide from default list)
- Search by keyword or tag
- Tag-based organization

### Commands

#### Add Snippet
```bash
python main.py snippet add "Git Reset" "git reset --hard HEAD" --tag git
python main.py snippet add "API Key" "sk-123..." --tag secrets --access LOCKED
```

#### List Snippets
```bash
python main.py snippet list
python main.py snippet list --tag python
python main.py snippet list --archived
```

#### Search Snippets
```bash
python main.py snippet search docker
```

#### View Snippet
```bash
python main.py snippet view 19032026_00001
```
*Locked snippets require master password*

#### Archive Snippet
```bash
python main.py snippet archive 19032026_00001
```

#### Unarchive Snippet
```bash
python main.py snippet unarchive 19032026_00001
```

#### Lock Snippet
```bash
python main.py snippet lock 19032026_00002
```

#### Unlock Snippet (requires verification)
```bash
python main.py snippet unlock 19032026_00002
```

### Shell Mode Example
```bash
python main.py snippet
[snippet] add "Docker Run" "docker run -it ubuntu bash" --tag docker
[snippet] list --tag docker
[snippet] view 19032026_00001
[snippet] lock 19032026_00001
[snippet] exit
```

### Access Levels
- `PUBLIC` - No password required (default)
- `LOCKED` - Master password required to view

### Common Tags
- `git` - Git commands
- `docker` - Docker commands
- `python` - Python code
- `bash` - Shell scripts
- `sql` - SQL queries
- `secrets` - API keys, tokens
- `notes` - General notes

---

## 🏗️ Architecture

### Project Structure

```
unified-cli-system/
├── main.py                 # Entry point & mode detection
├── config/
│   └── systems.py          # System registry (metadata)
├── core/
│   └── router.py           # Routing & module loading
├── auth/
│   ├── auth_manager.py     # Centralized authentication
│   └── data/
│       ├── session.json    # Login session
│       ├── vault_meta.json # Master password hash
│       └── attempts.json   # Failed login tracking
├── shared/
│   ├── id_generator.py     # Shared ID generation
│   ├── file_handler.py     # JSON/CSV operations
│   ├── validators.py       # Input validation
│   └── ui_utils.py         # UI components (tables, colors)
└── modules/
    ├── idgen/
    │   ├── main.py         # Shell & command execution
    │   ├── engine.py       # Business logic
    │   └── data/           # System data
    ├── penny/
    ├── taski/
    ├── shield/
    ├── shorturl/
    └── snippet/
```

### Design Principles

1. **Modularity** - Each system is self-contained
2. **DRY (Don't Repeat Yourself)** - Shared utilities for common operations
3. **Separation of Concerns** - Clear boundaries between layers
4. **Unified Interface** - Consistent command patterns
5. **Single Source of Truth** - Centralized system registry

### Data Flow

```
User Input
    ↓
main.py (argument parsing)
    ↓
router.py (system validation, auth check, module import)
    ↓
modules/*/main.py (run_shell or execute_command)
    ↓
modules/*/engine.py (business logic)
    ↓
shared utilities (file operations, validation)
    ↓
Data persistence
```

---

## 🔐 Authentication System

### Protected Systems
- `penny` - Expense Tracker
- `shield` - Password Manager
- `snippet` - Snippet Manager (for locked snippets)

### Authentication Flow

1. **First-time setup:**
   ```bash
   python main.py init
   ```
   Creates master password (min 6 chars, alphanumeric)

2. **Automatic login:** Protected systems prompt for password on first access

3. **Session persistence:** Login valid for 1 hour

4. **Manual logout:** Handled automatically when exiting systems

5. **Security features:**
   - Password hashing (SHA-256)
   - Lockout after 3 failed attempts
   - 30-second lockout duration
   - Session timeout

---

## 🛠️ Development

### Module Structure

Each module follows this standard pattern:

```python
# modules/<system>/main.py

def run_shell():
    """Interactive shell mode"""
    while True:
        cmd = input("[system] ")
        if cmd == "exit":
            break
        execute_command(cmd.split())

def execute_command(args):
    """Direct command execution"""
    command = args[0]
    # Route to appropriate handler
    # Return exit code (0 = success, 1 = error)

def cmd_<action>(args):
    """Individual command handlers"""
    # Parse arguments
    # Execute business logic
    # Return exit code
```

### Adding a New System

1. **Create module folder:**
   ```bash
   mkdir modules/newsystem
   ```

2. **Implement required functions:**
   - `run_shell()` - Interactive mode
   - `execute_command(args)` - Direct execution
   - `cmd_help()` - Help documentation

3. **Add to system registry:**
   ```python
   # config/systems.py
   SYSTEMS = {
       "newsystem": {
           "name": "New System",
           "description": "Description",
           "module": "modules.newsystem.main",
           "protected": False  # or True if auth required
       }
   }
   ```

4. **Use shared utilities:**
   ```python
   from shared.ui_utils import print_success, print_error, print_table
   from shared.validators import validate_not_empty
   from shared.file_handler import JSONFile
   ```

### Code Style Guidelines

- **Consistent error handling:** Use try-except, return exit codes
- **User-friendly messages:** Use shared UI utilities
- **Input validation:** Use shared validators
- **No print in business logic:** Return data, let UI layer print
- **Lazy initialization:** Use `get_<manager>()` pattern
- **Help commands:** Always provide comprehensive help

---

## 📊 File Locations

### User Data
All user data is stored in `modules/<system>/data/`:
- `modules/penny/data/expenses.csv`
- `modules/taski/data/tasks.csv`
- `modules/shield/data/vault_data.json`
- `modules/snippet/data/snippets.json`

### System Data
Authentication and shared data in dedicated folders:
- `auth/data/session.json`
- `auth/data/vault_meta.json`
- `shared/data/counters.json`

### Backups
Consider backing up these directories regularly:
- `modules/*/data/`
- `auth/data/`

---

## ⚡ Performance

### Optimization Features
- **Lazy imports:** Heavy libraries loaded only when needed
- **Lazy initialization:** System objects created on first use
- **Efficient routing:** Dynamic imports prevent loading unused systems
- **Minimal dependencies:** Only colorama and tabulate required

### Expected Performance
- Help commands: < 0.5 seconds
- Simple commands: < 1 second
- Data-heavy operations: 1-2 seconds

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'shared'`
```bash
# Solution: Ensure you're running from project root
cd unified-cli-system
python main.py <command>
```

**Issue:** `System not initialized`
```bash
# Solution: Run first-time setup
python main.py init
```

**Issue:** `Authentication required`
```bash
# Solution: Protected systems need login
# They will prompt for password automatically
```

**Issue:** Commands running slow
```bash
# Solution: Install dependencies
pip install colorama tabulate
```

**Issue:** `Locked out! Try after 30 seconds`
```bash
# Solution: Wait 30 seconds after 3 failed login attempts
# Or delete auth/data/attempts.json (emergency only)
```

---

## 📝 Tips & Best Practices

### General Usage
- Use **shell mode** for multiple operations on one system
- Use **direct mode** for quick one-off commands
- Use **menu mode** when exploring available systems

### Data Management
- Backup `modules/*/data/` folders regularly
- Export important data periodically
- Use meaningful tags and labels for organization

### Security
- Use a strong master password (8+ characters)
- Don't share master password
- Lock sensitive snippets
- Regularly review stored passwords

### Productivity
- Create shell aliases for frequent commands:
  ```bash
  alias t="python /path/to/main.py taski"
  alias p="python /path/to/main.py penny"
  ```

---

## 🎓 Learning Outcomes

This project demonstrates:

1. **Modular Architecture** - Independent systems with clear boundaries
2. **Code Reusability** - Shared utilities eliminate duplication
3. **Separation of Concerns** - UI, business logic, and data layers
4. **Authentication** - Centralized security with session management
5. **CLI Design** - Professional command-line interface patterns
6. **Error Handling** - Graceful failures with user-friendly messages
7. **Testing Integration** - How well-designed systems integrate easily

---

## 📜 License

This project is for educational purposes as part of a systems engineering learning program.

---

## 🤝 Contributing

This is a learning project, but suggestions are welcome! Focus areas:
- Additional micro-systems
- Performance optimizations
- Security enhancements
- UI/UX improvements

---

## 🎉 Acknowledgments

Built as Week 7 of a micro-systems engineering curriculum focused on:
- Modular design
- System integration
- Professional CLI development
- Software architecture principles

---

**Version:** 1.0  
**Last Updated:** April 2026  
**Python:** 3.8+