# Railway Deployment Guide

This guide will help you deploy the AI Mental Health Coach application to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)
2. Railway CLI installed (optional, for local deployment)
3. A PostgreSQL database (Railway provides this)
4. OpenAI API key for AI features

## Deployment Steps

### 1. Fork or Clone the Repository

First, ensure your code is in a GitHub repository.

### 2. Create a New Project on Railway

1. Log in to Railway
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository

### 3. Set Up PostgreSQL Database

1. In your Railway project, click "New Service"
2. Choose "Database" → "PostgreSQL"
3. Railway will automatically provision a PostgreSQL instance

### 4. Configure Environment Variables

In your Railway project settings, add the following environment variables:

```bash
# Database (Railway will auto-populate DATABASE_URL when you add PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

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
FRONTEND_URL=https://your-frontend-url.railway.app
```

### 5. Deploy the Backend

Railway will automatically detect the Python application and deploy it using the configuration files:
- `Procfile` - Defines the start command
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version
- `railway.json` - Railway-specific configuration
- `nixpacks.toml` - Build configuration

The deployment will:
1. Install Python 3.10
2. Install all dependencies from requirements.txt
3. Start the FastAPI application on the assigned port

### 6. Deploy the Frontend (Optional)

For the Next.js frontend in `Frontend/mindful-app/`:

1. Create a separate Railway service for the frontend
2. Set the root directory to `Frontend/mindful-app/`
3. Add environment variables:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```
4. Railway will automatically detect Next.js and deploy it

### 7. Verify Deployment

1. Check the deployment logs in Railway
2. Visit your backend URL (e.g., `https://your-app.railway.app`)
3. You should see the health check response: `{"status": "ok", "service": "ai-mental-health-coach"}`
4. Test the API documentation at `https://your-app.railway.app/docs`

## Post-Deployment Steps

### 1. Database Migrations

The application will automatically create tables on first run. If you need to run migrations manually:

```bash
# Connect to Railway shell
railway run python -m alembic upgrade head
```

### 2. Update CORS Settings

Update the `FRONTEND_URL` environment variable with your actual frontend URL to ensure proper CORS configuration.

### 3. Monitor Application

- Use Railway's built-in metrics to monitor performance
- Check logs for any errors
- Set up alerts for downtime

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure DATABASE_URL is properly set
   - Check if PostgreSQL service is running

2. **Import Errors**
   - Verify all dependencies are in requirements.txt
   - Check Python version compatibility

3. **Port Binding Errors**
   - Ensure the app uses `$PORT` environment variable
   - Don't hardcode port numbers

4. **CORS Errors**
   - Update FRONTEND_URL environment variable
   - Check allowed origins configuration

### Logs

View logs in Railway dashboard or using CLI:
```bash
railway logs
```

## Security Considerations

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong SECRET_KEY values
   - Rotate API keys regularly

2. **Database**
   - Railway PostgreSQL is secure by default
   - Regular backups are recommended
   - Use connection pooling for production

3. **API Security**
   - JWT tokens expire after 30 minutes by default
   - All endpoints except health check require authentication
   - Rate limiting is recommended for production

## Scaling

Railway supports horizontal scaling:
1. Increase replicas in railway.json
2. Configure load balancing
3. Use Redis for session management (if needed)

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: Create an issue in the GitHub repository 