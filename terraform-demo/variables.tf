variable "credentials" {
  description = "Path to the GCP credentials JSON file"
  default     = file("./keys/mycred.json")
  
}

variable "project" {
  description = "Project"
  default     = "my-gcp-project-id"
}

variable "region" {
  description = "Region"
  default = "us-central1"
}

variable "location" {
  description = "Project Location"
  default = "US"
}

variable "bq_dataset_name" {
  description = "Name of the BigQuery dataset to create"
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
    description = "Name of the Google Cloud Storage bucket to create"
    default     = "terra-bucket-id-terra-bucket"
  
}

variable "gcs_storage_class" {
  description = "Storage class for the Google Cloud Storage bucket"
  default     = "STANDARD"
}
