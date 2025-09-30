import os
import argparse
import mlflow
import datetime
import hashlib

# Отключаем GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

def timestamped_string(string):
    print(string)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return f"{string}-{timestamp}"

def create_sha256(file_path):
    """Вычисляет SHA256 хэш файла."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def register_model(tracking_uri, model_file, model_name, description="", source="", dataset_name="", dataset_version="", run="Jenkins Pipeline"):
    mlflow.set_tracking_uri(tracking_uri)

    # Если model_name не указан, используем имя файла без расширения
    if not model_name:
        model_name = os.path.splitext(os.path.basename(model_file))[0]

    # Вычисляем хэш модели
    model_hash = create_sha256(model_file)
    pipeline = timestamped_string(run)

    with mlflow.start_run(run_name=pipeline) as run:
        # Теги для эксперимента и модели
        tags = {
            "av scanned": "True",
            "model Scanned": "True",
            "mlflow.runName": pipeline,
            "hash": model_hash,
            "stage": "evaluation",
            "registered by": pipeline
        }

        # Устанавливаем теги для run
        for key, value in tags.items():
            mlflow.set_tag(key, value)
            print(f"Tag '{key}' set to '{value}'.")

        # Регистрируем модель в MLflow
        # Предполагаем, что модель в формате pickle (например, sklearn)
        mlflow.sklearn.log_model(
            sk_model=model_file,  # Путь к файлу будет артефактом
            artifact_path="model",
            registered_model_name=model_name
        )

        # Логируем дополнительные параметры
        mlflow.log_param("model_source", source or "unknown")
        mlflow.log_param("dataset_name", dataset_name or "unknown")
        mlflow.log_param("dataset_version", dataset_version or "unknown")
        mlflow.log_param("description", description or "none")

        # Логируем файл модели как артефакт
        mlflow.log_artifact(model_file, artifact_path="model_files")

        print(f"Model '{model_name}' registered in MLflow Model Registry with run {run.info.run_id}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Register a model with MLflow and log additional experiment attributes.')
    parser.add_argument('--tracking-uri', required=True, help='The MLflow tracking URI.')
    parser.add_argument('--model-file', required=True, help='The file path of the model to register.')
    parser.add_argument('--run', required=False, default='Jenkins Pipeline', help='The name of the pipeline.')
    parser.add_argument('--source', required=False, default='', help='The source of the model.')
    parser.add_argument('--dataset-name', required=False, default='', help='The name of the dataset used.')
    parser.add_argument('--dataset-version', required=False, default='', help='The version of the dataset used.')
    parser.add_argument('--model-name', required=False, default='', help='The name to register the model as in the MLflow Model Registry.')
    args = parser.parse_args()
    print("Arguments:", args)
    register_model(
        args.tracking_uri,
        args.model_file,
        args.model_name,
        run=args.run,
        source=args.source,
        dataset_name=args.dataset_name,
        dataset_version=args.dataset_version)