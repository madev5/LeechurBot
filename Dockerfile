FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# Create virtual environment with system packages enabled to use base image packages
RUN python3 -m venv --system-site-packages mltbenv

# Configure pip for better reliability and use environment variables for network settings
ENV PIP_DEFAULT_TIMEOUT=1000
ENV PIP_RETRIES=10
ENV PIP_TRUSTED_HOST="pypi.org pypi.python.org files.pythonhosted.org"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Upgrade pip
RUN mltbenv/bin/pip install --upgrade pip

# Install requirements with fallback approach
COPY requirements.txt .

# Try installing all packages at once, fallback to individual packages if it fails
RUN mltbenv/bin/pip install --no-cache-dir \
    --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    -r requirements.txt || \
    (mltbenv/bin/pip install --no-cache-dir \
        --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
        pyrogram tgcrypto pymongo==4.14.1 && \
     mltbenv/bin/pip install --no-cache-dir \
        --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
        fastapi uvicorn aiofiles aioqbt && \
     mltbenv/bin/pip install --no-cache-dir \
        --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
        requests httpx psutil pillow lxml && \
     mltbenv/bin/pip install --no-cache-dir \
        --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
        yt-dlp || true)

# Copy application code
COPY . .

CMD ["bash", "start.sh"]
