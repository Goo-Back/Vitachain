# Supabase Integration Fix Guide

## Problem Identified
The current Supabase project URL `https://bgdtqvpchfnrscupyyaa.supabase.co` returns 404, indicating the project reference is incorrect or the project doesn't exist.

## Solution Steps

### 1. Create New Supabase Project
1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Choose organization
4. Set project name: `vitachain`
5. Set database password: (generate secure password)
6. Choose region: EU West (Frankfurt)
7. Click "Create new project"

### 2. Update Environment Variables
Once project is created, update the `.env` file with:

```bash
# Replace with actual project values
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_ANON_KEY=YOUR_ANON_KEY_HERE
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVICE_ROLE_KEY_HERE
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_ID.supabase.co:5432/postgres
```

### 3. Run Database Setup
```bash
cd database
./supabase-setup.sh
```

### 4. Verify Setup
```bash
powershell -ExecutionPolicy Bypass -File verify-setup.ps1
```

## Temporary Workaround

For now, let's create a mock Supabase configuration for development:

### Frontend Configuration
Update `frontend/lib/supabase.ts` with mock configuration:

```typescript
// Mock Supabase client for development
export const supabase = {
  auth: {
    signIn: () => Promise.resolve({ data: { user: null }, error: null }),
    signOut: () => Promise.resolve({ error: null }),
    getUser: () => Promise.resolve({ data: { user: null }, error: null })
  },
  from: (table: string) => ({
    select: () => Promise.resolve({ data: [], error: null }),
    insert: () => Promise.resolve({ data: null, error: null }),
    update: () => Promise.resolve({ data: null, error: null }),
    delete: () => Promise.resolve({ data: null, error: null })
  })
}
```

### Backend Configuration
Update `backend/app/core/config.py` with local database:

```python
# Use local PostgreSQL for development
database_url = "postgresql://postgres:test@localhost:5432/vitachain_dev"
```

## Next Actions Required

1. **Create new Supabase project** (requires manual action)
2. **Update environment variables** with new project credentials
3. **Re-run database setup** with correct project URL
4. **Test integration** with new configuration

## Immediate Fix Available

The application can run with mock/local database for development while Supabase project is being set up properly.
