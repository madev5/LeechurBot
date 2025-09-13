FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# Create virtual environment
RUN python3 -m venv mltbenv

# Configure pip for better reliability
RUN mltbenv/bin/pip install --upgrade pip

# Install requirements with optimized settings
COPY requirements.txt .
RUN mltbenv/bin/pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    --timeout=1000 \
    --retries=3 \
    --disable-pip-version-check \
    -r requirements.txt

# Copy application code
COPY . .

CMD ["bash", "start.sh"]
