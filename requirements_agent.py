"""
Requirements Analysis Agent

Purpose: Converts business requirements into detailed technical specifications
Capabilities:
- Analyzes business requirements and user stories
- Identifies technical constraints and dependencies
- Generates structured technical specifications
- Prioritizes features and creates acceptance criteria
"""

from typing import Dict, Any, List
from base_agent import BaseAgent
import json


class RequirementsAgent(BaseAgent):
    """
    Agent responsible for analyzing and structuring requirements.
    
    Input:
        - business_requirements: Raw business requirements text
        - project_context: Project background and constraints
        - stakeholders: List of stakeholder information
        
    Output:
        - technical_specifications: Detailed technical specs
        - user_stories: Structured user stories with acceptance criteria
        - dependencies: Identified technical dependencies
        - risks: Potential risks and mitigation strategies
    """
    
    def __init__(self, agent_id: str = "requirements_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="RequirementsAnalysis"
        )
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Requirements Analysis Agent in a software development lifecycle.

Your role is to:
1. Analyze business requirements and translate them into technical specifications
2. Identify functional and non-functional requirements
3. Create detailed user stories with acceptance criteria
4. Identify technical dependencies and constraints
5. Assess risks and propose mitigation strategies
6. Ensure requirements are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)

When analyzing requirements:
- Break down complex requirements into smaller, manageable components
- Identify ambiguities and request clarification
- Consider scalability, security, and performance implications
- Map requirements to technical architecture needs
- Prioritize requirements using MoSCoW method (Must have, Should have, Could have, Won't have)

Output Format:
Provide structured JSON output with the following sections:
- technical_specifications: Detailed technical requirements
- user_stories: Array of user stories with acceptance criteria
- functional_requirements: List of functional requirements
- non_functional_requirements: Performance, security, scalability requirements
- dependencies: Technical and business dependencies
- risks: Identified risks with severity and mitigation
- clarifications_needed: Any ambiguities requiring stakeholder input
- estimated_complexity: Overall complexity assessment (Low/Medium/High)

Be thorough, precise, and ask for clarification when requirements are ambiguous."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process business requirements into technical specifications.
        
        Args:
            input_data: Dictionary containing:
                - business_requirements: Raw requirements text
                - project_context: Optional project context
                - stakeholders: Optional stakeholder information
                
        Returns:
            Structured requirements analysis
        """
        # Validate input
        self.validate_input(input_data, ["business_requirements"])
        
        business_requirements = input_data["business_requirements"]
        project_context = input_data.get("project_context", "")
        stakeholders = input_data.get("stakeholders", [])
        
        # Build the analysis prompt
        user_message = self._build_analysis_prompt(
            business_requirements,
            project_context,
            stakeholders
        )
        
        # Update state
        self.update_state(
            current_task="Analyzing requirements",
            progress=0.3
        )
        
        # Invoke Claude for analysis
        self.logger.info("Invoking Claude for requirements analysis")
        response = await self.invoke_claude(user_message)
        
        # Parse and structure the response
        self.update_state(
            current_task="Structuring analysis results",
            progress=0.7
        )
        
        analysis_result = self._parse_analysis_response(response)
        
        # Add metadata
        analysis_result["metadata"] = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "input_length": len(business_requirements),
            "analysis_timestamp": self.state.started_at.isoformat()
        }
        
        self.logger.info("Requirements analysis completed")
        
        return analysis_result
    
    def _build_analysis_prompt(
        self,
        business_requirements: str,
        project_context: str,
        stakeholders: List[str]
    ) -> str:
        """Build the prompt for requirements analysis"""
        
        prompt = f"""Analyze the following business requirements and provide a comprehensive technical analysis.

BUSINESS REQUIREMENTS:
{business_requirements}
"""
        
        if project_context:
            prompt += f"""

PROJECT CONTEXT:
{project_context}
"""
        
        if stakeholders:
            prompt += f"""

STAKEHOLDERS:
{', '.join(stakeholders)}
"""
        
        prompt += """

Please provide a structured analysis including:

1. TECHNICAL SPECIFICATIONS
   - Detailed technical requirements
   - System architecture implications
   - Technology stack recommendations

2. USER STORIES
   - Create user stories in the format: "As a [user], I want [goal] so that [benefit]"
   - Include acceptance criteria for each story
   - Add story points estimation (1, 2, 3, 5, 8, 13)

3. FUNCTIONAL REQUIREMENTS
   - List all functional requirements
   - Categorize by feature area

4. NON-FUNCTIONAL REQUIREMENTS
   - Performance requirements
   - Security requirements
   - Scalability requirements
   - Reliability and availability requirements

5. DEPENDENCIES
   - Technical dependencies (libraries, services, APIs)
   - Business dependencies
   - Team dependencies

6. RISKS AND MITIGATION
   - Identify potential risks
   - Assess severity (Low/Medium/High)
   - Propose mitigation strategies

7. CLARIFICATIONS NEEDED
   - List any ambiguities or unclear requirements
   - Suggest questions for stakeholders

8. COMPLEXITY ASSESSMENT
   - Overall project complexity (Low/Medium/High)
   - Breakdown by component

Please structure your response as valid JSON."""
        
        return prompt
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's response into structured data"""
        
        try:
            # Try to extract JSON from the response
            # Claude might wrap JSON in markdown code blocks
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
                "technical_specifications": parsed.get("technical_specifications", {}),
                "user_stories": parsed.get("user_stories", []),
                "functional_requirements": parsed.get("functional_requirements", []),
                "non_functional_requirements": parsed.get("non_functional_requirements", {}),
                "dependencies": parsed.get("dependencies", []),
                "risks": parsed.get("risks", []),
                "clarifications_needed": parsed.get("clarifications_needed", []),
                "complexity_assessment": parsed.get("complexity_assessment", "Medium"),
                "raw_analysis": response
            }
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            # Return a structured format with the raw response
            return {
                "technical_specifications": {},
                "user_stories": [],
                "functional_requirements": [],
                "non_functional_requirements": {},
                "dependencies": [],
                "risks": [],
                "clarifications_needed": [],
                "complexity_assessment": "Unknown",
                "raw_analysis": response,
                "parse_error": str(e)
            }
    
    async def refine_requirements(
        self,
        initial_analysis: Dict[str, Any],
        stakeholder_feedback: str
    ) -> Dict[str, Any]:
        """
        Refine requirements based on stakeholder feedback.
        
        Args:
            initial_analysis: Previous analysis results
            stakeholder_feedback: Feedback from stakeholders
            
        Returns:
            Refined requirements analysis
        """
        
        self.logger.info("Refining requirements based on feedback")
        
        user_message = f"""Based on the initial requirements analysis and stakeholder feedback, 
please refine and update the requirements.

INITIAL ANALYSIS:
{json.dumps(initial_analysis, indent=2)}

STAKEHOLDER FEEDBACK:
{stakeholder_feedback}

Please provide an updated requirements analysis addressing the feedback 
and refining the specifications as needed. Maintain the same JSON structure."""
        
        response = await self.invoke_claude(user_message)
        refined_result = self._parse_analysis_response(response)
        
        refined_result["metadata"] = {
            "agent_id": self.agent_id,
            "refinement_iteration": initial_analysis.get("metadata", {}).get("refinement_iteration", 0) + 1,
            "refined_timestamp": datetime.now().isoformat()
        }
        
        return refined_result
