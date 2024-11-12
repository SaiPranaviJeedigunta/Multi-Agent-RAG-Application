FROM apache/airflow:2.10.3

USER root

# Install Google Cloud SDK
RUN apt-get update && \
    apt-get install -y apt-transport-https ca-certificates gnupg && \
    echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install -y google-cloud-sdk && \
    rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow
