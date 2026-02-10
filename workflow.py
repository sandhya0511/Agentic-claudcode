"""
Agent Orchestration Framework

This module coordinates all SDLC agents using LangGraph for workflow management.
It handles:
- Agent execution order
- Data flow between agents
- Parallel execution where possible
- Error handling and retry logic
- State management across the workflow
"""

import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import logging
from langgraph.graph import StateGraph, END
from requirements_agent import RequirementsAgent
from architecture_agent import ArchitectureAgent
from code_generation_agent import CodeGenerationAgent
from code_review_agent import CodeReviewAgent
from testing_agent import TestingAgent
from documentation_agent import DocumentationAgent
from devops_agent import DevOpsAgent


class SDLCState(TypedDict):
    """
    State that flows through the SDLC workflow.
    Each agent reads from and writes to this state.
    """
    # Input
    business_requirements: str
    project_context: Optional[Dict[str, Any]]
    
    # Requirements phase
    technical_specifications: Optional[Dict[str, Any]]
    requirements_complete: bool
    
    # Architecture phase
    architecture_design: Optional[Dict[str, Any]]
    architecture_complete: bool
    
    # Code generation phase
    generated_code: Optional[Dict[str, Any]]
    code_generation_complete: bool
    
    # Code review phase
    code_review_results: Optional[Dict[str, Any]]
    code_review_approved: bool
    
    # Testing phase
    test_results: Optional[Dict[str, Any]]
    tests_complete: bool
    
    # Documentation phase
    documentation: Optional[Dict[str, Any]]
    documentation_complete: bool
    
    # DevOps phase
    devops_config: Optional[Dict[str, Any]]
    devops_complete: bool
    
    # Overall workflow state
    current_phase: str
    errors: List[str]
    warnings: List[str]
    workflow_complete: bool


