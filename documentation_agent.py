"""
Documentation Agent

Purpose: Creates and maintains comprehensive documentation
Capabilities:
- Generates API documentation
- Creates README files
- Writes user guides
- Generates code comments
- Creates architecture documentation
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import json


class DocumentationAgent(BaseAgent):
    """
    Agent responsible for creating documentation.
    
    Input:
        - code_files: Code to document
        - doc_type: api, readme, user_guide, or all
        - language: Programming language
        - architecture: Optional architecture design
        - target_audience: developers, users, or both
        
    Output:
        - documentation_files: Generated documentation
        - api_docs: API documentation
        - readme: README content
        - guides: User/developer guides
        - diagrams: Documentation diagrams
    """
    
    def __init__(self, agent_id: str = "documentation_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="Documentation"
        )
        
        # Documentation types
        self.doc_types = [
            "api",
            "readme",
            "user_guide",
            "developer_guide",
            "architecture",
            "deployment",
            "troubleshooting"
        ]
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Documentation Agent that creates clear, comprehensive documentation.

Your role is to:
1. Generate clear, accurate, and complete documentation
2. Write for the appropriate audience (developers, users, etc.)
3. Create well-structured, easy-to-navigate documents
4. Include examples and code snippets
5. Document APIs, functions, and classes
6. Create visual diagrams when helpful
7. Maintain consistency in style and format

Documentation Types:

1. API DOCUMENTATION
   - Endpoint descriptions
   - Request/response formats
   - Authentication requirements
   - Error codes and messages
   - Rate limits
   - Code examples in multiple languages

2. README
   - Project overview
   - Installation instructions
   - Quick start guide
   - Configuration options
   - Usage examples
   - Contributing guidelines
   - License information

3. USER GUIDE
   - Feature explanations
   - Step-by-step tutorials
   - Screenshots/diagrams
   - Common use cases
   - FAQ section
   - Troubleshooting

4. DEVELOPER GUIDE
   - Architecture overview
   - Code organization
   - Development setup
   - Testing procedures
   - Deployment process
   - Contributing workflow

5. ARCHITECTURE DOCUMENTATION
   - System design overview
   - Component descriptions
   - Data flow diagrams
   - Technology stack
   - Design decisions and rationale
   - Scalability considerations

Documentation Principles:
- Clear and concise writing
- Consistent formatting and structure
- Progressive disclosure (simple → complex)
- Plenty of examples
- Visual aids (diagrams, screenshots)
- Up-to-date and accurate
- Searchable and well-organized
- Accessibility considerations

Writing Style:
- Active voice
- Present tense
- Short sentences and paragraphs
- Bullet points for lists
- Headers for organization
- Code formatting for technical terms
- Consistent terminology

Code Examples:
- Complete, runnable examples
- Include necessary imports
- Show both basic and advanced usage
- Explain the example
- Handle errors appropriately
- Follow best practices

Output Format:
Provide as JSON with:
- documentation_files: {filename: content}
- api_docs: API documentation
- readme: README.md content
- guides: {guide_name: content}
- diagrams: Mermaid diagram code
- metadata: {version, last_updated, contributors}

Generate professional, production-ready documentation."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation.
        
        Args:
            input_data: Dictionary containing:
                - code_files: Code to document (optional)
                - doc_type: Type of documentation
                - language: Programming language (optional)
                - architecture: Architecture design (optional)
                - target_audience: Target audience
                
        Returns:
            Generated documentation
        """
        
        code_files = input_data.get("code_files", {})
        doc_type = input_data.get("doc_type", "all")
        language = input_data.get("language", "")
        architecture = input_data.get("architecture", {})
        target_audience = input_data.get("target_audience", "developers")
        project_name = input_data.get("project_name", "Project")
        project_description = input_data.get("project_description", "")
        
        # Build the documentation prompt
        user_message = self._build_doc_prompt(
            code_files,
            doc_type,
            language,
            architecture,
            target_audience,
            project_name,
            project_description
        )
        
        # Update state
        self.update_state(
            current_task=f"Generating {doc_type} documentation",
            progress=0.3
        )
        
        # Invoke Claude for documentation generation
        self.logger.info(f"Generating {doc_type} documentation")
        response = await self.invoke_claude(user_message, max_tokens=8000)
        
        # Parse and structure the response
        self.update_state(
            current_task="Structuring documentation",
            progress=0.7
        )
        
        doc_result = self._parse_doc_response(response)
        
        # Generate additional diagrams if needed
        if architecture and "diagrams" not in doc_result:
            self.update_state(
                current_task="Generating diagrams",
                progress=0.9
            )
            doc_result["diagrams"] = await self._generate_diagrams(architecture)
        
        # Add metadata
        doc_result["metadata"] = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "doc_type": doc_type,
            "target_audience": target_audience,
            "generation_timestamp": self.state.started_at.isoformat()
        }
        
        self.logger.info("Documentation generation completed")
        
        return doc_result
    
    def _build_doc_prompt(
        self,
        code_files: Dict[str, str],
        doc_type: str,
        language: str,
        architecture: Dict[str, Any],
        target_audience: str,
        project_name: str,
        project_description: str
    ) -> str:
        """Build the prompt for documentation generation"""
        
        prompt = f"""Generate comprehensive {doc_type} documentation for {project_name}.

PROJECT NAME: {project_name}
PROJECT DESCRIPTION: {project_description}
TARGET AUDIENCE: {target_audience}
"""
        
        if language:
            prompt += f"PROGRAMMING LANGUAGE: {language}\n"
        
        if code_files:
            files_text = ""
            for filename, code in code_files.items():
                # Truncate very long files
                code_preview = code[:2000] + "..." if len(code) > 2000 else code
                files_text += f"\n\nFILE: {filename}\n{code_preview}"
            
            prompt += f"""
CODE FILES:
{files_text}
"""
        
        if architecture:
            prompt += f"""
ARCHITECTURE:
{json.dumps(architecture, indent=2)[:2000]}
"""
        
        prompt += f"""
Please generate the following documentation:

"""
        
        if doc_type == "all" or doc_type == "readme":
            prompt += """
1. README.md
   - Project title and description
   - Badges (build status, version, etc.)
   - Features overview
   - Installation instructions
   - Quick start / Getting started
   - Usage examples
   - Configuration
   - API reference (brief)
   - Contributing guidelines
   - License
   - Contact/Support information

"""
        
        if doc_type == "all" or doc_type == "api":
            prompt += """
2. API DOCUMENTATION
   - API overview
   - Authentication
   - Base URLs and versioning
   - Endpoints documentation:
     * HTTP method
     * Endpoint path
     * Description
     * Parameters (path, query, body)
     * Request example
     * Response format
     * Status codes
     * Error responses
   - Code examples in multiple languages
   - Rate limiting
   - Webhooks (if applicable)

"""
        
        if doc_type == "all" or doc_type == "user_guide":
            prompt += """
3. USER GUIDE
   - Introduction
   - Key concepts
   - Feature walkthroughs
   - Step-by-step tutorials
   - Common use cases
   - Best practices
   - FAQ
   - Troubleshooting
   - Glossary

"""
        
        if doc_type == "all" or doc_type == "developer_guide":
            prompt += """
4. DEVELOPER GUIDE (docs/CONTRIBUTING.md)
   - Development setup
   - Project structure
   - Code organization
   - Coding standards
   - Testing guidelines
   - Pull request process
   - Code review checklist
   - Release process
   - Architecture decisions

"""
        
        if doc_type == "all" or doc_type == "architecture":
            prompt += """
5. ARCHITECTURE DOCUMENTATION (docs/ARCHITECTURE.md)
   - System overview
   - High-level architecture diagram
   - Component descriptions
   - Data flow
   - Technology stack
   - Design decisions
   - Scalability approach
   - Security considerations
   - Performance considerations

"""
        
        prompt += """
FORMATTING REQUIREMENTS:
- Use Markdown format
- Clear section headers (# ## ###)
- Code blocks with language tags
- Tables for structured data
- Links to related documentation
- Consistent style throughout

Include diagrams as Mermaid code where appropriate.

Provide output as JSON with:
- documentation_files: {filename: markdown_content}
- api_docs: Structured API documentation
- readme: Full README content
- guides: {guide_type: content}
- diagrams: {diagram_name: mermaid_code}

Make documentation professional, clear, and complete."""
        
        return prompt
    
    def _parse_doc_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's documentation response"""
        
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
                "documentation_files": parsed.get("documentation_files", {}),
                "api_docs": parsed.get("api_docs", {}),
                "readme": parsed.get("readme", ""),
                "guides": parsed.get("guides", {}),
                "diagrams": parsed.get("diagrams", {}),
                "raw_response": response
            }
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            # Try to extract markdown content directly
            documentation_files = {}
            if "# " in response:  # Has markdown headers
                documentation_files["DOCUMENTATION.md"] = response
            
            return {
                "documentation_files": documentation_files,
                "api_docs": {},
                "readme": "",
                "guides": {},
                "diagrams": {},
                "raw_response": response,
                "parse_error": str(e)
            }
    
    async def _generate_diagrams(self, architecture: Dict[str, Any]) -> Dict[str, str]:
        """Generate Mermaid diagrams for documentation"""
        
        self.logger.info("Generating documentation diagrams")
        
        user_message = f"""Based on this architecture, generate Mermaid diagrams for documentation:

{json.dumps(architecture, indent=2)}

Generate:
1. High-level system diagram
2. Component interaction diagram
3. Data flow diagram
4. Deployment diagram

Provide as JSON: {{diagram_name: mermaid_code}}"""
        
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
            return {"diagrams": response}
    
    async def update_documentation(
        self,
        existing_docs: Dict[str, str],
        changes: str,
        doc_type: str
    ) -> Dict[str, Any]:
        """
        Update existing documentation based on code changes.
        
        Args:
            existing_docs: Existing documentation files
            changes: Description of changes made
            doc_type: Type of documentation to update
            
        Returns:
            Updated documentation
        """
        
        self.logger.info(f"Updating {doc_type} documentation")
        
        user_message = f"""Update the following documentation based on these changes:

CHANGES:
{changes}

EXISTING DOCUMENTATION:
{json.dumps(existing_docs, indent=2)}

Update the documentation to reflect these changes. Maintain the existing 
structure and style. Only modify sections affected by the changes.

Provide updated documentation as JSON with same structure."""
        
        response = await self.invoke_claude(user_message)
        
        return self._parse_doc_response(response)
