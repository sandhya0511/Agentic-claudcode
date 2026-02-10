"""
Base Agent Class for Agentic SDLC System

This provides the foundation for all specialized agents in the system.
Each agent inherits core capabilities and implements specific SDLC functions.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from anthropic import Anthropic
from pydantic import BaseModel, Field


class AgentMessage(BaseModel):
    """Structured message format for inter-agent communication"""
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    content: Dict[str, Any]
    message_type: str  # request, response, notification
    priority: int = Field(default=1, ge=1, le=5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """Tracks the state of an agent during execution"""
    agent_id: str
    status: str  # idle, working, completed, failed
    current_task: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    error: Optional[str] = None
    results: Dict[str, Any] = Field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BaseAgent(ABC):
    """
    Base class for all SDLC agents.
    
    Provides:
    - Claude API integration
    - Logging and monitoring
    - State management
    - Inter-agent communication
    - Error handling
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        
        # Load configuration
        self.model = model or os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", "8000"))
        self.temperature = temperature or float(os.getenv("TEMPERATURE", "0.7"))
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Initialize state
        self.state = AgentState(
            agent_id=agent_id,
            status="idle"
        )
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Agent-specific system prompt (to be defined by subclasses)
        self.system_prompt = self._get_system_prompt()
        
        self.logger.info(f"Initialized {agent_type} agent: {agent_id}")
    
    def _setup_logger(self) -> logging.Logger:
        """Configure logging for the agent"""
        logger = logging.getLogger(f"Agent.{self.agent_id}")
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        log_file = os.getenv("LOG_FILE", "logs/agentic_sdlc.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Define the system prompt for this agent.
        Must be implemented by each specialized agent.
        """
        pass
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for the agent.
        Must be implemented by each specialized agent.
        """
        pass
    
    async def invoke_claude(
        self,
        user_message: str,
        context: Optional[List[Dict[str, str]]] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Invoke Claude API with the agent's system prompt.
        
        Args:
            user_message: The user/task message
            context: Optional conversation history
            max_tokens: Optional override for max tokens
            
        Returns:
            Claude's response text
        """
        messages = context or []
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"Error invoking Claude: {str(e)}")
            raise
    
    def update_state(
        self,
        status: Optional[str] = None,
        current_task: Optional[str] = None,
        progress: Optional[float] = None,
        error: Optional[str] = None,
        results: Optional[Dict[str, Any]] = None
    ):
        """Update the agent's state"""
        if status:
            self.state.status = status
            if status == "working" and not self.state.started_at:
                self.state.started_at = datetime.now()
            elif status in ["completed", "failed"]:
                self.state.completed_at = datetime.now()
        
        if current_task:
            self.state.current_task = current_task
        
        if progress is not None:
            self.state.progress = progress
        
        if error:
            self.state.error = error
        
        if results:
            self.state.results.update(results)
        
        self.logger.debug(f"State updated: {self.state.status} - {self.state.current_task}")
    
    def get_state(self) -> AgentState:
        """Get current agent state"""
        return self.state
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main process with error handling and state management.
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Processing results
        """
        try:
            self.update_state(status="working", current_task="Processing request")
            self.logger.info(f"Starting execution with input: {list(input_data.keys())}")
            
            # Call the agent-specific processing logic
            result = await self.process(input_data)
            
            self.update_state(
                status="completed",
                progress=1.0,
                results=result
            )
            self.logger.info("Execution completed successfully")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}", exc_info=True)
            self.update_state(
                status="failed",
                error=str(e)
            )
            raise
    
    def create_message(
        self,
        content: Dict[str, Any],
        message_type: str = "response",
        priority: int = 1
    ) -> AgentMessage:
        """Create a structured message for inter-agent communication"""
        return AgentMessage(
            agent_id=self.agent_id,
            content=content,
            message_type=message_type,
            priority=priority
        )
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that input data contains required fields.
        
        Args:
            input_data: Input data to validate
            required_fields: List of required field names
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        missing_fields = [field for field in required_fields if field not in input_data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return True
