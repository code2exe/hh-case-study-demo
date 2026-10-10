terraform {
  backend "s3" {
    bucket       = "<STATE_BUCKET_NAME>"
    key          = "<STATE_KEY>"
    region       = "<REGION>"
    encrypt      = true
    use_lockfile = true
  }
}
