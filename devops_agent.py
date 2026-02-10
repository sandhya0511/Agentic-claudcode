"""
DevOps Agent

Purpose: Handles deployment, CI/CD, and infrastructure automation
Capabilities:
- Generates CI/CD pipelines
- Creates Docker configurations
- Generates Kubernetes manifests
- Creates infrastructure as code
- Sets up monitoring and logging
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import json


class DevOpsAgent(BaseAgent):
    """
    Agent responsible for DevOps automation.
    
    Input:
        - architecture: System architecture
        - cloud_provider: AWS, Azure, GCP, or on-premise
        - deployment_type: docker, kubernetes, serverless, vm
        - ci_cd_platform: GitHub Actions, GitLab CI, Jenkins, etc.
        
    Output:
        - ci_cd_config: CI/CD pipeline configuration
        - docker_files: Dockerfile and docker-compose
        - kubernetes_manifests: K8s deployment files
        - infrastructure_code: Terraform/CloudFormation
        - monitoring_config: Monitoring setup
    """
    
    def __init__(self, agent_id: str = "devops_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="DevOps"
        )
        
        # Supported platforms
        self.cloud_providers = ["aws", "azure", "gcp", "digitalocean", "on-premise"]
        self.ci_cd_platforms = [
            "github-actions",
            "gitlab-ci",
            "jenkins",
            "circleci",
            "azure-devops",
            "bitbucket-pipelines"
        ]
        self.deployment_types = [
            "docker",
            "kubernetes",
            "serverless",
            "vm",
            "container"
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are an expert DevOps Agent specializing in deployment automation and infrastructure.

Your role is to:
1. Design and implement CI/CD pipelines
2. Create containerization configurations
3. Generate Kubernetes manifests
4. Write infrastructure as code
5. Set up monitoring and logging
6. Implement security best practices
7. Optimize for cost and performance

DevOps Principles:
- Infrastructure as Code (IaC)
- Continuous Integration/Continuous Deployment
- Automated testing in pipeline
- Immutable infrastructure
- Security from the start
- Observability (logging, monitoring, tracing)
- Disaster recovery planning
- Cost optimization

CI/CD Pipeline Components:
1. Source Control Integration
2. Build Stage
   - Dependency installation
   - Code compilation
   - Asset building
3. Test Stage
   - Unit tests
   - Integration tests
   - Security scans
   - Code quality checks
4. Build Artifacts
   - Docker images
   - Compiled binaries
   - Static assets
5. Deployment Stages
   - Development
   - Staging
   - Production
6. Post-Deployment
   - Health checks
   - Smoke tests
   - Notifications

Docker Best Practices:
- Multi-stage builds
- Small base images (alpine when possible)
- Layer caching optimization
- Security scanning
- Non-root user
- .dockerignore file
- Health checks
- Resource limits

Kubernetes Best Practices:
- Resource requests and limits
- Health probes (liveness, readiness)
- ConfigMaps and Secrets
- Rolling updates
- Horizontal Pod Autoscaling
- Network policies
- RBAC permissions
- Pod Security Policies

Security Considerations:
- Secret management
- Image scanning
- Least privilege access
- Network segmentation
- Encrypted communications
- Audit logging
- Compliance requirements

Monitoring and Logging:
- Application metrics
- Infrastructure metrics
- Centralized logging
- Distributed tracing
- Alerting rules
- Dashboards
- Log retention policies

Output Format:
Provide as JSON with:
- ci_cd_config: Pipeline configuration files
- docker_files: {Dockerfile, docker-compose.yml, .dockerignore}
- kubernetes_manifests: K8s YAML files
- infrastructure_code: Terraform/CloudFormation
- monitoring_config: Prometheus, Grafana, ELK configs
- secrets_management: How to handle secrets
- deployment_guide: Step-by-step deployment instructions
- rollback_procedure: How to rollback deployments

Generate production-ready DevOps configurations."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate DevOps configurations.
        
        Args:
            input_data: Dictionary containing:
                - architecture: System architecture
                - cloud_provider: Cloud platform
                - deployment_type: Deployment method
                - ci_cd_platform: CI/CD platform
                - project_name: Project name
                
        Returns:
            DevOps configurations
        """
        # Validate input
        architecture = input_data.get("architecture", {})
        cloud_provider = input_data.get("cloud_provider", "aws").lower()
        deployment_type = input_data.get("deployment_type", "docker").lower()
        ci_cd_platform = input_data.get("ci_cd_platform", "github-actions").lower()
        project_name = input_data.get("project_name", "project")
        language = input_data.get("language", "python")
        
        # Build the DevOps configuration prompt
        user_message = self._build_devops_prompt(
            architecture,
            cloud_provider,
            deployment_type,
            ci_cd_platform,
            project_name,
            language
        )
        
        # Update state
        self.update_state(
            current_task="Generating DevOps configurations",
            progress=0.3
        )
        
        # Invoke Claude for DevOps configuration
        self.logger.info(f"Generating DevOps configs for {deployment_type} on {cloud_provider}")
        response = await self.invoke_claude(user_message, max_tokens=8000)
        
        # Parse and structure the response
        self.update_state(
            current_task="Structuring DevOps configurations",
            progress=0.7
        )
        
        devops_result = self._parse_devops_response(response)
        
        # Add best practices checklist
        self.update_state(
            current_task="Adding best practices",
            progress=0.9
        )
        
        devops_result["best_practices_checklist"] = self._generate_best_practices_checklist(
            deployment_type,
            cloud_provider
        )
        
        # Add metadata
        devops_result["metadata"] = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "cloud_provider": cloud_provider,
            "deployment_type": deployment_type,
            "ci_cd_platform": ci_cd_platform,
            "generation_timestamp": self.state.started_at.isoformat()
        }
        
        self.logger.info("DevOps configuration completed")
        
        return devops_result
    
    def _build_devops_prompt(
        self,
        architecture: Dict[str, Any],
        cloud_provider: str,
        deployment_type: str,
        ci_cd_platform: str,
        project_name: str,
        language: str
    ) -> str:
        """Build the prompt for DevOps configuration"""
        
        prompt = f"""Generate comprehensive DevOps configurations for {project_name}.

PROJECT: {project_name}
LANGUAGE: {language}
CLOUD PROVIDER: {cloud_provider}
DEPLOYMENT TYPE: {deployment_type}
CI/CD PLATFORM: {ci_cd_platform}
"""
        
        if architecture:
            prompt += f"""
ARCHITECTURE:
{json.dumps(architecture, indent=2)[:2000]}
"""
        
        prompt += f"""
Please generate the following DevOps configurations:

1. CI/CD PIPELINE ({ci_cd_platform})
   - Pipeline file (e.g., .github/workflows/main.yml)
   - Build stage
   - Test stage
   - Security scanning
   - Artifact creation
   - Deployment stages (dev, staging, prod)
   - Environment variables and secrets
   - Notifications
   - Rollback capability

2. DOCKER CONFIGURATION
   - Dockerfile (multi-stage build)
   - docker-compose.yml (for local development)
   - .dockerignore
   - Health check configuration
   - Resource limits
   - Security best practices

"""
        
        if deployment_type == "kubernetes":
            prompt += """
3. KUBERNETES MANIFESTS
   - Deployment
   - Service
   - Ingress
   - ConfigMap
   - Secret (template)
   - HorizontalPodAutoscaler
   - PersistentVolumeClaim (if needed)
   - Network Policy
   - ServiceAccount and RBAC

"""
        
        prompt += f"""
4. INFRASTRUCTURE AS CODE ({cloud_provider})
   - Main infrastructure file
   - Network configuration
   - Security groups/firewall rules
   - Load balancer configuration
   - Database setup (if applicable)
   - Storage configuration
   - DNS configuration
   - Variables file
   - Outputs file

5. MONITORING AND LOGGING
   - Application metrics collection
   - Infrastructure monitoring
   - Log aggregation setup
   - Alerting rules
   - Dashboard configurations
   - Health check endpoints

6. SECRETS MANAGEMENT
   - How to store secrets
   - Environment-specific configurations
   - Secret rotation strategy
   - Access control

7. DEPLOYMENT GUIDE
   - Prerequisites
   - Initial setup steps
   - Environment configuration
   - Deployment commands
   - Verification steps
   - Common issues and solutions

8. ROLLBACK PROCEDURE
   - How to rollback a deployment
   - Database rollback considerations
   - Monitoring during rollback
   - Communication plan

IMPORTANT:
- Follow {cloud_provider} best practices
- Include security configurations
- Set up proper resource limits
- Enable monitoring and logging
- Make configurations production-ready
- Include disaster recovery considerations
- Optimize for cost

Provide output as JSON with keys: ci_cd_config, docker_files, 
kubernetes_manifests (if applicable), infrastructure_code, monitoring_config, 
secrets_management, deployment_guide, rollback_procedure"""
        
        return prompt
    
    def _parse_devops_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's DevOps response"""
        
        try:
            # Extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            parsed = json.loads(json_str)
            
            result = {
                "ci_cd_config": parsed.get("ci_cd_config", {}),
                "docker_files": parsed.get("docker_files", {}),
                "kubernetes_manifests": parsed.get("kubernetes_manifests", {}),
                "infrastructure_code": parsed.get("infrastructure_code", {}),
                "monitoring_config": parsed.get("monitoring_config", {}),
                "secrets_management": parsed.get("secrets_management", ""),
                "deployment_guide": parsed.get("deployment_guide", ""),
                "rollback_procedure": parsed.get("rollback_procedure", ""),
                "raw_response": response
            }
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            return {
                "ci_cd_config": {},
                "docker_files": {},
                "kubernetes_manifests": {},
                "infrastructure_code": {},
                "monitoring_config": {},
                "secrets_management": "",
                "deployment_guide": "",
                "rollback_procedure": "",
                "raw_response": response,
                "parse_error": str(e)
            }
    
    def _generate_best_practices_checklist(
        self,
        deployment_type: str,
        cloud_provider: str
    ) -> List[Dict[str, str]]:
        """Generate a best practices checklist"""
        
        checklist = [
            {
                "category": "Security",
                "items": [
                    "Secrets stored in secure vault",
                    "Container images scanned for vulnerabilities",
                    "Least privilege access configured",
                    "Network policies defined",
                    "SSL/TLS enabled",
                    "Security headers configured"
                ]
            },
            {
                "category": "Reliability",
                "items": [
                    "Health checks configured",
                    "Auto-scaling enabled",
                    "Backup strategy defined",
                    "Disaster recovery plan",
                    "Multi-AZ deployment",
                    "Graceful shutdown handling"
                ]
            },
            {
                "category": "Observability",
                "items": [
                    "Application metrics collected",
                    "Centralized logging configured",
                    "Alerting rules defined",
                    "Distributed tracing enabled",
                    "Dashboards created",
                    "SLOs/SLIs defined"
                ]
            },
            {
                "category": "Performance",
                "items": [
                    "Resource limits set",
                    "Caching strategy implemented",
                    "CDN configured",
                    "Database optimized",
                    "Load testing performed",
                    "Performance monitoring active"
                ]
            },
            {
                "category": "Cost Optimization",
                "items": [
                    "Right-sized instances",
                    "Auto-scaling configured",
                    "Spot instances used (where applicable)",
                    "Unused resources identified",
                    "Cost monitoring enabled",
                    "Reserved instances considered"
                ]
            }
        ]
        
        return checklist
    
    async def generate_disaster_recovery_plan(
        self,
        architecture: Dict[str, Any],
        cloud_provider: str
    ) -> Dict[str, Any]:
        """
        Generate a disaster recovery plan.
        
        Args:
            architecture: System architecture
            cloud_provider: Cloud platform
            
        Returns:
            Disaster recovery plan
        """
        
        self.logger.info("Generating disaster recovery plan")
        
        user_message = f"""Create a comprehensive disaster recovery plan for:

CLOUD PROVIDER: {cloud_provider}
ARCHITECTURE: {json.dumps(architecture, indent=2)}

Include:
1. RTO and RPO targets
2. Backup strategy
3. Failover procedures
4. Data recovery procedures
5. Testing procedures
6. Communication plan
7. Roles and responsibilities

Format as JSON with keys: rto_rpo, backup_strategy, failover_procedures, 
data_recovery, testing_plan, communication_plan, roles"""
        
        response = await self.invoke_claude(user_message)
        
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            result = json.loads(json_str)
            return result
            
        except json.JSONDecodeError:
            return {"raw_response": response}
