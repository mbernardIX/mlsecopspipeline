pipeline {
    agent any
    parameters {
        string(name: 'MODEL_FILE_PATH', defaultValue: 'simple-cifar10.h5', description: 'Path to the model file (e.g., simple-cifar10.h5)')
        string(name: 'MODEL_NAME', defaultValue: 'simple-cifar10', description: 'Name of the model for MLflow registration')
    }
    environment {
        MLFLOW_TRACKING_URI = "http://mlflow-server:5000"
    }

    stages {
        stage('AV Scan') {
            steps {
                echo "AV scanning for file at ${params.MODEL_FILE_PATH}"
                sh 'clamscan --infected --remove --recursive /downloads/models/${MODEL_FILE_PATH} || true'
            }
        }
        stage('Model Scan') {
            steps {
                echo "Scanning model ${params.MODEL_FILE_PATH} with ModelScan"
                sh '. /app/venv/bin/activate && modelscan -p /downloads/models/${MODEL_FILE_PATH} || true'
            }
        }
        stage('Register Model in MLflow') {
            steps {
                script {
                    def jobIdentifier = "${env.JOB_NAME}-${env.BUILD_ID}"
                    sh """
                        #!/bin/bash
                        . /app/venv/bin/activate
                        python /scripts/register_external_model.py \
                            --tracking-uri "\${MLFLOW_TRACKING_URI}" \
                            --model-file "/downloads/models/\${MODEL_FILE_PATH}" \
                            --model-name "\${MODEL_NAME}" \
                            --run "\${jobIdentifier}"
                    """
                }
            }
        }
    }
}