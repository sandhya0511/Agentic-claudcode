"""
Main Execution Script for Agentic SDLC System

This script demonstrates how to use the agentic SDLC system.
It can be run directly or imported as a module.
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from workflow import AgentOrchestrator


def setup_logging():
    """Configure logging for the application"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/sdlc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )


def save_results(results: dict, output_dir: str = "output"):
    """
    Save workflow results to files.
    
    Args:
        results: Workflow results
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save complete results as JSON
    results_file = output_path / f"sdlc_results_{timestamp}.json"
    
    # Convert datetime objects to strings for JSON serialization
    serializable_results = json.loads(
        json.dumps(results, default=str)
    )
    
    with open(results_file, 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n✓ Complete results saved to: {results_file}")
    
    # Save individual artifacts
    artifacts_dir = output_path / f"artifacts_{timestamp}"
    artifacts_dir.mkdir(exist_ok=True)
    
    # Save code files
    if results.get("generated_code") and results["generated_code"].get("files"):
        code_dir = artifacts_dir / "code"
        code_dir.mkdir(exist_ok=True)
        
        for filename, code in results["generated_code"]["files"].items():
            with open(code_dir / filename, 'w') as f:
                f.write(code)
        
        print(f"✓ Code files saved to: {code_dir}")
    
    # Save test files
    if results.get("test_results") and results["test_results"].get("test_files"):
        tests_dir = artifacts_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        for filename, code in results["test_results"]["test_files"].items():
            with open(tests_dir / filename, 'w') as f:
                f.write(code)
        
        print(f"✓ Test files saved to: {tests_dir}")
    
    # Save documentation
    if results.get("documentation") and results["documentation"].get("documentation_files"):
        docs_dir = artifacts_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        for filename, content in results["documentation"]["documentation_files"].items():
            with open(docs_dir / filename, 'w') as f:
                f.write(content)
        
        print(f"✓ Documentation saved to: {docs_dir}")
    
    # Save DevOps configurations
    if results.get("devops_config"):
        devops_dir = artifacts_dir / "devops"
        devops_dir.mkdir(exist_ok=True)
        
        devops_config = results["devops_config"]
        
        # Save Docker files
        if devops_config.get("docker_files"):
            for filename, content in devops_config["docker_files"].items():
                with open(devops_dir / filename, 'w') as f:
                    f.write(content)
        
        # Save CI/CD config
        if devops_config.get("ci_cd_config"):
            cicd_dir = devops_dir / ".github" / "workflows"
            cicd_dir.mkdir(parents=True, exist_ok=True)
            
            for filename, content in devops_config["ci_cd_config"].items():
                with open(cicd_dir / filename, 'w') as f:
                    f.write(content)
        
        print(f"✓ DevOps configurations saved to: {devops_dir}")
    
    print(f"\n✓ All artifacts saved to: {artifacts_dir}")
    
    return artifacts_dir


async def run_example_workflow():
    """Run an example SDLC workflow"""
    
    # Example business requirements
    business_requirements = """
    We need to build a Task Management API that allows users to:
    
    1. Create, read, update, and delete tasks
    2. Assign tasks to team members
    3. Set due dates and priorities for tasks
    4. Add comments to tasks
    5. Filter and search tasks by various criteria
    6. Track task completion status
    
    The system should:
    - Be RESTful
    - Support authentication and authorization
    - Be scalable to handle 10,000+ users
    - Have comprehensive API documentation
    - Include automated tests
    - Be deployable to cloud infrastructure
    
    Non-functional requirements:
    - Response time < 200ms for most operations
    - 99.9% uptime
    - Secure (HTTPS, encrypted data)
    - Easy to maintain and extend
    """
    
    # Project context
    project_context = {
        "project_name": "TaskMaster API",
        "stakeholders": ["Product Manager", "Engineering Team", "Users"],
        "constraints": {
            "timeline": "3 months",
            "team_size": 5,
            "budget": "medium"
        },
        "cloud_provider": "aws",
        "deployment_type": "kubernetes",
        "ci_cd_platform": "github-actions"
    }
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    print("\n" + "="*80)
    print("AGENTIC SDLC SYSTEM - WORKFLOW EXECUTION")
    print("="*80)
    print(f"\nProject: {project_context['project_name']}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "="*80 + "\n")
    
    # Run workflow
    results = await orchestrator.run_workflow(
        business_requirements=business_requirements,
        project_context=project_context
    )
    
    # Print summary
    print("\n" + "="*80)
    print("WORKFLOW SUMMARY")
    print("="*80)
    
    phases = [
        ("Requirements Analysis", results.get("requirements_complete")),
        ("Architecture Design", results.get("architecture_complete")),
        ("Code Generation", results.get("code_generation_complete")),
        ("Code Review", results.get("code_review_approved")),
        ("Testing", results.get("tests_complete")),
        ("Documentation", results.get("documentation_complete")),
        ("DevOps Configuration", results.get("devops_complete"))
    ]
    
    for phase_name, completed in phases:
        status = "✓ COMPLETED" if completed else "✗ FAILED"
        print(f"{phase_name:.<50} {status}")
    
    if results.get("errors"):
        print(f"\nErrors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"  ✗ {error}")
    
    if results.get("warnings"):
        print(f"\nWarnings: {len(results['warnings'])}")
        for warning in results["warnings"]:
            print(f"  ⚠ {warning}")
    
    # Print key metrics
    print("\n" + "="*80)
    print("KEY METRICS")
    print("="*80)
    
    if results.get("generated_code"):
        code_files = results["generated_code"].get("files", {})
        print(f"Code files generated: {len(code_files)}")
    
    if results.get("test_results"):
        test_files = results["test_results"].get("test_files", {})
        coverage = results["test_results"].get("coverage_estimate", 0)
        print(f"Test files generated: {len(test_files)}")
        print(f"Estimated coverage: {coverage}%")
    
    if results.get("code_review_results"):
        score = results["code_review_results"].get("overall_score", 0)
        print(f"Code quality score: {score}/100")
    
    print("\n" + "="*80)
    
    # Save results
    artifacts_dir = save_results(results)
    
    print("\n" + "="*80)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*80)
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Artifacts location: {artifacts_dir}")
    print("\n")
    
    return results


async def run_custom_workflow(
    requirements_file: str,
    context_file: str = None
):
    """
    Run a custom workflow from files.
    
    Args:
        requirements_file: Path to file with business requirements
        context_file: Optional path to JSON file with project context
    """
    
    # Load requirements
    with open(requirements_file, 'r') as f:
        business_requirements = f.read()
    
    # Load context if provided
    project_context = {}
    if context_file:
        with open(context_file, 'r') as f:
            project_context = json.load(f)
    
    # Initialize and run
    orchestrator = AgentOrchestrator()
    
    print(f"\nRunning workflow with requirements from: {requirements_file}")
    if context_file:
        print(f"Using context from: {context_file}")
    
    results = await orchestrator.run_workflow(
        business_requirements=business_requirements,
        project_context=project_context
    )
    
    # Save results
    save_results(results)
    
    return results


def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    setup_logging()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("\nPlease:")
        print("1. Copy .env.template to .env")
        print("2. Add your Anthropic API key to .env")
        print("3. Run the script again\n")
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agentic SDLC System - End-to-End Software Development Automation"
    )
    parser.add_argument(
        "--requirements",
        type=str,
        help="Path to file containing business requirements"
    )
    parser.add_argument(
        "--context",
        type=str,
        help="Path to JSON file containing project context"
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run the built-in example workflow"
    )
    
    args = parser.parse_args()
    
    # Run appropriate workflow
    if args.example or (not args.requirements):
        # Run example workflow
        asyncio.run(run_example_workflow())
    else:
        # Run custom workflow
        asyncio.run(run_custom_workflow(args.requirements, args.context))


if __name__ == "__main__":
    main()
