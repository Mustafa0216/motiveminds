# Deployment Guide

This application is ready to be deployed on free tier platforms. The Redis dependency has been detached from the required services, and the app will gracefully fall back to an in-memory checkpointer.

## 1. Deploying on Render (Recommended)

Render offers a free tier for web services that spin down after 15 minutes of inactivity. It is perfectly suited for this Streamlit application.

### Prerequisites
- A GitHub account.
- A free account on [Render](https://render.com).

### Steps
1. Push this codebase to a repository on your GitHub account.
2. Log into your Render dashboard.
3. Click on **New** -> **Blueprint**.
4. Connect your GitHub account (if not already connected) and select the repository containing this app.
5. Render will automatically detect the `render.yaml` file in the repository.
6. Provide a name and approve the creation of the `motiveminds-app` Web Service.
7. Wait for the initial build and deployment to finish (it will build the Docker image and deploy it).
8. Once deployed, click on the Web Service in your dashboard, go to the **Environment** tab, and add your API keys:
   - `GOOGLE_API_KEY`: your-gemini-key
   - `OPENAI_API_KEY`: (optional, if you're using OpenAI)
9. Restart the service to apply the environment variables.

---

## 2. Deploying on Railway

[Railway](https://railway.app) is a highly reliable cloud platform that makes deploying Docker applications incredibly straightforward. They offer a trial tier that is great for testing small projects.

### Prerequisites
- A GitHub account.
- An account on [Railway](https://railway.app/).

### Steps
1. Log into your Railway dashboard.
2. Click **New Project** and select **Deploy from GitHub repo**.
3. Select your `motiveminds` repository.
4. Railway will automatically detect your `Dockerfile` and begin building the application.
5. While it builds, go to the **Variables** tab in your Railway project.
6. Add your API keys as environment variables:
   - `GOOGLE_API_KEY`: your-gemini-key
   - `OPENAI_API_KEY`: (optional, if you're using OpenAI)
7. Go to the **Settings** tab and scroll down to **Networking**.
8. Click **Generate Domain** to get a public URL for your application (e.g., `motiveminds-production.up.railway.app`).
9. Your app will redeploy with the environment variables and become accessible at the generated URL!

> **Note:**
> Railway uses your Dockerfile exactly as configured. Because we removed the Redis dependency and shifted to `MemorySaver`, your chat history will be stored in-memory and will reset if the Railway container restarts.
