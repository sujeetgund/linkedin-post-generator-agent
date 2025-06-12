# 🚀 LinkedIn Post Generator Agent

A modular, agent-based system for crafting engaging LinkedIn posts. This project uses Google ADK (Agent Development Kit) to orchestrate multiple specialized sub-agents, ensuring a polished, professional final post — complete with behind-the-scenes storytelling, optimized hashtags, and an optional image.


## 📝 Project Overview

I launched this project after noticing a clear pattern - While more people are sharing on LinkedIn, many posts end up blending together, often carrying that generic, AI-generated feel.
If AI is already part of the process, why not build a tool that empowers **users to create posts that stand out** and **authentically reflect their unique voice and goals**?

This project implements a multi-phase, agent-based workflow to do just that:

✅ **Phase 1:** Gather post intent and additional details  
✅ **Phase 2:** Generate a compelling behind story  
✅ **Phase 3:** Suggest relevant hashtags  
✅ **Phase 4:** Craft a complete post  
✅ **Phase 5:** (Optional) Generate a prompt-based image  

All phases are orchestrated by a manager agent, delegating to sub-agents for each specialized task.


## 📂 Project Structure

```
.
├── .gitignore
├── .vscode/settings.json
├── LICENSE
├── README.md
├── requirements.txt
└── linkedin_post_agent/
    ├── .env
    ├── agent.py
    ├── constants.py
    ├── prompt.py
    └── sub_agents/
        ├── story_agent/
        │   ├── agent.py
        │   └── prompt.py
        ├── hashtag_agent/
        │   ├── agent.py
        │   └── prompt.py
        ├── post_agent/
        │   ├── agent.py
        │   └── prompt.py
        └── image_agent/
            ├── agent.py
            ├── prompt.py
            └── tools/create_image.py
```


## ⚡️ Installation & Setup

Follow these steps to get the project up and running:

```bash
# Clone this repository
git clone https://github.com/sujeetgund/linkedin-post-generator-agent.git
cd linkedin-post-generator-agent

# Set up a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```


## 🔑 Setting up Application Secrets

Create a `.env` file in the `linkedin_post_agent/` directory based on the provided `.env.example` file:

```bash
cd linkedin_post_agent
cp .env.example .env
```

### Google API

This project uses the Google Gemini API for generating content and images.

1. Visit the [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **"Create API key"** and copy it.

4. Add your Gemini API key to `.env`:

    ```
    GOOGLE_API_KEY=your_gemini_api_key
    ```

### Cloudinary API

To enable image uploads, you'll need to set up Cloudinary credentials:

1. [Sign up for a free Cloudinary account](https://cloudinary.com/users/register) if you don't have one.
2. After logging in, go to your [Cloudinary Dashboard](https://cloudinary.com/console).
3. Locate your **Cloud name**, **API Key**, and **API Secret** under the "Account Details" section.
4. Add these values to your `.env` file:

    ```
    CLOUDINARY_CLOUD_NAME=your_cloud_name
    CLOUDINARY_API_KEY=your_api_key
    CLOUDINARY_API_SECRET=your_api_secret
    ```

These credentials allow the agent to upload and manage images for your LinkedIn posts.

## 🚀 Running the Agent

To start the agent system, run:

```bash
python -m linkedin_post_agent
```

This command launches the FastAPI server, allowing you to generate LinkedIn posts through an interactive, agent-driven workflow.

For development and debugging, you can also launch the Google ADK developer UI with:

```bash
adk web
```


## ❕ Example Workflow

Here’s what you can expect from the interaction:
1. Manager agent asks: **"What is the intention of your post?"**
2. You provide a topic and optional details.
3. **Story Agent** generates an engaging backstory.
4. **Hashtag Agent** suggests relevant hashtags.
5. **Post Agent** crafts the complete LinkedIn post.
6. Optionally, **Image Agent** can create a relevant image for your post.
7. The final post (and image) are presented to you for review.


## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to [open an issue](https://github.com/sujeetgund/linkedin-post-generator-agent/issues) or submit a pull request.


## 📜 License

This project is licensed under the [Apache 2.0 License](LICENSE).


## 🌟 Acknowledgements

- Built with the power of Google Gemini API.
- Orchestrated using Google ADK.
