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

## 2. Deploying on Koyeb

[Koyeb](https://www.koyeb.com) is an excellent developer-friendly platform that offers a generous free tier (EcoFree) for running Docker containers directly from GitHub.

### Prerequisites
- A GitHub account.
- A free account on [Koyeb](https://app.koyeb.com/).

### Steps
1. Log into your Koyeb dashboard.
2. Click **Create Service**.
3. Select **GitHub** as the deployment method and connect your account.
4. Select your `motiveminds` repository.
5. In the **Builder** section, select **Dockerfile**. Koyeb will automatically detect the `Dockerfile` in the root of your repository.
6. In the **Environment variables** section, add your API keys:
   - Key: `GOOGLE_API_KEY` | Value: `your-gemini-key`
   - Key: `OPENAI_API_KEY` | Value: `(optional)`
7. Scroll down to the **Instance** section and select the **Free** (EcoFree) tier.
8. Click **Deploy**.
9. Koyeb will build the Docker container and start your Streamlit app. You can monitor the build process in the logs and access the app via the public URL provided!

> **Note:**
> Just like Render, the free tier on Koyeb may sleep after a period of inactivity, which will reset the in-memory checkpointer. This is standard across free hosting providers.
