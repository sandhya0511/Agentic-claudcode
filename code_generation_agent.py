"""
Code Generation Agent

Purpose: Generates production-ready code based on architecture and specifications
Capabilities:
- Generates code in multiple languages
- Creates modular, well-documented code
- Implements design patterns correctly
- Generates tests alongside code
- Follows language-specific best practices
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import json
import os


class CodeGenerationAgent(BaseAgent):
    """
    Agent responsible for generating production-quality code.
    
    Input:
        - component_specification: What to build
        - architecture_design: Architecture context
        - language: Target programming language
        - framework: Optional framework to use
        - coding_standards: Optional coding standards to follow
        
    Output:
        - code_files: Dictionary of filename: code content
        - tests: Test files for the generated code
        - documentation: Code documentation
        - dependencies: Required dependencies/packages
    """
    
    def __init__(self, agent_id: str = "code_generation_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="CodeGeneration"
        )
        
        # Language-specific templates and best practices
        self.language_config = {
            "python": {
                "style_guide": "PEP 8",
                "test_framework": "pytest",
                "doc_style": "Google docstrings"
            },
            "javascript": {
                "style_guide": "Airbnb",
                "test_framework": "Jest",
                "doc_style": "JSDoc"
            },
            "typescript": {
                "style_guide": "Airbnb TypeScript",
                "test_framework": "Jest",
                "doc_style": "TSDoc"
            },
            "java": {
                "style_guide": "Google Java Style",
                "test_framework": "JUnit 5",
                "doc_style": "Javadoc"
            },
            "go": {
                "style_guide": "Effective Go",
                "test_framework": "Go testing",
                "doc_style": "Godoc"
            }
        }
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Code Generation Agent that produces production-ready code.

Your role is to:
1. Generate clean, maintainable, and well-documented code
2. Follow language-specific best practices and style guides
3. Implement proper error handling and logging
4. Write modular, testable code
5. Include comprehensive unit tests
6. Add inline documentation and comments where needed
7. Consider security implications
8. Optimize for performance where appropriate

Code Quality Standards:
- Follow SOLID principles
- Write self-documenting code with clear naming
- Keep functions/methods focused and small
- Avoid code duplication (DRY)
- Handle edge cases and errors gracefully
- Include input validation
- Use appropriate design patterns
- Write defensive code

Documentation Standards:
- Add file/module headers explaining purpose
- Document all public APIs with docstrings
- Include usage examples in documentation
- Document complex algorithms or business logic
- Add inline comments for non-obvious code

Testing Standards:
- Write unit tests for all functions/methods
- Achieve high code coverage (aim for 80%+)
- Test edge cases and error conditions
- Use clear test names that describe what's being tested
- Follow AAA pattern (Arrange, Act, Assert)

Security Considerations:
- Validate all inputs
- Sanitize user data
- Use parameterized queries for database access
- Don't hardcode secrets or credentials
- Implement proper authentication and authorization
- Follow principle of least privilege

Output Format:
Provide code as a JSON object with:
- files: Dictionary of {filename: code_content}
- tests: Dictionary of {test_filename: test_code}
- dependencies: List of required packages/libraries
- documentation: README or API documentation
- setup_instructions: How to run/deploy the code

Generate complete, production-ready code that can be directly used."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code based on specifications.
        
        Args:
            input_data: Dictionary containing:
                - component_specification: What to build
                - architecture_design: Architecture context
                - language: Target language
                - framework: Optional framework
                - coding_standards: Optional standards
                
        Returns:
            Generated code, tests, and documentation
        """
        # Validate input
        self.validate_input(input_data, ["component_specification", "language"])
        
        component_spec = input_data["component_specification"]
        architecture = input_data.get("architecture_design", {})
        language = input_data["language"].lower()
        framework = input_data.get("framework", "")
        coding_standards = input_data.get("coding_standards", {})
        
        # Get language configuration
        lang_config = self.language_config.get(language, {})
        
        # Build the code generation prompt
        user_message = self._build_generation_prompt(
            component_spec,
            architecture,
            language,
            framework,
            coding_standards,
            lang_config
        )
        
        # Update state
        self.update_state(
            current_task=f"Generating {language} code",
            progress=0.3
        )
        
        # Invoke Claude for code generation
        self.logger.info(f"Generating code for {language}")
        response = await self.invoke_claude(user_message, max_tokens=8000)
        
        # Parse and structure the response
        self.update_state(
            current_task="Structuring generated code",
            progress=0.7
        )
        
        code_result = self._parse_code_response(response, language)
        
        # Validate generated code syntax if possible
        self.update_state(
            current_task="Validating generated code",
            progress=0.9
        )
        
        validation_result = await self._validate_code(code_result, language)
        code_result["validation"] = validation_result
        
        # Add metadata
        code_result["metadata"] = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "language": language,
            "framework": framework,
            "generation_timestamp": self.state.started_at.isoformat()
        }
        
        self.logger.info("Code generation completed")
        
        return code_result
    
    def _build_generation_prompt(
        self,
        component_spec: str,
        architecture: Dict[str, Any],
        language: str,
        framework: str,
        coding_standards: Dict[str, Any],
        lang_config: Dict[str, Any]
    ) -> str:
        """Build the prompt for code generation"""
        
        prompt = f"""Generate production-ready {language} code based on the following specification.

COMPONENT SPECIFICATION:
{component_spec}

TARGET LANGUAGE: {language}
"""
        
        if framework:
            prompt += f"FRAMEWORK: {framework}\n"
        
        if lang_config:
            prompt += f"""
LANGUAGE-SPECIFIC REQUIREMENTS:
- Style Guide: {lang_config.get('style_guide', 'Standard')}
- Test Framework: {lang_config.get('test_framework', 'Standard')}
- Documentation Style: {lang_config.get('doc_style', 'Standard')}
"""
        
        if architecture:
            prompt += f"""
ARCHITECTURE CONTEXT:
{json.dumps(architecture, indent=2)}
"""
        
        if coding_standards:
            prompt += f"""
CODING STANDARDS:
{json.dumps(coding_standards, indent=2)}
"""
        
        prompt += """

Please generate:

1. IMPLEMENTATION CODE
   - Complete, working implementation
   - Proper project structure
   - Well-organized modules/packages
   - Clear separation of concerns

2. UNIT TESTS
   - Comprehensive test coverage
   - Test edge cases and error conditions
   - Use appropriate testing framework
   - Include test fixtures/mocks if needed

3. DEPENDENCIES
   - List all required packages/libraries
   - Include version constraints
   - Provide installation instructions

4. DOCUMENTATION
   - README with overview and usage
   - API documentation for public interfaces
   - Setup and deployment instructions
   - Configuration guide

5. CONFIGURATION FILES
   - Any necessary config files (package.json, requirements.txt, etc.)
   - Environment variable templates
   - Build/deployment configs

IMPORTANT:
- Generate COMPLETE, RUNNABLE code
- Include ALL necessary imports/includes
- Add comprehensive error handling
- Follow best practices for the language
- Make code production-ready
- Ensure tests can actually run

Provide output as JSON with keys: files, tests, dependencies, documentation, config_files"""
        
        return prompt
    
    def _parse_code_response(self, response: str, language: str) -> Dict[str, Any]:
        """Parse Claude's response into structured code output"""
        
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
                "files": parsed.get("files", {}),
                "tests": parsed.get("tests", {}),
                "dependencies": parsed.get("dependencies", []),
                "documentation": parsed.get("documentation", ""),
                "config_files": parsed.get("config_files", {}),
                "raw_response": response
            }
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            # Try to extract code blocks directly
            files = {}
            code_blocks = self._extract_code_blocks(response)
            
            for i, block in enumerate(code_blocks):
                filename = f"generated_code_{i}.{self._get_file_extension(language)}"
                files[filename] = block
            
            return {
                "files": files,
                "tests": {},
                "dependencies": [],
                "documentation": "",
                "config_files": {},
                "raw_response": response,
                "parse_error": str(e)
            }
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown-formatted text"""
        blocks = []
        in_block = False
        current_block = []
        
        for line in text.split('\n'):
            if line.strip().startswith('```'):
                if in_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                    in_block = False
                else:
                    in_block = True
            elif in_block:
                current_block.append(line)
        
        return blocks
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for a language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "c++": "cpp",
            "c#": "cs"
        }
        return extensions.get(language.lower(), "txt")
    
    async def _validate_code(
        self,
        code_result: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """
        Validate the generated code for syntax and basic issues.
        
        Args:
            code_result: Generated code structure
            language: Programming language
            
        Returns:
            Validation results
        """
        
        validation = {
            "syntax_valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Basic validation checks
        files = code_result.get("files", {})
        
        if not files:
            validation["syntax_valid"] = False
            validation["issues"].append("No code files generated")
        
        # Language-specific basic checks
        for filename, code in files.items():
            if not code or len(code.strip()) < 10:
                validation["warnings"].append(f"{filename} appears to be empty or too short")
            
            # Check for common issues
            if language == "python":
                if "import" not in code and "def" in code:
                    validation["warnings"].append(f"{filename} may be missing imports")
            
            elif language in ["javascript", "typescript"]:
                if code.count("{") != code.count("}"):
                    validation["issues"].append(f"{filename} has mismatched braces")
        
        return validation
    
    async def refactor_code(
        self,
        code: str,
        refactoring_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Refactor existing code based on specific goals.
        
        Args:
            code: Code to refactor
            refactoring_goals: List of refactoring objectives
            
        Returns:
            Refactored code
        """
        
        self.logger.info("Refactoring code")
        
        user_message = f"""Refactor the following code to achieve these goals:
{', '.join(refactoring_goals)}

CODE:
{code}

Provide the refactored code along with:
- Explanation of changes made
- List of improvements
- Any trade-offs or considerations

Format as JSON with keys: refactored_code, changes, improvements, considerations"""
        
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
