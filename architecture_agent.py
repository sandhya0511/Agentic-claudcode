"""
Architecture Design Agent

Purpose: Designs system architecture based on technical specifications
Capabilities:
- Creates system architecture diagrams (as code/descriptions)
- Recommends technology stack
- Designs database schemas
- Defines API contracts
- Identifies design patterns
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent
import json


class ArchitectureAgent(BaseAgent):
    """
    Agent responsible for system architecture design.
    
    Input:
        - technical_specifications: From Requirements Agent
        - constraints: Technical constraints (budget, timeline, team skills)
        - existing_systems: Information about existing systems to integrate
        
    Output:
        - system_architecture: High-level architecture design
        - technology_stack: Recommended technologies
        - database_schema: Database design
        - api_contracts: API endpoint definitions
        - design_patterns: Recommended design patterns
        - architecture_diagrams: Mermaid/PlantUML diagrams
    """
    
    def __init__(self, agent_id: str = "architecture_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="ArchitectureDesign"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Software Architecture Agent specializing in system design.

Your role is to:
1. Design scalable, maintainable, and robust system architectures
2. Recommend appropriate technology stacks based on requirements
3. Create database schemas optimized for the use case
4. Define clear API contracts and interfaces
5. Apply appropriate design patterns and principles
6. Consider security, performance, and scalability from the start

Architectural Principles to Follow:
- SOLID principles
- Separation of concerns
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple, Stupid)
- Microservices vs Monolith based on scale and team
- Cloud-native design when applicable
- Security by design
- Fail-fast and resilience patterns

Technology Selection Criteria:
- Team expertise and learning curve
- Community support and maturity
- Performance characteristics
- Scalability potential
- Cost considerations
- Integration capabilities
- Long-term maintainability

Output Format:
Provide structured JSON output with:
- system_architecture: Component breakdown and relationships
- technology_stack: Frontend, backend, database, infrastructure recommendations
- database_schema: Tables, relationships, indexes
- api_contracts: RESTful or GraphQL API definitions
- design_patterns: Patterns to apply (MVC, Repository, Factory, etc.)
- architecture_diagrams: Mermaid diagram code for visualization
- scalability_strategy: How the system will scale
- security_design: Security measures and authentication flow
- deployment_architecture: Deployment topology and CI/CD considerations

Be specific, justify your choices, and provide alternatives when relevant."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design system architecture based on specifications.
        
        Args:
            input_data: Dictionary containing:
                - technical_specifications: From requirements agent
                - constraints: Optional constraints (budget, timeline, etc.)
                - existing_systems: Optional existing system info
                
        Returns:
            Complete architecture design
        """
        # Validate input
        self.validate_input(input_data, ["technical_specifications"])
        
        tech_specs = input_data["technical_specifications"]
        constraints = input_data.get("constraints", {})
        existing_systems = input_data.get("existing_systems", [])
        
        # Build the design prompt
        user_message = self._build_design_prompt(
            tech_specs,
            constraints,
            existing_systems
        )
        
        # Update state
        self.update_state(
            current_task="Designing system architecture",
            progress=0.3
        )
        
        # Invoke Claude for architecture design
        self.logger.info("Invoking Claude for architecture design")
        response = await self.invoke_claude(user_message)
        
        # Parse and structure the response
        self.update_state(
            current_task="Structuring architecture design",
            progress=0.7
        )
        
        design_result = self._parse_design_response(response)
        
        # Generate architecture diagrams
        self.update_state(
            current_task="Generating architecture diagrams",
            progress=0.9
        )
        
        if "architecture_diagrams" not in design_result or not design_result["architecture_diagrams"]:
            design_result["architecture_diagrams"] = await self._generate_diagrams(design_result)
        
        # Add metadata
        design_result["metadata"] = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "design_timestamp": self.state.started_at.isoformat()
        }
        
        self.logger.info("Architecture design completed")
        
        return design_result
    
    def _build_design_prompt(
        self,
        tech_specs: Dict[str, Any],
        constraints: Dict[str, Any],
        existing_systems: List[str]
    ) -> str:
        """Build the prompt for architecture design"""
        
        prompt = f"""Design a complete system architecture based on the following technical specifications.

TECHNICAL SPECIFICATIONS:
{json.dumps(tech_specs, indent=2)}
"""
        
        if constraints:
            prompt += f"""

CONSTRAINTS:
{json.dumps(constraints, indent=2)}
"""
        
        if existing_systems:
            prompt += f"""

EXISTING SYSTEMS TO INTEGRATE:
{json.dumps(existing_systems, indent=2)}
"""
        
        prompt += """

Please provide a comprehensive architecture design including:

1. SYSTEM ARCHITECTURE
   - High-level component architecture
   - Component responsibilities and interactions
   - Data flow between components
   - Architecture style (Microservices, Monolith, Serverless, etc.)

2. TECHNOLOGY STACK
   Frontend:
   - Framework/library recommendations
   - State management approach
   - UI component library
   
   Backend:
   - Programming language and framework
   - API design (REST/GraphQL)
   - Authentication/authorization approach
   
   Database:
   - Database type (SQL/NoSQL)
   - Specific database recommendation
   - Caching strategy
   
   Infrastructure:
   - Cloud provider recommendation
   - Container orchestration
   - Message queue/event streaming if needed

3. DATABASE SCHEMA
   - Tables/Collections design
   - Relationships and foreign keys
   - Indexes for performance
   - Data migration strategy

4. API CONTRACTS
   - Endpoint definitions
   - Request/response formats
   - Authentication requirements
   - Rate limiting strategy

5. DESIGN PATTERNS
   - Architectural patterns to apply
   - Design patterns for key components
   - Justification for pattern choices

6. ARCHITECTURE DIAGRAMS (Mermaid syntax)
   - System context diagram
   - Component diagram
   - Database schema diagram
   - Deployment diagram

7. SCALABILITY STRATEGY
   - Horizontal vs vertical scaling approach
   - Bottleneck identification
   - Caching strategy
   - CDN usage

8. SECURITY DESIGN
   - Authentication mechanism
   - Authorization model
   - Data encryption (in transit and at rest)
   - Security best practices

9. DEPLOYMENT ARCHITECTURE
   - Environment strategy (dev, staging, prod)
   - CI/CD pipeline design
   - Monitoring and logging strategy
   - Disaster recovery plan

Provide your response as valid JSON with all these sections."""
        
        return prompt
    
    def _parse_design_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response into structured architecture design"""
        
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
            
            # Ensure all expected fields exist
            result = {
                "system_architecture": parsed.get("system_architecture", {}),
                "technology_stack": parsed.get("technology_stack", {}),
                "database_schema": parsed.get("database_schema", {}),
                "api_contracts": parsed.get("api_contracts", []),
                "design_patterns": parsed.get("design_patterns", []),
                "architecture_diagrams": parsed.get("architecture_diagrams", {}),
                "scalability_strategy": parsed.get("scalability_strategy", {}),
                "security_design": parsed.get("security_design", {}),
                "deployment_architecture": parsed.get("deployment_architecture", {}),
                "raw_design": response
            }
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            return {
                "system_architecture": {},
                "technology_stack": {},
                "database_schema": {},
                "api_contracts": [],
                "design_patterns": [],
                "architecture_diagrams": {},
                "scalability_strategy": {},
                "security_design": {},
                "deployment_architecture": {},
                "raw_design": response,
                "parse_error": str(e)
            }
    
    async def _generate_diagrams(self, design: Dict[str, Any]) -> Dict[str, str]:
        """Generate Mermaid diagrams for the architecture"""
        
        self.logger.info("Generating architecture diagrams")
        
        user_message = f"""Based on the following architecture design, generate Mermaid diagram code 
