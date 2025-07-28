FROM ollama/ollama:latest

# Pull model
RUN ollama serve & \
    sleep 3 && \
    ollama pull llama3.2:1b

# Install required packages
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

# Create Python virtual environment and install backend dependencies
RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip install --upgrade pip \
    && pip install \
        websockets \
        langchain-ollama \
        ollama \
        langchain

# Make venv the default Python
ENV PATH="/venv/bin:$PATH"

# Copy chatbot-ui frontend code
COPY src/chatbot-ui/ /app/chatbot-ui/
WORKDIR /app/chatbot-ui

# Install frontend dependencies
RUN npm install

# Expose frontend port
EXPOSE 8501

# Copy Supervisor config
COPY src/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Override the Ollama default entrypoint
ENTRYPOINT []

# Run all services via Supervisor
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
