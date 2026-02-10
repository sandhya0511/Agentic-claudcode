"""
Code Review Agent

Purpose: Reviews code for quality, security, and best practices
Capabilities:
- Performs comprehensive code reviews
- Identifies security vulnerabilities
- Checks code quality metrics
- Suggests improvements
- Validates against coding standards
"""

from typing import Dict, Any, List, Optional
from base_agent import BaseAgent
import json
import re


class CodeReviewAgent(BaseAgent):
    """
    Agent responsible for automated code review.
    
    Input:
        - code_files: Dictionary of filename: code content
        - language: Programming language
        - review_criteria: Specific aspects to review
        - coding_standards: Standards to check against
        
    Output:
        - review_summary: Overall review summary
        - issues: List of issues found (critical, major, minor)
        - suggestions: Improvement suggestions
        - metrics: Code quality metrics
        - security_findings: Security vulnerabilities
        - approval_status: approved/needs_changes/rejected
    """
    
    def __init__(self, agent_id: str = "code_review_agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="CodeReview"
        )
        
        # Review categories
        self.review_categories = [
            "code_quality",
            "security",
            "performance",
            "maintainability",
            "documentation",
            "testing",
            "best_practices"
        ]
        
        # Severity levels
        self.severity_levels = ["critical", "major", "minor", "suggestion"]
    
    def _get_system_prompt(self) -> str:
        return """You are an expert Code Review Agent that performs thorough code reviews.

Your role is to:
1. Review code for quality, security, and best practices
2. Identify bugs, vulnerabilities, and potential issues
3. Assess code maintainability and readability
4. Check adherence to coding standards
5. Evaluate test coverage and quality
6. Suggest specific improvements
7. Provide constructive, actionable feedback

Review Categories:

1. CODE QUALITY
   - Readability and clarity
   - Naming conventions
   - Code organization and structure
   - Complexity (cyclomatic complexity)
   - Code duplication
   - Dead code or unused variables

2. SECURITY
   - Input validation vulnerabilities
   - SQL injection risks
   - XSS vulnerabilities
   - Authentication/authorization issues
   - Sensitive data exposure
   - Dependency vulnerabilities
   - Insecure cryptography

3. PERFORMANCE
   - Inefficient algorithms
   - Memory leaks
   - Database query optimization
   - Unnecessary computations
   - Caching opportunities
   - Resource management

4. MAINTAINABILITY
   - SOLID principles adherence
   - Separation of concerns
   - Modularity
   - Coupling and cohesion
   - Code reusability
   - Extensibility

5. DOCUMENTATION
   - Code comments quality
   - API documentation
   - Function/method documentation
   - Complex logic explanation
   - README completeness

6. TESTING
   - Test coverage
   - Test quality and assertions
   - Edge case coverage
   - Test maintainability
   - Mock usage appropriateness

7. BEST PRACTICES
   - Language-specific idioms
   - Design pattern usage
   - Error handling
   - Logging practices
   - Configuration management

Issue Severity Levels:
- CRITICAL: Security vulnerabilities, data loss risks, system crashes
- MAJOR: Significant bugs, poor performance, major design flaws
- MINOR: Code quality issues, minor bugs, style violations
- SUGGESTION: Improvements, optimizations, alternative approaches

Review Guidelines:
- Be specific and cite line numbers or code snippets
- Explain WHY something is an issue
- Provide concrete suggestions for fixes
- Balance criticism with recognition of good practices
- Prioritize issues by severity and impact
- Be constructive and professional

Output Format:
Provide review as JSON with:
- review_summary: Executive summary of the review
- overall_score: Numeric score 0-100
- issues: Array of {severity, category, description, location, suggestion}
- positive_aspects: Things done well
- metrics: {complexity, maintainability_index, code_smells_count}
- security_findings: Specific security issues
- recommendations: Prioritized improvement recommendations
- approval_status: "approved" | "approved_with_suggestions" | "needs_changes" | "rejected"

Be thorough but fair in your review."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform code review.
        
        Args:
            input_data: Dictionary containing:
                - code_files: Files to review
                - language: Programming language
                - review_criteria: Optional specific criteria
                - coding_standards: Optional standards to check
                
        Returns:
            Complete code review results
        """
        # Validate input
        self.validate_input(input_data, ["code_files", "language"])
        
        code_files = input_data["code_files"]
        language = input_data["language"]
        review_criteria = input_data.get("review_criteria", self.review_categories)
        coding_standards = input_data.get("coding_standards", {})
        
        # Build the review prompt
        user_message = self._build_review_prompt(
            code_files,
            language,
            review_criteria,
            coding_standards
        )
        
        # Update state
        self.update_state(
            current_task="Performing code review",
            progress=0.3
        )
        
        # Invoke Claude for code review
        self.logger.info(f"Reviewing {len(code_files)} files")
        response = await self.invoke_claude(user_message, max_tokens=8000)
        
        # Parse and structure the response
        self.update_state(
            current_task="Structuring review results",
            progress=0.7
        )
        
        review_result = self._parse_review_response(response)
        
        # Calculate additional metrics
        self.update_state(
            current_task="Calculating code metrics",
            progress=0.9
        )
        
        additional_metrics = self._calculate_metrics(code_files, language)
        review_result["metrics"].update(additional_metrics)
        
        # Add metadata
        review_result["metadata"] = {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "files_reviewed": len(code_files),
            "language": language,
            "review_timestamp": self.state.started_at.isoformat()
        }
        
        self.logger.info(f"Code review completed: {review_result['approval_status']}")
        
        return review_result
    
    def _build_review_prompt(
        self,
        code_files: Dict[str, str],
        language: str,
        review_criteria: List[str],
        coding_standards: Dict[str, Any]
    ) -> str:
        """Build the prompt for code review"""
        
        # Format code files for review
        files_text = ""
        for filename, code in code_files.items():
            files_text += f"\n\n{'='*60}\nFILE: {filename}\n{'='*60}\n{code}"
        
        prompt = f"""Perform a comprehensive code review of the following {language} code.

REVIEW CRITERIA:
{', '.join(review_criteria)}
"""
        
        if coding_standards:
            prompt += f"""
CODING STANDARDS TO CHECK:
{json.dumps(coding_standards, indent=2)}
"""
        
        prompt += f"""
CODE TO REVIEW:
{files_text}

Please provide a detailed code review including:

1. REVIEW SUMMARY
   - Overall assessment
   - Key findings
   - Critical issues count
   - Recommendation

2. OVERALL SCORE (0-100)
   Based on code quality, security, and best practices

3. ISSUES FOUND
   For each issue provide:
   - severity: critical | major | minor | suggestion
   - category: code_quality | security | performance | maintainability | documentation | testing | best_practices
   - description: Clear description of the issue
   - location: File and line number/function where issue exists
   - suggestion: Specific fix or improvement suggestion
   - example: If applicable, show the problematic code and suggested fix

4. POSITIVE ASPECTS
   - Things the code does well
   - Good practices observed
   - Strengths of the implementation

5. CODE METRICS
   - cyclomatic_complexity: Estimated complexity
   - maintainability_index: 0-100 score
   - code_smells_count: Number of code smells detected
   - test_coverage_estimate: Estimated test coverage
   - lines_of_code: Total lines
   - comment_ratio: Ratio of comments to code

6. SECURITY FINDINGS
   - Specific security vulnerabilities
   - Severity of each vulnerability
   - Recommended fixes

7. RECOMMENDATIONS
   - Prioritized list of improvements
   - Quick wins (easy, high impact)
   - Long-term improvements

8. APPROVAL STATUS
   - "approved": Code is good to merge
   - "approved_with_suggestions": Can merge but improvements recommended
   - "needs_changes": Must address issues before merging
   - "rejected": Critical issues, significant rework needed

Provide comprehensive, specific, and actionable feedback.
Format as JSON with all sections above."""
        
        return prompt
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's review response"""
        
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
                "review_summary": parsed.get("review_summary", ""),
                "overall_score": parsed.get("overall_score", 0),
                "issues": parsed.get("issues", []),
                "positive_aspects": parsed.get("positive_aspects", []),
                "metrics": parsed.get("metrics", {}),
                "security_findings": parsed.get("security_findings", []),
                "recommendations": parsed.get("recommendations", []),
                "approval_status": parsed.get("approval_status", "needs_review"),
                "raw_review": response
            }
            
            # Categorize issues by severity
            result["issues_by_severity"] = self._categorize_issues(result["issues"])
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            
            return {
                "review_summary": "Review parsing failed",
                "overall_score": 0,
                "issues": [],
                "positive_aspects": [],
                "metrics": {},
                "security_findings": [],
                "recommendations": [],
                "approval_status": "needs_review",
                "raw_review": response,
                "parse_error": str(e)
            }
    
    def _categorize_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Categorize issues by severity"""
        categorized = {
            "critical": [],
            "major": [],
            "minor": [],
            "suggestion": []
        }
        
        for issue in issues:
            severity = issue.get("severity", "minor").lower()
            if severity in categorized:
                categorized[severity].append(issue)
        
        return categorized
    
    def _calculate_metrics(
        self,
        code_files: Dict[str, str],
        language: str
    ) -> Dict[str, Any]:
        """Calculate basic code metrics"""
        
        metrics = {
            "total_files": len(code_files),
            "total_lines": 0,
            "total_code_lines": 0,
            "total_comment_lines": 0,
            "total_blank_lines": 0,
            "average_file_length": 0,
            "longest_file": "",
            "longest_file_lines": 0
        }
        
        for filename, code in code_files.items():
            lines = code.split('\n')
            file_lines = len(lines)
            
            code_lines = 0
            comment_lines = 0
            blank_lines = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    blank_lines += 1
                elif self._is_comment_line(stripped, language):
                    comment_lines += 1
                else:
                    code_lines += 1
            
            metrics["total_lines"] += file_lines
            metrics["total_code_lines"] += code_lines
            metrics["total_comment_lines"] += comment_lines
            metrics["total_blank_lines"] += blank_lines
            
            if file_lines > metrics["longest_file_lines"]:
                metrics["longest_file"] = filename
                metrics["longest_file_lines"] = file_lines
        
        if code_files:
            metrics["average_file_length"] = metrics["total_lines"] / len(code_files)
        
        if metrics["total_code_lines"] > 0:
            metrics["comment_ratio"] = metrics["total_comment_lines"] / metrics["total_code_lines"]
        else:
            metrics["comment_ratio"] = 0
        
        return metrics
    
    def _is_comment_line(self, line: str, language: str) -> bool:
        """Check if a line is a comment"""
        comment_patterns = {
            "python": r'^\s*#',
            "javascript": r'^\s*(//|/\*|\*)',
            "typescript": r'^\s*(//|/\*|\*)',
            "java": r'^\s*(//|/\*|\*)',
            "go": r'^\s*//',
            "rust": r'^\s*//',
            "c++": r'^\s*(//|/\*|\*)',
            "c#": r'^\s*(//|/\*|\*)'
        }
        
        pattern = comment_patterns.get(language.lower(), r'^\s*(//|#)')
        return bool(re.match(pattern, line))
    
    async def review_diff(
        self,
        original_code: str,
        modified_code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Review changes between original and modified code.
        
        Args:
            original_code: Original code
            modified_code: Modified code
            language: Programming language
            
        Returns:
            Diff review results
        """
        
        self.logger.info("Reviewing code diff")
        
        user_message = f"""Review the changes between the original and modified {language} code.

ORIGINAL CODE:
{original_code}

MODIFIED CODE:
{modified_code}

Provide a review of the changes including:
- Summary of changes made
- Improvements in the modified code
- Any regressions or new issues introduced
- Overall assessment of the changes

Format as JSON with keys: changes_summary, improvements, regressions, assessment"""
        
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