for the following diagrams:

1. System Context Diagram (C4 model)
2. Component Diagram
3. Database Schema Diagram (ER diagram)
4. Deployment Diagram

ARCHITECTURE DESIGN:
{json.dumps(design, indent=2)}

Provide the output as JSON with keys: system_context, components, database, deployment
Each value should be valid Mermaid diagram code."""
        
        response = await self.invoke_claude(user_message)
        
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            diagrams = json.loads(json_str)
            return diagrams
            
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse diagram JSON, returning raw response")
            return {"diagrams": response}
    
    async def review_architecture(
        self,
        design: Dict[str, Any],
        review_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Review the architecture design against specific criteria.
        
        Args:
            design: The architecture design to review
            review_criteria: List of review criteria (e.g., ["scalability", "security"])
            
        Returns:
            Architecture review results
        """
        
        self.logger.info("Reviewing architecture design")
        
        user_message = f"""Review the following architecture design against these criteria:
{', '.join(review_criteria)}

ARCHITECTURE DESIGN:
{json.dumps(design, indent=2)}

Provide a detailed review including:
- Strengths of the design
- Potential weaknesses or concerns
- Specific recommendations for improvement
- Risk assessment for each criterion
- Alternative approaches to consider

Format as JSON with keys: strengths, weaknesses, recommendations, risks, alternatives"""
        
        response = await self.invoke_claude(user_message)
        
        try:
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()
            
            review = json.loads(json_str)
            review["raw_review"] = response
            
            return review
            
        except json.JSONDecodeError:
            return {"raw_review": response}
