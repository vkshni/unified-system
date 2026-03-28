# Authentication Policy

## Protected Systems (Require Login)
1. **Password Manager (shield)** - YES (stores sensitive passwords)
2. **Expense Tracker (penny)** - YES (financial data)
3. **Snippet Manager (snippet)** - YES (has PUBLIC/LOCKED access levels)

## Public Systems (No Login Required)
1. **Task Manager (taski)** - NO (tasks aren't sensitive)
2. **URL Shortener (shortly)** - NO (public URLs)
3. **ID Generator (idgen)** - NO (just generates IDs)

## Access Rules
- Protected systems check auth on every command
- If not logged in → prompt for password
- Session lasts 1 hour
- Can logout manually with `logout` command
