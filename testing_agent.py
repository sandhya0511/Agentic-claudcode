"""
Testing Agent

Purpose: Generates and executes comprehensive tests
Capabilities:
- Generates unit tests, integration tests, and E2E tests
- Creates test data and fixtures
- Analyzes test coverage
- Identifies untested edge cases
- Generates test reports
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
import json


class TestingAgent(BaseAgent):
    """
    Agent responsible for test generation and analysis.
    
    Input:
        - code_files: Code to test
        - test_type: unit, integration, e2e, or all
        - language: Programming language
        - framework: Test framework to use
        - coverage_target: Target coverage percentage
        
    Output:
        - test_files: Generated test files
        - test_cases: List of test cases
        - test_data: Test fixtures and mock data
        - coverage_analysis: Coverage analysis
        - edge_cases: Identified edge cases
    """
    
    def __init__(self, agent_id: str = "testing_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="Testing"
        )
        
        # Test framework mappings
        self.test_frameworks = {
            "python": ["pytest", "unittest", "nose2"],
            "javascript": ["jest", "mocha", "jasmine", "vitest"],
            "typescript": ["jest", "mocha", "vitest"],
            "java": ["junit5", "junit4", "testng"],
            "go": ["testing", "testify"],
            "rust": ["cargo test"],
            "c#": ["xunit", "nunit", "mstest"]
        }
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Testing Agent that creates comprehensive test suites.

Your role is to:
1. Generate thorough test cases covering all code paths
2. Create unit tests for individual functions/methods
3. Design integration tests for component interactions
4. Develop end-to-end tests for user workflows
5. Generate test data and fixtures
6. Identify edge cases and boundary conditions
7. Ensure high test coverage (80%+ target)
8. Write maintainable and readable tests

Test Types:

1. UNIT TESTS
   - Test individual functions/methods in isolation
   - Mock external dependencies
   - Test happy path and edge cases
   - Validate input/output behavior
   - Test error handling

2. INTEGRATION TESTS
   - Test interactions between components
   - Test database operations
   - Test API integrations
   - Test service dependencies
   - Validate data flow

3. END-TO-END TESTS
   - Test complete user workflows
   - Simulate real user scenarios
   - Test UI interactions (if applicable)
   - Validate business processes
   - Test critical paths

Testing Principles:
- AAA Pattern: Arrange, Act, Assert
- One assertion per test (when possible)
- Clear, descriptive test names
- Independent tests (no dependencies between tests)
- Fast execution
- Deterministic results
- Easy to maintain

Test Coverage Goals:
- Critical paths: 100%
- Business logic: 90%+
- Overall code: 80%+
- Edge cases and errors: High priority

Edge Cases to Consider:
- Null/undefined/None inputs
- Empty collections
- Boundary values (min/max)
- Invalid inputs
- Concurrent access
- Network failures
- Timeout scenarios
- Large data sets
- Special characters in strings

Test Data:
- Create realistic test data
- Use factories or builders for complex objects
- Provide both valid and invalid data
- Include edge case data
- Make data easy to understand

Output Format:
Provide as JSON with:
- test_files: {filename: test_code}
- test_cases: [{name, description, type, assertions_count}]
- test_data: Test fixtures and mock data
- coverage_estimate: Estimated coverage percentage
- edge_cases_covered: List of edge cases tested
- setup_instructions: How to run the tests
- recommendations: Additional tests to consider

Generate complete, runnable tests that can be executed immediately."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive tests.
        
        Args:
            input_data: Dictionary containing:
                - code_files: Code to test
                - test_type: Type of tests (unit/integration/e2e/all)
                - language: Programming language
                - framework: Optional test framework
                - coverage_target: Target coverage %
                
        Returns:
            Generated tests and analysis
        """
        # Validate input
        self.validate_input(input_data, ["code_files", "language"])
        
        code_files = input_data["code_files"]
        test_type = input_data.get("test_type", "all")
        language = input_data["language"]
        framework = input_data.get("framework", "")
        coverage_target = input_data.get("coverage_target", 80)
        
        # Select appropriate test framework
        if not framework:
            frameworks = self.test_frameworks.get(language.lower(), [])
            framework = frameworks[0] if frameworks else "default"
        
        # Build the test generation prompt
        user_message = self._build_test_prompt(
            code_files,
            test_type,
            language,
            framework,
            coverage_target
        )
        
        # Update state
        self.update_state(
            current_task=f"Generating {test_type} tests",
            progress=0.3
        )
        
        # Invoke Claude for test generation
        self.logger.info(f"Generating {test_type} tests for {language}")
        response = await self.invoke_claude(user_message, max_tokens=8000)
        
        # Parse and structure the response
        self.update_state(
            current_task="Structuring test results",
            progress=0.7
        )
        
        test_result = self._parse_test_response(response)
        
        # Analyze coverage
        self.update_state(
            current_task="Analyzing test coverage",
            progress=0.9
        )
        
        coverage_analysis = self._analyze_coverage(
            code_files,
            test_result.get("test_files", {})
        )
        test_result["coverage_analysis"] = coverage_analysis
        
        # Add metadata
        test_result["metadata"] = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "test_type": test_type,
            "language": language,
            "framework": framework,
            "coverage_target": coverage_target,
            "generation_timestamp": self.state.started_at.isoformat()
        }
        
        self.logger.info("Test generation completed")
        
        return test_result
    
    def _build_test_prompt(
        self,
        code_files: Dict[str, str],
        test_type: str,
        language: str,
        framework: str,
        coverage_target: int
    ) -> str:
        """Build the prompt for test generation"""
        
        # Format code files
        files_text = ""
        for filename, code in code_files.items():
            files_text += f"\n\n{'='*60}\nFILE: {filename}\n{'='*60}\n{code}"
        
        prompt = f"""Generate comprehensive {test_type} tests for the following {language} code.

TEST FRAMEWORK: {framework}
COVERAGE TARGET: {coverage_target}%

CODE TO TEST:
{files_text}

Please generate:

1. TEST FILES
   - Complete test implementations
   - Proper test file naming conventions
   - Appropriate imports and setup
   - Test classes/suites organization

2. TEST CASES
   For each test provide:
   - name: Descriptive test name
   - description: What the test validates
   - type: unit | integration | e2e
   - assertions_count: Number of assertions
   - covers: Which function/method it tests

3. TEST DATA
   - Test fixtures
   - Mock data
   - Factory functions for test objects
   - Both valid and invalid test data

4. SETUP AND TEARDOWN
   - beforeEach/setUp functions
   - afterEach/tearDown functions
   - Test database setup (if needed)
   - Mock configurations

5. EDGE CASES COVERED
   - Null/undefined inputs
   - Empty collections
   - Boundary values
   - Error conditions
   - Concurrent scenarios
   - Invalid inputs

6. COVERAGE ESTIMATE
   - Estimated line coverage
   - Estimated branch coverage
   - Functions/methods covered
   - Critical paths covered

7. SETUP INSTRUCTIONS
   - How to install test dependencies
   - How to run tests
   - How to run specific test suites
   - How to generate coverage reports

8. RECOMMENDATIONS
   - Additional tests to add
   - Integration test scenarios
   - Performance test considerations
   - Security test considerations

TEST TYPES TO INCLUDE:
"""
        
        if test_type == "all":
            prompt += "- Unit tests for all functions/methods\n"
            prompt += "- Integration tests for component interactions\n"
            prompt += "- End-to-end tests for critical workflows\n"
        elif test_type == "unit":
            prompt += "- Comprehensive unit tests for all functions/methods\n"
        elif test_type == "integration":
            prompt += "- Integration tests for component interactions\n"
        elif test_type == "e2e":
            prompt += "- End-to-end tests for user workflows\n"
        
        prompt += """
IMPORTANT:
- Generate COMPLETE, RUNNABLE tests
- Include ALL necessary imports
- Use proper test framework syntax
- Add clear test descriptions
- Test both success and failure cases
- Make tests independent and isolated
- Ensure tests are deterministic

Provide output as JSON with all sections."""
        
        return prompt
    
    def _parse_test_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's test generation response"""
        
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
                "test_files": parsed.get("test_files", {}),
                "test_cases": parsed.get("test_cases", []),
                "test_data": parsed.get("test_data", {}),
                "coverage_estimate": parsed.get("coverage_estimate", 0),
                "edge_cases_covered": parsed.get("edge_cases_covered", []),
                "setup_instructions": parsed.get("setup_instructions", ""),
                "recommendations": parsed.get("recommendations", []),
                "raw_response": response
            }
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            return {
                "test_files": {},
                "test_cases": [],
                "test_data": {},
                "coverage_estimate": 0,
                "edge_cases_covered": [],
                "setup_instructions": "",
                "recommendations": [],
                "raw_response": response,
                "parse_error": str(e)
            }
    
    def _analyze_coverage(
        self,
        code_files: Dict[str, str],
        test_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """Analyze test coverage (basic estimation)"""
        
        analysis = {
            "code_files_count": len(code_files),
            "test_files_count": len(test_files),
            "has_tests": len(test_files) > 0,
            "test_to_code_ratio": 0,
            "estimated_coverage": 0
        }
        
        if not code_files:
            return analysis
        
        # Calculate lines
        total_code_lines = sum(len(code.split('\n')) for code in code_files.values())
        total_test_lines = sum(len(test.split('\n')) for test in test_files.values())
        
        if total_code_lines > 0:
            analysis["test_to_code_ratio"] = total_test_lines / total_code_lines
            
            # Rough estimation: 1:1 ratio suggests ~70% coverage, 2:1 suggests ~90%
            if analysis["test_to_code_ratio"] >= 2:
                analysis["estimated_coverage"] = 90
            elif analysis["test_to_code_ratio"] >= 1:
                analysis["estimated_coverage"] = 70
            elif analysis["test_to_code_ratio"] >= 0.5:
                analysis["estimated_coverage"] = 50
            else:
                analysis["estimated_coverage"] = 30
        
        return analysis
    
    async def identify_missing_tests(
        self,
        code_files: Dict[str, str],
        existing_tests: Dict[str, str],
        language: str
    ) -> Dict[str, Any]:
        """
        Identify code paths not covered by existing tests.
        
        Args:
            code_files: Source code files
            existing_tests: Existing test files
            language: Programming language
            
        Returns:
            Missing test identification
        """
        
        self.logger.info("Identifying missing tests")
        
        user_message = f"""Analyze the following code and tests to identify missing test coverage.

CODE FILES:
{json.dumps(code_files, indent=2)}

EXISTING TESTS:
{json.dumps(existing_tests, indent=2)}

Identify:
1. Functions/methods without any tests
2. Edge cases not covered
3. Error paths not tested
4. Integration scenarios missing
5. Recommended tests to add

Format as JSON with keys: untested_functions, missing_edge_cases, 
missing_error_tests, missing_integration_tests, priority_tests"""
        
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
