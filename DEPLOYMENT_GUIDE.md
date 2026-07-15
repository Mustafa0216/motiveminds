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

## 2. Deploying on Streamlit Community Cloud

Since this is a Streamlit application, the **Streamlit Community Cloud** is actually the most native and seamless way to deploy it for free. It pulls directly from your GitHub repository and handles all the infrastructure for you automatically.

### Prerequisites
- A GitHub account.
- A free account on [Streamlit Community Cloud](https://share.streamlit.io/).

### Steps
1. Log into Streamlit Community Cloud using your GitHub account.
2. Click **New app** -> **Use existing repo**.
3. Select your `motiveminds` repository from the dropdown.
4. Set the **Main file path** to `app.py`.
5. Before clicking deploy, click on **Advanced settings**.
6. In the **Secrets** section (which acts exactly like your `.env` file), paste your API keys like this:
   ```toml
   GOOGLE_API_KEY="your-gemini-key"
   OPENAI_API_KEY="your-openai-key" # Optional
   ```
7. Click **Save** and then click **Deploy!**
8. Streamlit will automatically read your `requirements.txt`, install everything, and launch your app. It will give you a public shareable link instantly.

> **Note:**
> Just like Render, apps on the free Community Cloud will go to sleep if they haven't been visited for a few days. The memory checkpointer will reset when the app wakes up.
