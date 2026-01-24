## Docker Guide for GEO Pulse

This file summarizes the commands to run the project using Docker (backend + frontend in a single container).

### Understanding Docker: Build vs Run

**Why two separate commands?**

Think of it like compiling a program:
- **`docker build`** = **Compile** the code into an image (like building an executable). You do this **once** (or when you change code).
- **`docker run`** = **Launch** a container from that image (like running the executable). You can do this **many times** from the same image.



### 1. Prerequisites

- **Docker installed** (that's it! No need for any other dependencies)
- Your **own** API keys:
  - `OPENAI_API_KEY`
  - `TAVILY_API_KEY`

**Note:** Docker handles everything for you - Python, dependencies (`uv`), and all tools are included in the image. You just need Docker and your API keys!

### 2. Prepare the `.env` file

From the provided template:

```bash
cp .env.example .env
```

Then edit `.env` to add **your** keys:

```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```


### 3. Build the Docker image

From the project root:

```bash
docker build -t geo-pulse .
```

**What this does:**
- `docker build`: Builds an image from the `Dockerfile`
- `-t geo-pulse`: Tags the image with the name `geo-pulse` (so you can reference it later)
- `.`: The build context is the current directory (where your code, Dockerfile, etc. are)


### 4. Run the container (backend + frontend)

**Simple version (recommended):**

```bash
docker run -p 8000:8000 -p 8501:8501 --env-file .env geo-pulse
```

**What each part does:**
- `docker run`: Creates and starts a new container
- `-p 8000:8000`: Maps port 8000 from container → port 8000 on your machine (FastAPI backend)
- `-p 8501:8501`: Maps port 8501 from container → port 8501 on your machine (Streamlit frontend)
- `--env-file .env`: Loads environment variables (your API keys) from your `.env` file
- `geo-pulse`: The name of the image to use (the one you built in step 3)

**This step:**
- Starts the FastAPI backend on port 8000
- Starts the Streamlit frontend on port 8501
- Takes ~5-10 seconds

**Advanced version (with container name, runs in background):**

```bash
docker run -d -p 8000:8000 -p 8501:8501 --name geo-pulse-container --env-file .env geo-pulse
```

### 5. Access the application

Once the container is running:

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/api/health

### 6. Useful Docker commands

```bash
# List running containers
docker ps

# View logs
docker logs geo-pulse-container
docker logs -f geo-pulse-container  # follow logs in real-time

# Stop the container
docker stop geo-pulse-container

# Start a stopped container
docker start geo-pulse-container

# Remove the container (after stopping it)
docker rm -f geo-pulse-container

# List all images (including geo-pulse)
docker images

# Remove the image (if you want to rebuild from scratch)
docker rmi geo-pulse
```

### Quick reference: Full workflow

```bash
# 1. Prepare environment
cp .env.example .env
# Edit .env with your API keys

# 2. Build the image (once, or when code changes)
docker build -t geo-pulse .

# 3. Run the container (every time you want to use it)
docker run -p 8000:8000 -p 8501:8501 --name geo-pulse-container --env-file .env geo-pulse

# 4. Access
# Frontend: http://localhost:8501
# API: http://localhost:8000/docs
```
