FROM jenkins/jenkins:lts

USER root

# Update and install necessary packages
RUN apt-get update && apt-get install -y \
    python3-venv \
    wget \
    apt-transport-https \
    gnupg \
    lsb-release \
    clamav \
    clamav-daemon

# Create directory for clamav-daemon
RUN mkdir -p /var/run/clamav && chown jenkins:jenkins /var/run/clamav

# Freshen ClamAV's database during build (optional, for initial setup)
RUN freshclam

# Create a virtual environment
RUN python3 -m venv /app/venv
RUN . /app/venv/bin/activate && pip install modelscan mlflow adversarial-robustness-toolbox bandit scikit-learn

# Install Trivy
RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | apt-key add -
RUN echo deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main | tee -a /etc/apt/sources.list.d/trivy.list
RUN apt-get update && apt-get install -y trivy

# Install Jenkins plugins
COPY plugins.txt /usr/share/jenkins/plugins.txt
#RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/plugins.txt

# Setting up the environment for Python and security tools
RUN . /app/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install modelscan h5py tensorflow torch dill joblib mlflow adversarial-robustness-toolbox bandit

# Copy the job creation Groovy script and Jenkinsfile
COPY pipelines/validate-model-pipeline.groovy /usr/share/jenkins/ref/jobs/ModelPipelineJob/validate-model-pipeline.groovy

# Ensure Jenkins owns all copied files
RUN chown -R jenkins:jenkins /usr/share/jenkins/ref

# Copy your Python scripts into the image
COPY scripts /app/scripts
RUN chown -R jenkins:jenkins /app/scripts

# Start clamav-daemon and Jenkins
CMD service clamav-daemon start && /usr/local/bin/jenkins.sh

USER jenkins