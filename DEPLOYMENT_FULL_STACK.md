# Full Stack Deployment Guide for Railway

This guide covers deploying both the backend (FastAPI) and frontend (Next.js) applications to Railway.

## Architecture Overview

You'll create two separate Railway services:
1. **Backend Service** - FastAPI API at `https://your-backend.railway.app`
2. **Frontend Service** - Next.js app at `https://your-frontend.railway.app`

## Step 1: Deploy the Backend

### 1.1 Create Backend Service

1. Go to [Railway](https://railway.app) and create a new project
2. Click "New Service" → "GitHub Repo"
3. Select your repository
4. Railway will automatically detect the Python app

### 1.2 Add PostgreSQL Database

1. In the same project, click "New Service" → "Database" → "PostgreSQL"
2. Railway will automatically set the `DATABASE_URL` environment variable

### 1.3 Configure Backend Environment Variables

Add these environment variables in the Railway backend service settings:

```bash
# JWT Configuration
SECRET_KEY=your-very-secure-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Application Settings
ENVIRONMENT=production
DEBUG=False

# Frontend URL (update after deploying frontend)
FRONTEND_URL=https://your-frontend.railway.app
```

### 1.4 Deploy Backend

Railway will automatically deploy using:
- `.nixpacks.json` - Build configuration
- `requirements.txt` - Python dependencies
- `railway.json` - Deployment settings
- `.railwayignore` - Files to exclude

## Step 2: Deploy the Frontend

### 2.1 Create Frontend Service

1. In the same Railway project, click "New Service" → "GitHub Repo"
2. Select the same repository
3. **Important**: Set the root directory to `Frontend/mindful-app/`

### 2.2 Configure Frontend Environment Variables

Add this environment variable in the Railway frontend service settings:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

Replace `your-backend.railway.app` with your actual backend URL from Step 1.

### 2.3 Deploy Frontend

Railway will automatically:
1. Detect the Next.js application
2. Run `npm install` or `npm ci`
3. Run `npm run build`
4. Start with `npm run start`

## Step 3: Update CORS Settings

After both services are deployed:

1. Go back to your backend service settings
2. Update the `FRONTEND_URL` environment variable with your actual frontend URL
3. Railway will automatically redeploy the backend

## Step 4: Verify Deployment

### Backend Health Check
```bash
curl https://your-backend.railway.app/
# Should return: {"status": "ok", "service": "ai-mental-health-coach"}
```

### API Documentation
Visit: `https://your-backend.railway.app/docs`

### Frontend
Visit: `https://your-frontend.railway.app`

## Alternative: Monorepo Deployment (Single Service)

If you prefer to deploy both frontend and backend as a single service, you can create a custom start script. However, this is more complex and not recommended for production.

## Project Structure in Railway

Your Railway project will look like this:
```
My Project
├── Backend Service (FastAPI)
│   ├── Environment Variables
│   └── Deployment Settings
├── Frontend Service (Next.js)
│   ├── Environment Variables
│   └── Deployment Settings
└── PostgreSQL Database
    └── Connection String
```

## Deployment Commands

### Using Railway CLI (Optional)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy backend
railway up

# Deploy frontend (from Frontend/mindful-app directory)
cd Frontend/mindful-app
railway up
```

## Troubleshooting

### Frontend Can't Connect to Backend

1. Check CORS settings in backend (`FRONTEND_URL` environment variable)
2. Verify `NEXT_PUBLIC_API_URL` in frontend is correct
3. Ensure both services are running

### Build Failures

1. Check Railway build logs
2. Ensure all dependencies are in `package.json` or `requirements.txt`
3. Verify root directory settings for frontend

### Database Connection Issues

1. Railway automatically sets `DATABASE_URL` when you add PostgreSQL
2. Check if the backend service can see the database service
3. Verify database migrations ran successfully

## Monitoring

1. **Logs**: Available in each service's dashboard
2. **Metrics**: CPU, Memory, and Network usage
3. **Deployments**: History of all deployments
4. **Environment Variables**: Manage secrets securely

## Costs

Railway offers:
- $5 free credit monthly
- Pay-as-you-go pricing
- Separate billing for each service

## Next Steps

1. Set up custom domains (optional)
2. Configure auto-scaling if needed
3. Set up monitoring and alerts
4. Implement CI/CD with GitHub Actions

## Support Resources

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Next.js on Railway: https://docs.railway.app/guides/nextjs
- FastAPI on Railway: https://docs.railway.app/guides/fastapi 