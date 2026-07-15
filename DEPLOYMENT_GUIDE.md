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

## 2. Deploying on Hugging Face Spaces

Hugging Face Spaces is an excellent, free alternative for hosting AI applications, especially Streamlit and Docker-based apps.

### Prerequisites
- A free account on [Hugging Face](https://huggingface.co/).

### Steps
1. Go to your Hugging Face profile and click **New Space**.
2. Set the **Space name** (e.g., `motiveminds-support`).
3. For **License**, choose an appropriate license or leave it blank.
4. For **Space SDK**, choose **Docker**.
5. Choose the **Blank** Docker template.
6. Set the Space hardware to **Free**.
7. Click **Create Space**.
8. In the Space settings, go to the **Variables and secrets** section and add a New Secret:
   - Name: `GOOGLE_API_KEY`
   - Value: your-gemini-key
9. Upload your project files (including the `Dockerfile` and `requirements.txt`) to the Space. You can do this via the browser interface (Add file -> Upload files) or by cloning the Space's Git repository and pushing your code.
10. Hugging Face will automatically detect the `Dockerfile`, build the image, and start your Streamlit app!

> **Note:**
> Since both platforms spin down inactive containers on their free tiers, the in-memory chat history (handled by `MemorySaver`) will reset when the application sleeps and wakes up. This is standard behavior for free deployment environments without an external database.
