# Docker Troubleshooting Guide - Sprint D-SP-1

## Issue #1: Dashboard "Failed to load" Error ✅ FIXED

**Date:** 18 октября 2025
**Status:** ✅ Resolved

### Problem Description

When opening the Dashboard at `http://localhost:3000/dashboard`, the following error was displayed:

```
Failed to load dashboard
Network error: fetch failed
Make sure the API server is running at http://localhost:8000
```

### Root Cause

Next.js uses **Server-Side Rendering (SSR)** for the Dashboard page. When SSR runs inside the Docker container, it tries to fetch data from the API using `http://localhost:8000`. However, inside a Docker container, `localhost` refers to the container itself, not the host machine or other containers.

The problem occurs because:
1. Next.js Dashboard page is an `async` Server Component
2. It calls `getStats("day")` during SSR (on the server, inside container)
3. The API client uses `process.env.NEXT_PUBLIC_API_URL` which is `http://localhost:8000`
4. Inside the frontend container, `localhost:8000` doesn't point to the API container

### Solution

Use **different URLs for server-side and client-side**:
- **Server-side (SSR in Docker):** `http://api:8000` (Docker service name)
- **Client-side (browser):** `http://localhost:8000` (host machine)

#### Changes Made

**1. Updated `frontend/src/lib/api.ts`:**

```typescript
// Use different URLs for server-side (Docker) and client-side (browser)
// Server-side: use Docker service name 'api'
// Client-side: use localhost for browser
const API_BASE_URL =
  typeof window === "undefined"
    ? process.env.API_URL || "http://api:8000" // Server-side (SSR in Docker)
    : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // Client-side (browser)
```

**Key points:**
- `typeof window === "undefined"` detects if code runs on server (Node.js) or client (browser)
- Server-side uses `process.env.API_URL` (not prefixed with NEXT_PUBLIC)
- Client-side uses `process.env.NEXT_PUBLIC_API_URL` (available in browser)

**2. Updated `docker-compose.yml`:**

```yaml
frontend:
  environment:
    - NEXT_PUBLIC_API_URL=http://localhost:8000  # For browser (client-side)
    - API_URL=http://api:8000                     # For SSR (server-side in Docker)
```

**Key points:**
- `NEXT_PUBLIC_API_URL` - accessible in browser JavaScript
- `API_URL` - only accessible on server-side (not prefixed with NEXT_PUBLIC)

### Verification Steps

```bash
# 1. Rebuild and restart frontend
docker-compose up -d --build frontend

# 2. Wait for startup
sleep 10

# 3. Check Dashboard
curl http://localhost:3000/dashboard

# 4. Check API from frontend container
docker-compose exec frontend wget -O- http://api:8000/health
```

### Test Results

✅ **Before fix:**
- Dashboard showed "Failed to load dashboard" error
- SSR failed to connect to API

✅ **After fix:**
- Dashboard loads successfully
- Statistics displayed correctly
- Both SSR (server-side) and client-side API calls work

### Lessons Learned

1. **Next.js SSR in Docker requires special handling**
   - SSR code runs inside container, not in browser
   - Must use Docker service names for inter-container communication

2. **Environment variables strategy**
   - `NEXT_PUBLIC_*` variables are embedded in browser bundle
   - Non-prefixed variables are only available server-side
   - Use different variables for server vs client

3. **Testing SSR applications**
   - Always test initial page load (SSR)
   - Test client-side navigation
   - Check both server and client logs

### Related Files

- `frontend/src/lib/api.ts` - API client with dual URL support
- `docker-compose.yml` - Environment variables configuration
- `frontend/src/app/dashboard/page.tsx` - Server Component using SSR

### Prevention

For future Next.js + Docker projects:
1. Always consider SSR when using Docker containers
2. Use environment variable detection (`typeof window`)
3. Provide both internal (Docker) and external (host) URLs
4. Test SSR pages separately from client-only pages

---

**Status:** ✅ Resolved
**Impact:** Dashboard now works correctly in Docker environment
**Time to fix:** 15 minutes

