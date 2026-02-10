# Implementation Guide - Agentic SDLC System

## Complete Step-by-Step Setup and Deployment

This guide provides detailed instructions for implementing the Agentic SDLC system in your organization.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation Steps](#2-installation-steps)
3. [Configuration](#3-configuration)
4. [First Run](#4-first-run)
5. [Integration with Existing Tools](#5-integration)
6. [Production Deployment](#6-production-deployment)
7. [Customization](#7-customization)
8. [Monitoring and Maintenance](#8-monitoring)

---

## 1. Prerequisites

### 1.1 System Requirements

**Hardware:**
- CPU: 2+ cores recommended
- RAM: 4GB minimum, 8GB recommended
- Storage: 10GB free space
- Network: Stable internet connection

**Software:**
- Python 3.8, 3.9, 3.10, or 3.11
- pip (Python package manager)
- git (optional, for version control)

**Accounts:**
- Anthropic API account with API key
- GitHub account (if using GitHub Actions for CI/CD)

### 1.2 Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy and save it securely

**Cost Estimate:**
- Claude Sonnet 4: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- Average workflow: ~50K tokens = $0.15-$0.75 per run
- Monthly estimate (10 workflows/day): $45-$225

---

## 2. Installation Steps

### 2.1 Download the System

```bash
# Option 1: If you have a zip file
unzip agentic-sdlc-system.zip
cd agentic-sdlc-system

# Option 2: If in a git repository
git clone <repository-url>
cd agentic-sdlc-system
```

### 2.2 Create Virtual Environment

**Why:** Isolates dependencies from system Python

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows (Command Prompt):
venv\Scripts\activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

# Verify activation (should show venv path):
which python  # macOS/Linux
where python  # Windows
```

### 2.3 Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Verify installation
python -c "import anthropic; print('Success!')"
```

**Common Issues:**

```bash
# If you get SSL errors:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# If you get permission errors (avoid sudo if possible):
pip install --user -r requirements.txt
```

### 2.4 Verify Installation

```bash
# Create a test script
cat > test_install.py << 'EOF'
import anthropic
import langgraph
import langchain
print("✓ All dependencies installed successfully")
EOF

# Run it
python test_install.py
```

---

## 3. Configuration

### 3.1 Environment Setup

```bash
# Copy the template
cp .env.template .env

# Edit the .env file
# On Windows: notepad .env
# On macOS: open -e .env
# On Linux: nano .env
```

### 3.2 Required Configuration

Edit `.env` and set:

```bash
# REQUIRED: Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# RECOMMENDED: Adjust if needed
CLAUDE_MODEL=claude-sonnet-4-20250514
MAX_TOKENS=8000
TEMPERATURE=0.7

# OPTIONAL: Fine-tuning
LOG_LEVEL=INFO
CONCURRENT_AGENTS=3
AGENT_TIMEOUT_SECONDS=300
```

### 3.3 Advanced Configuration

For production use:

```bash
# Database (optional, for storing results)
DATABASE_URL=postgresql://user:pass@localhost:5432/agentic_sdlc

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0

# Enable/disable specific agents
ENABLE_CODE_GENERATION=true
ENABLE_CODE_REVIEW=true
ENABLE_TESTING=true
ENABLE_DOCUMENTATION=true
ENABLE_DEVOPS=true
```

---

## 4. First Run

### 4.1 Run the Example Workflow

```bash
# Ensure virtual environment is activated
# Run the built-in example
python main.py --example
```

**What Happens:**
1. System validates API key
2. Initializes 7 agents
3. Executes complete SDLC workflow
4. Saves results to `output/` directory

**Expected Output:**
```
================================================================================
AGENTIC SDLC SYSTEM - WORKFLOW EXECUTION
================================================================================

Project: TaskMaster API
Started: 2024-XX-XX XX:XX:XX

=== PHASE 1: Requirements Analysis ===
...
=== PHASE 2: Architecture Design ===
...
[continues through all phases]

================================================================================
WORKFLOW SUMMARY
================================================================================
Requirements Analysis..................... ✓ COMPLETED
Architecture Design....................... ✓ COMPLETED
Code Generation........................... ✓ COMPLETED
Code Review............................... ✓ COMPLETED
Testing................................... ✓ COMPLETED
Documentation............................. ✓ COMPLETED
DevOps Configuration...................... ✓ COMPLETED

✓ Complete results saved to: output/sdlc_results_TIMESTAMP.json
✓ Code files saved to: output/artifacts_TIMESTAMP/code
✓ Test files saved to: output/artifacts_TIMESTAMP/tests
✓ Documentation saved to: output/artifacts_TIMESTAMP/docs
✓ DevOps configurations saved to: output/artifacts_TIMESTAMP/devops
```

### 4.2 Examine the Results

```bash
# Navigate to output directory
cd output/artifacts_<TIMESTAMP>

# View generated code
ls code/
cat code/main.py

# View tests
ls tests/
cat tests/test_main.py

# View documentation
ls docs/
cat docs/README.md

# View DevOps configs
ls devops/
cat devops/Dockerfile
```

---

## 5. Integration with Existing Tools

### 5.1 GitHub Integration

```bash
# Initialize git repository (if not already)
git init
git add .
git commit -m "Initial commit: Agentic SDLC System"

# Create GitHub repository and push
git remote add origin <your-repo-url>
git push -u origin main
```

### 5.2 CI/CD Integration

The system generates CI/CD configs. To use them:

```bash
# Copy generated GitHub Actions workflow
cp output/artifacts_*/devops/.github/workflows/*.yml .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "Add CI/CD pipeline"
git push
```

### 5.3 Jira/Linear Integration

```python
# Create custom integration script
# integration/jira_sync.py

import asyncio
from jira import JIRA
from agents.requirements_agent import RequirementsAgent

async def sync_from_jira(jira_issue_key):
    # Connect to Jira
    jira = JIRA(server='https://your-domain.atlassian.net',
                basic_auth=('email', 'api_token'))
    
    # Get issue
    issue = jira.issue(jira_issue_key)
    
    # Extract requirements
    requirements = f"""
    Title: {issue.fields.summary}
    Description: {issue.fields.description}
    """
    
    # Run requirements agent
    agent = RequirementsAgent()
    result = await agent.execute({
        "business_requirements": requirements
    })
    
    # Post back to Jira as comment
    jira.add_comment(jira_issue_key, 
                    f"Technical Specs: {result}")
    
    return result

# Usage
asyncio.run(sync_from_jira('PROJ-123'))
```

### 5.4 Slack Notifications

```python
# integration/slack_notifier.py

import os
import requests

def notify_slack(message, channel='#dev-team'):
    webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    payload = {
        'channel': channel,
        'text': message,
        'username': 'Agentic SDLC Bot'
    }
    
    requests.post(webhook_url, json=payload)

# Use in main.py
from integration.slack_notifier import notify_slack

# After workflow completion
notify_slack(f"✓ SDLC workflow completed for {project_name}")
```

---

## 6. Production Deployment

### 6.1 Docker Deployment

Create a Dockerfile for the system:

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1

# Run
CMD ["python", "main.py", "--example"]
```

Build and run:

```bash
# Build image
docker build -t agentic-sdlc:latest .

# Run container
docker run -e ANTHROPIC_API_KEY=your_key \
           -v $(pwd)/output:/app/output \
           agentic-sdlc:latest
```

### 6.2 Kubernetes Deployment

Create Kubernetes manifests:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentic-sdlc
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agentic-sdlc
  template:
    metadata:
      labels:
        app: agentic-sdlc
    spec:
      containers:
      - name: agentic-sdlc
        image: agentic-sdlc:latest
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: agentic-secrets
              key: api-key
        volumeMounts:
        - name: output
          mountPath: /app/output
      volumes:
      - name: output
        persistentVolumeClaim:
          claimName: sdlc-output
---
apiVersion: v1
kind: Secret
metadata:
  name: agentic-secrets
type: Opaque
stringData:
  api-key: "your-api-key-here"
```

Deploy:

```bash
kubectl apply -f k8s/deployment.yaml
```

### 6.3 AWS Lambda Deployment

For serverless deployment:

```python
# lambda_handler.py
import json
import asyncio
from main import run_custom_workflow

def lambda_handler(event, context):
    # Extract requirements from event
    requirements = event.get('requirements', '')
    project_context = event.get('context', {})
    
    # Run workflow
    results = asyncio.run(run_custom_workflow(
        requirements,
        project_context
    ))
    
    return {
        'statusCode': 200,
        'body': json.dumps(results, default=str)
    }
```

---

## 7. Customization

### 7.1 Adding a Custom Agent

Create your agent:

```python
# agents/security_agent.py
from typing import Dict, Any
from .base_agent import BaseAgent

class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="security_agent",
            agent_type="Security"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are a security analysis agent.
        Identify security vulnerabilities and provide fixes."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        code = input_data["code_files"]
        
        # Build prompt
        prompt = f"Analyze this code for security issues:\n{code}"
        
        # Invoke Claude
        response = await self.invoke_claude(prompt)
        
        return {
            "security_issues": response,
            "severity": "high"
        }
```

Add to workflow:

```python
# In orchestrator/workflow.py

# Add to __init__
self.security_agent = SecurityAgent()

# Add node
workflow.add_node("security", self._security_node)

# Add edge
workflow.add_edge("code_review", "security")
workflow.add_edge("security", "testing")

# Add node function
async def _security_node(self, state: SDLCState) -> SDLCState:
    result = await self.security_agent.execute({
        "code_files": state["generated_code"]["files"]
    })
    state["security_results"] = result
    return state
```

### 7.2 Customizing Agent Prompts

Modify agent behavior:

```python
# In agents/code_generation_agent.py

def _get_system_prompt(self) -> str:
    # Add your organization's coding standards
    base_prompt = super()._get_system_prompt()
    
    custom_standards = """
    ADDITIONAL REQUIREMENTS:
    - Use our company's logging framework
    - Follow our naming conventions: PascalCase for classes
    - Include type hints for all function parameters
    - Add docstrings in Google format
    """
    
    return base_prompt + custom_standards
```

### 7.3 Adding Language Support

```python
# In agents/code_generation_agent.py

self.language_config = {
    # Add new language
    "kotlin": {
        "style_guide": "Kotlin Coding Conventions",
        "test_framework": "JUnit 5 + MockK",
        "doc_style": "KDoc"
    },
    # ... existing languages
}
```

---

## 8. Monitoring and Maintenance

### 8.1 Logging Configuration

```python
# config/logging_config.py

import logging
import logging.handlers

def setup_production_logging():
    # Rotating file handler
    handler = logging.handlers.RotatingFileHandler(
        'logs/sdlc.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler]
    )
```

### 8.2 Performance Monitoring

```python
# monitoring/metrics.py

import time
import psutil
from dataclasses import dataclass

@dataclass
class WorkflowMetrics:
    start_time: float
    end_time: float
    total_duration: float
    api_calls: int
    tokens_used: int
    memory_used: float
    
def track_workflow(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        start_memory = psutil.virtual_memory().used
        
        result = await func(*args, **kwargs)
        
        end = time.time()
        end_memory = psutil.virtual_memory().used
        
        metrics = WorkflowMetrics(
            start_time=start,
            end_time=end,
            total_duration=end - start,
            memory_used=end_memory - start_memory,
            # ... other metrics
        )
        
        # Log or store metrics
        print(f"Workflow completed in {metrics.total_duration:.2f}s")
        
        return result
    
    return wrapper
```

### 8.3 Health Checks

```python
# health_check.py

import asyncio
from agents.requirements_agent import RequirementsAgent

async def health_check():
    """Verify system is operational"""
    
    try:
        # Test agent initialization
        agent = RequirementsAgent()
        
        # Test API call
        test_input = {
            "business_requirements": "Test requirement"
        }
        
        result = await agent.execute(test_input)
        
        if result:
            print("✓ Health check passed")
            return True
        else:
            print("✗ Health check failed: No result")
            return False
            
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

# Run periodically
if __name__ == "__main__":
    asyncio.run(health_check())
```

### 8.4 Cost Tracking

```python
# monitoring/cost_tracker.py

class CostTracker:
    # Pricing (as of Feb 2025)
    SONNET_INPUT = 0.003  # per 1K tokens
    SONNET_OUTPUT = 0.015  # per 1K tokens
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def track_call(self, input_tokens, output_tokens):
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
    
    def get_cost(self):
        input_cost = (self.total_input_tokens / 1000) * self.SONNET_INPUT
        output_cost = (self.total_output_tokens / 1000) * self.SONNET_OUTPUT
        return input_cost + output_cost
    
    def report(self):
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": self.get_cost()
        }
```

---

## Troubleshooting Common Issues

### Issue: Rate Limiting

**Problem:** Getting rate limit errors from Anthropic API

**Solution:**
```python
# Add retry logic in base_agent.py
import time
from anthropic import RateLimitError

async def invoke_claude(self, user_message, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = self.client.messages.create(...)
            return response.content[0].text
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
```

### Issue: Out of Memory

**Problem:** System runs out of memory on large projects

**Solution:**
```python
# Process files in batches
def chunk_files(files, chunk_size=5):
    items = list(files.items())
    for i in range(0, len(items), chunk_size):
        yield dict(items[i:i+chunk_size])

# In agent processing
for file_batch in chunk_files(all_files):
    result = await process_batch(file_batch)
```

### Issue: Slow Performance

**Problem:** Workflow takes too long

**Solutions:**
1. Enable parallel processing where possible
2. Reduce MAX_TOKENS for simpler tasks
3. Use Claude Haiku for non-critical agents
4. Cache intermediate results

---

## Next Steps

1. ✅ Complete installation and configuration
2. ✅ Run example workflow successfully
3. ✅ Review generated outputs
4. 🔄 Customize for your organization
5. 🔄 Integrate with existing tools
6. 🔄 Deploy to production
7. 🔄 Monitor and optimize

**Congratulations!** You now have a production-ready agentic SDLC system.