class AgentOrchestrator:
    """
    Orchestrates the execution of all SDLC agents.
    
    Uses LangGraph to create a directed graph of agent execution,
    allowing for conditional branching and parallel execution.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AgentOrchestrator")
        
        # Initialize all agents
        self.requirements_agent = RequirementsAgent()
        self.architecture_agent = ArchitectureAgent()
        self.code_generation_agent = CodeGenerationAgent()
        self.code_review_agent = CodeReviewAgent()
        self.testing_agent = TestingAgent()
        self.documentation_agent = DocumentationAgent()
        self.devops_agent = DevOpsAgent()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        self.logger.info("Agent orchestrator initialized")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the SDLC workflow graph.
        
        Workflow:
        1. Requirements Analysis
        2. Architecture Design
        3. Code Generation
        4. Code Review (may loop back to generation)
        5. Testing (parallel with Documentation)
        6. Documentation (parallel with Testing)
        7. DevOps Configuration
        """
        
        workflow = StateGraph(SDLCState)
        
        # Add nodes for each agent
        workflow.add_node("requirements", self._requirements_node)
        workflow.add_node("architecture", self._architecture_node)
        workflow.add_node("code_generation", self._code_generation_node)
        workflow.add_node("code_review", self._code_review_node)
        workflow.add_node("testing", self._testing_node)
        workflow.add_node("documentation", self._documentation_node)
        workflow.add_node("devops", self._devops_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define the workflow edges
        workflow.set_entry_point("requirements")
        
        # Sequential flow
        workflow.add_edge("requirements", "architecture")
        workflow.add_edge("architecture", "code_generation")
        workflow.add_edge("code_generation", "code_review")
        
        # Conditional edge from code review
        workflow.add_conditional_edges(
            "code_review",
            self._should_regenerate_code,
            {
                "regenerate": "code_generation",
                "proceed": "testing"
            }
        )
        
        # Testing and documentation can run in parallel
        # But we'll run them sequentially for simplicity
        workflow.add_edge("testing", "documentation")
        workflow.add_edge("documentation", "devops")
        workflow.add_edge("devops", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def _requirements_node(self, state: SDLCState) -> SDLCState:
        """Execute requirements analysis agent"""
        self.logger.info("=== PHASE 1: Requirements Analysis ===")
        
        try:
            state["current_phase"] = "requirements"
            
            input_data = {
                "business_requirements": state["business_requirements"],
                "project_context": state.get("project_context", {}),
                "stakeholders": state.get("project_context", {}).get("stakeholders", [])
            }
            
            result = await self.requirements_agent.execute(input_data)
            
            state["technical_specifications"] = result
            state["requirements_complete"] = True
            
            self.logger.info("Requirements analysis completed successfully")
            
        except Exception as e:
            self.logger.error(f"Requirements analysis failed: {e}")
            state["errors"].append(f"Requirements phase: {str(e)}")
        
        return state
    
    async def _architecture_node(self, state: SDLCState) -> SDLCState:
        """Execute architecture design agent"""
        self.logger.info("=== PHASE 2: Architecture Design ===")
        
        try:
            state["current_phase"] = "architecture"
            
            if not state.get("requirements_complete"):
                raise ValueError("Requirements must be completed before architecture")
            
            input_data = {
                "technical_specifications": state["technical_specifications"],
                "constraints": state.get("project_context", {}).get("constraints", {}),
                "existing_systems": state.get("project_context", {}).get("existing_systems", [])
            }
            
            result = await self.architecture_agent.execute(input_data)
            
            state["architecture_design"] = result
            state["architecture_complete"] = True
            
            self.logger.info("Architecture design completed successfully")
            
        except Exception as e:
            self.logger.error(f"Architecture design failed: {e}")
            state["errors"].append(f"Architecture phase: {str(e)}")
        
        return state
    
    async def _code_generation_node(self, state: SDLCState) -> SDLCState:
        """Execute code generation agent"""
        self.logger.info("=== PHASE 3: Code Generation ===")
        
        try:
            state["current_phase"] = "code_generation"
            
            if not state.get("architecture_complete"):
                raise ValueError("Architecture must be completed before code generation")
            
            # Get language from architecture or default to Python
            tech_stack = state["architecture_design"].get("technology_stack", {})
            language = tech_stack.get("backend", {}).get("language", "python")
            framework = tech_stack.get("backend", {}).get("framework", "")
            
            # Generate code for main components
            tech_specs = state["technical_specifications"]
            user_stories = tech_specs.get("user_stories", [])
            
            # For now, generate code for the first few user stories
            # In production, you'd iterate through all components
            component_spec = f"""
Implement the following features based on user stories:

{user_stories[:3] if len(user_stories) > 3 else user_stories}

Technical Specifications:
{tech_specs.get('functional_requirements', [])}
"""
            
            input_data = {
                "component_specification": component_spec,
                "architecture_design": state["architecture_design"],
                "language": language,
                "framework": framework
            }
            
            result = await self.code_generation_agent.execute(input_data)
            
            state["generated_code"] = result
            state["code_generation_complete"] = True
            
            self.logger.info("Code generation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            state["errors"].append(f"Code generation phase: {str(e)}")
        
        return state
    
    async def _code_review_node(self, state: SDLCState) -> SDLCState:
        """Execute code review agent"""
        self.logger.info("=== PHASE 4: Code Review ===")
        
        try:
            state["current_phase"] = "code_review"
            
            if not state.get("code_generation_complete"):
                raise ValueError("Code generation must be completed before review")
            
            generated_code = state["generated_code"]
            language = state["generated_code"]["metadata"]["language"]
            
            input_data = {
                "code_files": generated_code.get("files", {}),
                "language": language,
                "review_criteria": [
                    "code_quality",
                    "security",
                    "performance",
                    "maintainability"
                ]
            }
            
            result = await self.code_review_agent.execute(input_data)
            
            state["code_review_results"] = result
            
            # Determine if code is approved
            approval_status = result.get("approval_status", "needs_review")
            state["code_review_approved"] = approval_status in ["approved", "approved_with_suggestions"]
            
            self.logger.info(f"Code review completed: {approval_status}")
            
            if not state["code_review_approved"]:
                state["warnings"].append("Code review requires changes")
            
        except Exception as e:
            self.logger.error(f"Code review failed: {e}")
            state["errors"].append(f"Code review phase: {str(e)}")
            state["code_review_approved"] = False
        
        return state
    
    def _should_regenerate_code(self, state: SDLCState) -> str:
        """Determine if code should be regenerated based on review"""
        
        # Check if there are critical issues
        review_results = state.get("code_review_results", {})
        issues_by_severity = review_results.get("issues_by_severity", {})
        critical_issues = issues_by_severity.get("critical", [])
        
        # For demo purposes, we'll proceed even with issues
        # In production, you might want to implement retry logic
        if critical_issues and len(state.get("errors", [])) < 3:
            return "regenerate"
        
        return "proceed"
    
    async def _testing_node(self, state: SDLCState) -> SDLCState:
        """Execute testing agent"""
        self.logger.info("=== PHASE 5: Testing ===")
        
        try:
            state["current_phase"] = "testing"
            
            generated_code = state["generated_code"]
            language = generated_code["metadata"]["language"]
            
            input_data = {
                "code_files": generated_code.get("files", {}),
                "test_type": "all",
                "language": language,
                "coverage_target": 80
            }
            
            result = await self.testing_agent.execute(input_data)
            
            state["test_results"] = result
            state["tests_complete"] = True
            
            self.logger.info("Testing completed successfully")
            
        except Exception as e:
            self.logger.error(f"Testing failed: {e}")
            state["errors"].append(f"Testing phase: {str(e)}")
        
        return state
    
    async def _documentation_node(self, state: SDLCState) -> SDLCState:
        """Execute documentation agent"""
        self.logger.info("=== PHASE 6: Documentation ===")
        
        try:
            state["current_phase"] = "documentation"
            
            generated_code = state["generated_code"]
            
            input_data = {
                "code_files": generated_code.get("files", {}),
                "doc_type": "all",
                "language": generated_code["metadata"]["language"],
                "architecture": state.get("architecture_design", {}),
                "target_audience": "developers",
                "project_name": state.get("project_context", {}).get("project_name", "Project"),
                "project_description": state.get("business_requirements", "")[:500]
            }
            
            result = await self.documentation_agent.execute(input_data)
            
            state["documentation"] = result
            state["documentation_complete"] = True
            
            self.logger.info("Documentation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Documentation failed: {e}")
            state["errors"].append(f"Documentation phase: {str(e)}")
        
        return state
    
    async def _devops_node(self, state: SDLCState) -> SDLCState:
        """Execute DevOps agent"""
        self.logger.info("=== PHASE 7: DevOps Configuration ===")
        
        try:
            state["current_phase"] = "devops"
            
            project_context = state.get("project_context", {})
            
            input_data = {
                "architecture": state.get("architecture_design", {}),
                "cloud_provider": project_context.get("cloud_provider", "aws"),
                "deployment_type": project_context.get("deployment_type", "docker"),
                "ci_cd_platform": project_context.get("ci_cd_platform", "github-actions"),
                "project_name": project_context.get("project_name", "project"),
                "language": state["generated_code"]["metadata"]["language"]
            }
            
            result = await self.devops_agent.execute(input_data)
            
            state["devops_config"] = result
            state["devops_complete"] = True
            
            self.logger.info("DevOps configuration completed successfully")
            
        except Exception as e:
            self.logger.error(f"DevOps configuration failed: {e}")
            state["errors"].append(f"DevOps phase: {str(e)}")
        
        return state
    
    async def _finalize_node(self, state: SDLCState) -> SDLCState:
        """Finalize the workflow and prepare output"""
        self.logger.info("=== FINALIZING WORKFLOW ===")
        
        state["current_phase"] = "complete"
        state["workflow_complete"] = True
        
        # Log summary
        self.logger.info("Workflow Summary:")
        self.logger.info(f"- Requirements: {'✓' if state.get('requirements_complete') else '✗'}")
        self.logger.info(f"- Architecture: {'✓' if state.get('architecture_complete') else '✗'}")
        self.logger.info(f"- Code Generation: {'✓' if state.get('code_generation_complete') else '✗'}")
        self.logger.info(f"- Code Review: {'✓' if state.get('code_review_approved') else '✗'}")
        self.logger.info(f"- Testing: {'✓' if state.get('tests_complete') else '✗'}")
        self.logger.info(f"- Documentation: {'✓' if state.get('documentation_complete') else '✗'}")
        self.logger.info(f"- DevOps: {'✓' if state.get('devops_complete') else '✗'}")
        
        if state["errors"]:
            self.logger.warning(f"Errors encountered: {len(state['errors'])}")
            for error in state["errors"]:
                self.logger.warning(f"  - {error}")
        
        if state["warnings"]:
            self.logger.info(f"Warnings: {len(state['warnings'])}")
            for warning in state["warnings"]:
                self.logger.info(f"  - {warning}")
        
        return state
    
    async def run_workflow(self, business_requirements: str, project_context=None):
        """Run the SDLC workflow and return final state."""

        initial_state = {
            "business_requirements": business_requirements,
            "project_context": project_context or {},
            "technical_specifications": None,
            "requirements_complete": False,
            "architecture_design": None,
            "architecture_complete": False,
            "generated_code": None,
            "code_generation_complete": False,
            "code_review_results": None,
            "code_review_approved": False,
            "test_results": None,
            "tests_complete": False,
            "documentation": None,
            "documentation_complete": False,
            "devops_config": None,
            "devops_complete": False,
            "current_phase": "start",
            "errors": [],
            "warnings": [],
            "workflow_complete": False,
        }

        final_state = await self.workflow.ainvoke(initial_state)

        return final_state
