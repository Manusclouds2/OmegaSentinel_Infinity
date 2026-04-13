# OMEGA-SOVEREIGN UNIVERSAL DOCKER CORE
# Optimized for Multi-Architecture (x86_64, ARM64, IoT)

FROM python:3.11-slim-bookworm

# Set system environment
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OMEGA_MODE SOVEREIGN
ENV DEBIAN_FRONTEND noninteractive

# Install system dependencies for elite protocols and network monitoring
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpcap-dev \
    curl \
    iproute2 \
    iptables \
    tor \
    obfs4proxy \
    && rm -rf /var/lib/apt/lists/*

# Establish working dimension
WORKDIR /app

# Install terrestrial requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy elite logic and multiversal assets
COPY . .

# Expose ports: 8000 (API), 9050 (Tor SOCKS), 8888 (Universal Proxy)
EXPOSE 8000 9050 8888

# Healthcheck for SaaS reliability
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/status || exit 1

# Initiate Sovereign Core
CMD ["python", "bootstrap_omega.py"]
