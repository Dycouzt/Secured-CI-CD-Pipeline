# DevSecOps: Secure CI/CD Pipeline Project

This project demonstrates a production-grade, 11-stage secure CI/CD pipeline using GitHub Actions. It is built around a sample Python Flask application with intentional vulnerabilities to showcase how various security tools can be integrated into a DevOps workflow to "shift security left."

The pipeline automatically scans code, dependencies, secrets, and container images, failing the build if high-severity vulnerabilities are detected. This acts as a security gate, preventing insecure code from being merged or deployed.

## Project Goals

-   **Automate Security:** Integrate security scanning directly into the CI/CD workflow.
-   **Shift Left:** Detect and remediate vulnerabilities early in the development process.
-   **Break the Build:** Enforce security policies by automatically failing builds that contain critical vulnerabilities.
-   **Auditability:** Generate and store reports from all security scans for compliance and review.

## 🛠️ Tools Used

| Tool      | Category                       | Purpose                                                              |
| :-------- | :----------------------------- | :------------------------------------------------------------------- |
| **Bandit**  | SAST (Static Analysis)         | Scans Python code for common security issues (e.g., SQL injection).  |
| **Snyk**    | SCA (Dependency Scanning)      | Finds and fixes vulnerabilities in open-source dependencies.         |
| **Gitleaks**| Secret Detection               | Scans Git history for hardcoded secrets like API keys and passwords. |
| **Trivy**   | Container Image Scanning       | Scans container images for OS and application-level vulnerabilities. |
| **Docker**  | Containerization               | Packages the application and its dependencies into a container image.|
| **GitHub Actions** | CI/CD Orchestration   | Automates the entire build, test, scan, and deploy workflow.         |
| **actions/checkout** | Checkout Code | `08eba0b27e820071cde6df949e0beb9ba4906955` |
| **actions/setup-python** | Setup Python | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| **snyk/actions/python** | Dependency Scanning | `9adf32b1121593767fc3c057af55b55db032dc04` |
| **gitleaks/gitleaks-action** | Secret Detection | `ff98106e4c7b2bc287b24eaf42907196329070c7` |
| **docker/setup-buildx-action** | Docker Buildx Setup | `e468171a9de216ec08956ac3ada2f0791b6bd435` |
| **docker/build-push-action** | Docker Build and Push | `ca052bb54ab0790a636c9b5f226502c73d547a25` |
| **aquasecurity/trivy-action** | Container Scanning | `b6643a29fecd7f34b3597bc6acb0a98b03d33ff8` |
| **actions/upload-artifact** | Upload Artifacts | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| **docker/login-action** | Docker Login | `5e57cd118135c172c3672efd75eb46360885c0ef` |

### Pipeline Diagram

```mermaid
graph TD
    A[Push or Pull Request to 'main'] --> B(Checkout Code);
    B --> C(Set up Python);
    C --> D(Install Dependencies);
    D --> E(Run Unit Tests);
    E --> F{Bandit Scan};
    F --> G{Snyk Scan};
    G --> H{Gitleaks Scan};
    H --> I(Set up Docker Buildx);
    I --> J(Build Docker image);
    J --> K{Trivy Scan};
    K --> L(Upload Reports);
    L --> M(Login to Docker Hub);
    M --> N(Push to Docker Hub);

    subgraph Security Gates (Break Build on Failure)
        F; G; H; K;
    end

    style F fill:#F8D7DA,stroke:#DC3545,stroke-width:2px,color:#333;
    style G fill:#F8D7DA,stroke:#DC3545,stroke-width:2px,color:#333;
    style H fill:#F8D7DA,stroke:#DC3545,stroke-width:2px,color:#333;
    style K fill:#F8D7DA,stroke:#DC3545,stroke-width:2px,color:#333;
```

## 🔧 How to Run

### 1. Prerequisites

-   A GitHub account.
-   A Docker Hub account.
-   A Snyk account.

### 2. Fork and Clone the Repository

Fork this repository to your own GitHub account and then clone it locally:

```bash
git clone https://github.com/YOUR_USERNAME/ci-cd-secured-pipeline.git
cd ci-cd-secured-pipeline
```

### 3. Configure GitHub Secrets

In your forked repository, go to `Settings > Secrets and variables > Actions` and add the following repository secrets:

-   `DOCKERHUB_USERNAME`: Your Docker Hub username.
-   `DOCKERHUB_TOKEN`: A Docker Hub access token with `read`, `write`, and `delete` permissions.
-   `SNYK_TOKEN`: Your Snyk API token, found in your Snyk account settings.

### 4. Trigger the Pipeline

The pipeline will automatically trigger when you:
1.  **Push a commit** to the `main` branch.
2.  **Create a Pull Request** targeting the `main` branch.

The pipeline is designed to **fail** because of the intentional vulnerabilities in the code. This is the expected behavior.

### 5. Running Scans Locally

You can run the same security tools locally to get faster feedback.

```bash
# Install dependencies
pip install bandit snyk gitleaks trivy

# Run Bandit (SAST)
bandit -c security-tools/bandit-config.yml -r app/

# Run Snyk (SCA) - Requires `snyk auth` first
snyk test --file=app/requirements.txt

# Run Gitleaks (Secret Scanning)
gitleaks detect --source . -v

# Build and Scan Docker Image with Trivy
docker build -t my-secure-app:latest .
trivy image my-secure-app:latest
```

## Reading the Results

After a pipeline run, you can find all security reports in the "Actions" tab of your repository. Select the failed run and look for an artifact named `security-reports`. Download and unzip this file to view the JSON reports from Bandit, Snyk, Gitleaks, and Trivy.

-   **`bandit-report.json`**: Shows code-level issues like the SQL injection and hardcoded key.
-   **`snyk-report.json`**: Lists vulnerable dependencies from `requirements.txt`.
-   **`gitleaks-report.json`**: Pinpoints the exact commit and line where a secret was found.
-   **`trivy-report.json`**: Details vulnerabilities in the base image's OS packages and application dependencies.

## Learning Outcomes

By analyzing this project, you will understand:
-   The practical implementation of "shift left" security.
-   How to create a security-gated CI/CD pipeline that enforces quality.
-   The role and function of SAST, SCA, secret scanning, and container scanning tools.
-   How to configure security tools to fail a build based on vulnerability severity.
-   Best practices for writing a secure, multi-stage `Dockerfile`.

## Author

Dycouzt - Diego Acosta