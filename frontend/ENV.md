# Environment Variables Setup

Create a `.env.local` file in the `frontend/` directory with the following content:

```env
# Backend API URL
# Development: http://localhost:8000
# Production: replace with your production API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Instructions

1. Copy this content to `.env.local`:
   ```bash
   cd frontend
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

2. For production, update the URL to your production API endpoint

3. The `.env.local` file is already in `.gitignore` and won't be committed to git

## Available Variables

- `NEXT_PUBLIC_API_URL` - Backend API base URL (required)
  - Must start with `NEXT_PUBLIC_` to be accessible in the browser
  - Default: `http://localhost:8000`

