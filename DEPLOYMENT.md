# Deployment Guide

## Frontend Deployment (Vercel)

1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your GitHub repository
4. Set environment variables:
   - `REACT_APP_BACKEND_URL` = your backend URL (e.g., https://budget-backend.railway.app)
5. Deploy

## Backend Deployment (Railway.app)

### Step 1: Prepare Backend for Railway

1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository

### Step 2: Configure Environment in Railway Dashboard

In Railway project settings, add these environment variables:

- `MONGO_URL` = your MongoDB Atlas connection string
- `DB_NAME` = budget_db

### Step 3: Set Start Command

Railway should auto-detect Python. If needed, set:

```
python backend/server.py
```

Or in Procfile (optional):

```
web: python backend/server.py
```

### Step 4: Get Your Backend URL

Once deployed, Railway will provide a URL like:

```
https://budget-api.railway.app
```

### Step 5: Update Frontend

Set `REACT_APP_BACKEND_URL` in Vercel to your Railway backend URL.

## MongoDB Setup

Your MongoDB connection string should stay private and only live in `backend/.env`.

Create `backend/.env` with values like:

```
MONGO_URL=mongodb+srv://<USERNAME>:<PASSWORD>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority
DB_NAME=budget_db
```

Do not commit this file to the repository.
