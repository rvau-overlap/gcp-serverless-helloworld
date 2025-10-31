# GCP Serverless Hello World

A simple serverless application deployed to Google Cloud Run that displays "Hello, world!" along with the visitor's user agent and IP address.

## Features

- Displays a greeting message
- Shows the visitor's User Agent
- Shows the visitor's IP address (with proxy support)
- Automatic deployment to Google Cloud Run via GitHub Actions

## Application Structure

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration for Cloud Run
- `.github/workflows/deploy-to-gcp.yml` - GitHub Actions workflow for automatic deployment

## Setup Instructions

### Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GitHub account with this repository
3. `gcloud` CLI installed locally (for initial setup)

### GCP Configuration

#### 1. Create a GCP Project

```bash
# Create a new project (or use an existing one)
gcloud projects create YOUR_PROJECT_ID --name="Hello World App"

# Set the project as default
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Enable Required APIs

```bash
# Enable Cloud Run API
gcloud services enable run.googleapis.com

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Enable IAM Credentials API (for Workload Identity)
gcloud services enable iamcredentials.googleapis.com
```

#### 3. Create Artifact Registry Repository

```bash
# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create helloworld-app \
  --repository-format=docker \
  --location=us-central1 \
  --description="Docker repository for Hello World app"
```

#### 4. Set Up Workload Identity Federation

Workload Identity Federation allows GitHub Actions to authenticate to GCP without using service account keys.

```bash
# Create a Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --project="YOUR_PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create a Workload Identity Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --project="YOUR_PROJECT_ID" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="assertion.repository_owner=='YOUR_GITHUB_USERNAME_OR_ORG'" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

#### 5. Create a Service Account

```bash
# Create a service account for GitHub Actions
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account" \
  --project="YOUR_PROJECT_ID"

# Grant necessary permissions to the service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Allow the Workload Identity Pool to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding \
  github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --project="YOUR_PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/YOUR_GITHUB_USERNAME/gcp-serverless-helloworld"
```

Note: Replace `PROJECT_NUMBER` with your actual GCP project number (not ID). You can find it by running:
```bash
gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"
```

### GitHub Repository Configuration

#### Required Secrets

Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. **GCP_PROJECT_ID**
   - Your GCP project ID
   - Example: `my-project-12345`

2. **GCP_WORKLOAD_IDENTITY_PROVIDER**
   - Format: `projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider`
   - Get it by running:
     ```bash
     gcloud iam workload-identity-pools providers describe github-provider \
       --project="YOUR_PROJECT_ID" \
       --location="global" \
       --workload-identity-pool="github-pool" \
       --format="value(name)"
     ```

3. **GCP_SERVICE_ACCOUNT**
   - Your service account email
   - Format: `github-actions-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com`

### Deployment

Once configured, the application will automatically deploy to Google Cloud Run whenever you push to the `main` branch.

```bash
# Push to main branch to trigger deployment
git push origin main
```

The deployment workflow will:
1. Build a Docker image
2. Push it to Google Artifact Registry
3. Deploy to Cloud Run
4. Display the service URL in the workflow logs

### Local Development

To run the application locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:8080`

### Local Docker Testing

To test the Docker container locally:

```bash
# Build the image
docker build -t helloworld-app .

# Run the container
docker run -p 8080:8080 helloworld-app

# Access the app at http://localhost:8080
```

## Customization

### Change the Region

Edit the `REGION` environment variable in `.github/workflows/deploy-to-gcp.yml`:

```yaml
env:
  REGION: us-central1  # Change to your preferred region
```

Don't forget to create your Artifact Registry repository in the same region.

### Change the Service Name

Edit the `SERVICE_NAME` environment variable in `.github/workflows/deploy-to-gcp.yml`:

```yaml
env:
  SERVICE_NAME: helloworld-app  # Change to your preferred name
```

Also update the Artifact Registry repository name accordingly.

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:
- Verify all secrets are correctly set in GitHub
- Ensure the Workload Identity Pool is properly configured
- Check that the service account has the necessary permissions

### Deployment Failures

If deployment fails:
- Check the GitHub Actions logs for detailed error messages
- Verify that all required GCP APIs are enabled
- Ensure the Artifact Registry repository exists in the correct region

### Application Issues

If the app doesn't work as expected:
- Check Cloud Run logs: `gcloud run logs read helloworld-app --region=us-central1`
- Verify the service is publicly accessible (--allow-unauthenticated)

## Security Considerations

- The application is deployed with `--allow-unauthenticated` flag, making it publicly accessible
- IP addresses are captured from `X-Forwarded-For` header (set by Cloud Run)
- For production use, consider implementing authentication and rate limiting

## License

This project is provided as-is for educational purposes.