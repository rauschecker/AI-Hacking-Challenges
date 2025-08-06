FROM ollama/ollama:latest

# Pull model
RUN ollama serve & \
    sleep 3 && \
    ollama pull llama3.2:3b

# Install required packages: git, python3, pip, curl, nodejs, npm, supervisor
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Create a virtual environment and install Python dependencies inside it
RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip install --upgrade pip \
    && pip install \
        "packaging<25,>=23.2" \
        torch==2.2.2+cpu -f https://download.pytorch.org/whl/torch_stable.html \
        transformers==4.37.2 \
        langchain==0.2.17 \
        langchain-ollama==0.1.0 \
        langchain-community \
        ollama \
        websockets==10.4 \
        sqlalchemy==2.0.41 \
        networkx==2.8.8

# Make the venv the default Python environment
ENV PATH="/venv/bin:$PATH"

# Copy frontend app
COPY src/chatbot-ui/ /app/chatbot-ui/
WORKDIR /app/chatbot-ui

# Install Node.js frontend dependencies
RUN npm install

# Expose frontend port
EXPOSE 8501

# Copy supervisord configuration
COPY src/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Override Ollama entrypoint
ENTRYPOINT []

# Launch everything with supervisord
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
