# GIFgen 🖼️✨

**Transform natural language prompts, style choices, and optional initial images into animated GIFs using the power of the Wan 2.1 and AI-driven prompt enhancement.**

GIFgen offers a pipeline to generate unique GIFs by interpreting your creative ideas. It enhances your input prompts, allows for artistic style selection, and can optionally use an uploaded image as a starting point for the animation.

---

## Table of Contents

* [Features](#features)
* [How It Works](#how-it-works)
* [Tech Stack](#tech-stack)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Configuration](#configuration)
    * [Running the Frontend](#running-the-frontend)
    * [Running the Backend Server](#running-the-backend-server)
* [Usage](#usage)


---


## Features

* 💬 **Natural Language to Optimized Prompt Conversion:** Utilizes OpenAI API to refine user input into more effective prompts for the generation model.
* 🎨 **Easy-to-Use Style Changer:** Allows users to select different visual styles to apply to their generated GIFs.
* 🖼️ **Optional Image Upload:** Users can upload an image to serve as the initial frame or a strong thematic guide for the GIF.
* 🤖 **AI-Powered GIF Generation:** Employs the "Wan2.1 model" (please specify more details if possible, e.g., "a Latent Diffusion Model specialized for...", or "based on...") for the core image-to-GIF pipeline.
* 🛠️ **Separated Frontend and Backend:** Ensures a modular design with a user-friendly interface and a powerful processing backend.

---

## How It Works

1.  **User Input:** The user provides a natural language description of the desired GIF, selects a style, and optionally uploads a starting image via the frontend.
2.  **Prompt Enhancement:** The frontend sends the natural language prompt to the backend Flask server. The server (if an OpenAI API key is provided) uses the OpenAI API to enhance and optimize this prompt.
3.  **GIF Generation Request:** The (enhanced) prompt, style choice, and optional image are then processed by the backend.
4.  **"Wan2.1 Model" Processing:** The backend utilizes the "Wan2.1 model" to generate the sequence of frames that will form the GIF based on the processed inputs.
5.  **GIF Output:** The resulting GIF is sent back to the frontend for the user to view and download.

---

## Tech Stack

* **Frontend:**
    * HTML, CSS, JavaScript
    * NextJS, TailwindCSS
    * NPM for package management
* **Backend:**
    * Python
    * Flask (as the web framework)
* **AI & Machine Learning:**
    * Wan-AI/Wan2.1-I2V-14B-480P
    * OpenAI API (for prompt enhancement)
* **Communication:**
    * HTTP/REST APIs between frontend and backend.

---

## Getting Started

Follow these instructions to set up and run GIFgen on your local machine.

### Prerequisites

* Node.js and npm (for the frontend)
* Python 3.x and pip (for the backend)
* Git (for cloning the repository)
* An OpenAI API Key (optional, for prompt enhancement feature)

### Configuration

1.  **Backend - OpenAI API Key (Optional):**
    * In the `server` directory, create a file named `.env`.
    * Add your OpenAI API key to this file:
        ```env
        OPENAI_API_KEY=your_openai_api_key_here
        ```
    * This enables the natural language to ideal prompt conversion feature.

2.  **Frontend-Backend Communication:**
    * You need to ensure the frontend knows how to reach the backend Flask server.
    * **In `server/app.py`**: Note the `HOST` IP address and `PORT` the Flask app is configured to run on (e.g., `0.0.0.0` or `127.0.0.1`, and a port like `5000`).
    * **In `frontend/src/page.txt`** (or wherever the backend URL is configured, e.g., a `.js` config file or an environment variable for the frontend build): Update the server IP address and port to match the Flask server's configuration.
        *Example: If your Flask server runs on `http://127.0.0.1:5000`, this URL should be configured in your frontend code that makes API calls.*

### Running the Frontend

1.  Navigate to the frontend directory:
    ```bash
    cd gifgen-website/frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    This will typically open the frontend in your default web browser.

### Running the Backend Server

1.  Navigate to the server directory (from the project root):
    ```bash
    cd gifgen-website/server
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Start the Flask server:
    ```bash
    flask run
    ```
    Ensure this server is running and accessible at the IP/port configured for the frontend.

---

## Usage

1.  Ensure both the frontend and backend servers are running and correctly configured to communicate.
2.  Open the frontend application in your web browser (usually `http://localhost:port_specified_by_npm_run_dev`).
3.  Enter a natural language description for the GIF you want to create.
4.  Select your desired artistic style from the available options.
5.  (Optional) Upload an image to be used as a starting point or reference.
6.  Click the "Generate GIF" button (or similar).
7.  Wait for the processing to complete. Your generated GIF will be displayed.
