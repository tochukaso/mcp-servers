#!/usr/bin/env python3
"""
MCP Server with Multiple AI Personalities

This server implements the Model Context Protocol with a multi-personality system.
It features 4 different AI personalities with distinct roles and a manager to oversee them.

Usage:
    python mcp_personality_server.py

The server implements JSON-RPC 2.0 protocol over stdin/stdout for MCP compatibility.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class PersonalityType(Enum):
    """Enum for different personality types"""
    MANAGER = "manager"
    ANALYST = "analyst"
    CREATIVE = "creative"
    CRITIC = "critic"
    IMPLEMENTER = "implementer"


@dataclass
class PersonalityState:
    """State tracking for each personality"""
    personality_type: PersonalityType
    name: str
    role: str
    description: str
    active: bool = True
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    feedback_given: List[Dict[str, Any]] = field(default_factory=list)
    tasks_assigned: List[str] = field(default_factory=list)
    last_activity: Optional[datetime] = None


class PersonalityManager:
    """Manages all AI personalities and their interactions"""
    
    def __init__(self):
        self.personalities: Dict[PersonalityType, PersonalityState] = {}
        self.initialize_personalities()
        self.collaborative_session: Dict[str, Any] = {}
        self.session_history: List[Dict[str, Any]] = []
        logger.info("PersonalityManager initialized")
    
    def initialize_personalities(self):
        """Initialize all personalities with their roles and characteristics"""
        
        # Manager - Oversees all operations
        self.personalities[PersonalityType.MANAGER] = PersonalityState(
            personality_type=PersonalityType.MANAGER,
            name="Director",
            role="Project Manager & Coordinator",
            description="Oversees all operations, coordinates between personalities, makes final decisions, and ensures quality standards. Responsible for task delegation and overall project success."
        )
        
        # Analyst - Data analysis and logical reasoning
        self.personalities[PersonalityType.ANALYST] = PersonalityState(
            personality_type=PersonalityType.ANALYST,
            name="Logic",
            role="Data Analyst & Strategic Thinker",
            description="Focuses on logical analysis, data interpretation, risk assessment, and strategic planning. Provides fact-based insights and identifies potential issues."
        )
        
        # Creative - Innovation and creative solutions
        self.personalities[PersonalityType.CREATIVE] = PersonalityState(
            personality_type=PersonalityType.CREATIVE,
            name="Spark",
            role="Creative Innovator & Solution Designer",
            description="Generates innovative ideas, creative solutions, and out-of-the-box thinking. Focuses on user experience and aesthetic aspects."
        )
        
        # Critic - Quality assurance and improvement
        self.personalities[PersonalityType.CRITIC] = PersonalityState(
            personality_type=PersonalityType.CRITIC,
            name="Guardian",
            role="Quality Assurance & Process Optimizer",
            description="Identifies flaws, suggests improvements, ensures quality standards, and challenges assumptions. Provides constructive criticism and quality control."
        )
        
        # Implementer - Execution and practical solutions
        self.personalities[PersonalityType.IMPLEMENTER] = PersonalityState(
            personality_type=PersonalityType.IMPLEMENTER,
            name="Builder",
            role="Implementation Specialist & Problem Solver",
            description="Focuses on practical implementation, technical execution, and hands-on problem solving. Ensures ideas become actionable reality."
        )
        
        logger.info("All personalities initialized")
    
    def get_personality_prompt(self, personality_type: PersonalityType) -> str:
        """Get the specific prompt for each personality"""
        personality = self.personalities[personality_type]
        
        base_prompt = f"""You are {personality.name}, the {personality.role}.
        
Your core characteristics:
{personality.description}

Your responsibilities:
"""
        
        if personality_type == PersonalityType.MANAGER:
            return base_prompt + """
- Coordinate all personality interactions
- Make final decisions after consulting others
- Assign tasks and monitor progress
- Resolve conflicts between personalities
- Ensure project goals are met
- Provide executive summaries and final recommendations

Communication style: Professional, decisive, diplomatic
"""
        
        elif personality_type == PersonalityType.ANALYST:
            return base_prompt + """
- Analyze data and provide factual insights
- Identify patterns, trends, and correlations
- Assess risks and opportunities
- Provide evidence-based recommendations
- Challenge assumptions with data
- Create structured analysis reports

Communication style: Logical, precise, evidence-based
"""
        
        elif personality_type == PersonalityType.CREATIVE:
            return base_prompt + """
- Generate innovative ideas and creative solutions
- Think outside conventional boundaries
- Focus on user experience and design
- Propose unconventional approaches
- Inspire and motivate the team
- Create engaging and aesthetic solutions

Communication style: Imaginative, inspiring, enthusiastic
"""
        
        elif personality_type == PersonalityType.CRITIC:
            return base_prompt + """
- Identify potential problems and weaknesses
- Provide constructive criticism and feedback
- Challenge ideas to improve them
- Ensure quality standards are maintained
- Test assumptions and validate approaches
- Prevent costly mistakes through careful review

Communication style: Constructive, thorough, quality-focused
"""
        
        elif personality_type == PersonalityType.IMPLEMENTER:
            return base_prompt + """
- Focus on practical implementation details
- Solve technical and operational challenges
- Create actionable plans and procedures
- Ensure feasibility of proposed solutions
- Handle execution and delivery
- Provide hands-on problem solving

Communication style: Practical, action-oriented, solution-focused
"""
        
        return base_prompt
    
    def log_interaction(self, personality_type: PersonalityType, interaction_type: str, content: str):
        """Log personality interactions"""
        personality = self.personalities[personality_type]
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "content": content,
            "personality": personality.name
        }
        personality.conversation_history.append(interaction)
        personality.last_activity = datetime.now()
        
        # Also log to session history
        self.session_history.append(interaction)
        
        logger.info(f"Interaction logged: {personality.name} - {interaction_type}")
    
    def get_personality_context(self, personality_type: PersonalityType) -> Dict[str, Any]:
        """Get full context for a personality"""
        personality = self.personalities[personality_type]
        
        # Get recent interactions from other personalities
        other_personalities = [p for p in self.personalities.values() if p.personality_type != personality_type]
        recent_interactions = []
        
        for other_p in other_personalities:
            if other_p.conversation_history:
                recent_interactions.extend(other_p.conversation_history[-3:])  # Last 3 interactions
        
        return {
            "personality": {
                "name": personality.name,
                "role": personality.role,
                "description": personality.description,
                "active": personality.active,
                "tasks_assigned": personality.tasks_assigned,
                "last_activity": personality.last_activity.isoformat() if personality.last_activity else None
            },
            "recent_team_interactions": recent_interactions,
            "session_context": self.collaborative_session
        }
    
    def start_collaborative_session(self, topic: str, initial_request: str) -> str:
        """Start a new collaborative session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.collaborative_session = {
            "session_id": session_id,
            "topic": topic,
            "initial_request": initial_request,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "participants": [p.value for p in self.personalities.keys()]
        }
        
        # Log session start for all personalities
        for personality_type in self.personalities.keys():
            self.log_interaction(
                personality_type, 
                "session_start", 
                f"New collaborative session started: {topic}"
            )
        
        logger.info(f"Collaborative session started: {session_id}")
        return session_id


class MCPServer:
    """MCP Server implementing JSON-RPC 2.0 protocol"""
    
    def __init__(self):
        self.personality_manager = PersonalityManager()
        self.server_info = {
            "name": "multi-personality-ai",
            "version": "1.0.0"
        }
        logger.info("MCP Server initialized")
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "logging": {},
                "tools": {
                    "listChanged": True
                },
                "resources": {
                    "subscribe": True,
                    "listChanged": True
                }
            },
            "serverInfo": self.server_info
        }
    
    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        tools = [
            {
                "name": "start_collaborative_session",
                "description": "Start a new collaborative session with all personalities",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The main topic or project to work on"
                        },
                        "initial_request": {
                            "type": "string",
                            "description": "The initial request or problem to solve"
                        }
                    },
                    "required": ["topic", "initial_request"]
                }
            },
            {
                "name": "consult_personality",
                "description": "Consult a specific personality for their input",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "personality": {
                            "type": "string",
                            "enum": ["manager", "analyst", "creative", "critic", "implementer"],
                            "description": "The personality to consult"
                        },
                        "question": {
                            "type": "string",
                            "description": "The question or request for the personality"
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context for the question"
                        }
                    },
                    "required": ["personality", "question"]
                }
            },
            {
                "name": "get_team_consensus",
                "description": "Get consensus from all personalities on a specific topic",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to get consensus on"
                        },
                        "details": {
                            "type": "string",
                            "description": "Detailed description of the topic"
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "personality_feedback",
                "description": "Get feedback from personalities on a proposal or idea",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "proposal": {
                            "type": "string",
                            "description": "The proposal or idea to get feedback on"
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas to focus feedback on"
                        }
                    },
                    "required": ["proposal"]
                }
            },
            {
                "name": "assign_task",
                "description": "Assign a specific task to a personality",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "personality": {
                            "type": "string",
                            "enum": ["manager", "analyst", "creative", "critic", "implementer"],
                            "description": "The personality to assign the task to"
                        },
                        "task": {
                            "type": "string",
                            "description": "The task to assign"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Task priority level"
                        }
                    },
                    "required": ["personality", "task"]
                }
            },
            {
                "name": "get_personality_status",
                "description": "Get the current status of all personalities",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        return {"tools": tools}
    
    async def handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/list request"""
        resources = []
        
        # Personality states
        for personality_type, personality in self.personality_manager.personalities.items():
            resources.append({
                "uri": f"personality://{personality_type.value}",
                "name": f"{personality.name} - {personality.role}",
                "description": f"Access {personality.name}'s state, history, and capabilities",
                "mimeType": "application/json"
            })
        
        # Session information
        resources.extend([
            {
                "uri": "session://current",
                "name": "Current Collaborative Session",
                "description": "Information about the current collaborative session",
                "mimeType": "application/json"
            },
            {
                "uri": "session://history",
                "name": "Session History",
                "description": "Complete history of all interactions",
                "mimeType": "application/json"
            }
        ])
        
        return {"resources": resources}
    
    async def handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resources/read request"""
        uri = params.get("uri", "")
        
        if uri.startswith("personality://"):
            personality_type_str = uri.split("://")[1]
            try:
                personality_type = PersonalityType(personality_type_str)
                context = self.personality_manager.get_personality_context(personality_type)
                
                return {
                    "contents": [{
                        "type": "text",
                        "text": json.dumps(context, indent=2, default=str)
                    }]
                }
            except ValueError:
                return {
                    "contents": [{
                        "type": "text",
                        "text": f"Unknown personality type: {personality_type_str}"
                    }]
                }
        
        elif uri == "session://current":
            return {
                "contents": [{
                    "type": "text",
                    "text": json.dumps(self.personality_manager.collaborative_session, indent=2, default=str)
                }]
            }
        
        elif uri == "session://history":
            return {
                "contents": [{
                    "type": "text",
                    "text": json.dumps(self.personality_manager.session_history, indent=2, default=str)
                }]
            }
        
        else:
            return {
                "contents": [{
                    "type": "text",
                    "text": f"Unknown resource: {uri}"
                }]
            }
    
    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {name} with arguments: {arguments}")
        
        if name == "start_collaborative_session":
            topic = arguments.get("topic", "")
            initial_request = arguments.get("initial_request", "")
            
            session_id = self.personality_manager.start_collaborative_session(topic, initial_request)
            
            # Get initial response from manager
            manager_response = await self.get_personality_response(
                PersonalityType.MANAGER, 
                f"A new collaborative session has started. Topic: {topic}. Initial request: {initial_request}. Please coordinate the team response."
            )
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Collaborative session started (ID: {session_id})\n\n**Manager Response:**\n{manager_response}"
                }]
            }
        
        elif name == "consult_personality":
            personality_str = arguments.get("personality", "")
            question = arguments.get("question", "")
            context = arguments.get("context", "")
            
            try:
                personality_type = PersonalityType(personality_str)
                full_query = f"{question}\n\nContext: {context}" if context else question
                
                response = await self.get_personality_response(personality_type, full_query)
                
                return {
                    "content": [{
                        "type": "text",
                        "text": f"**{self.personality_manager.personalities[personality_type].name} ({self.personality_manager.personalities[personality_type].role}):**\n\n{response}"
                    }]
                }
            except ValueError:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown personality: {personality_str}"
                    }]
                }
        
        elif name == "get_team_consensus":
            topic = arguments.get("topic", "")
            details = arguments.get("details", "")
            
            full_query = f"Topic: {topic}\n\nDetails: {details}" if details else f"Topic: {topic}"
            
            responses = {}
            for personality_type in PersonalityType:
                response = await self.get_personality_response(
                    personality_type, 
                    f"Please provide your perspective on this topic for team consensus: {full_query}"
                )
                responses[personality_type.value] = response
            
            # Get final consensus from manager
            manager_consensus = await self.get_personality_response(
                PersonalityType.MANAGER,
                f"Based on all team input, please provide a final consensus on: {full_query}\n\nTeam responses: {json.dumps(responses, indent=2)}"
            )
            
            result_text = f"**Team Consensus on: {topic}**\n\n"
            for personality_type, response in responses.items():
                personality = self.personality_manager.personalities[PersonalityType(personality_type)]
                result_text += f"**{personality.name} ({personality.role}):**\n{response}\n\n"
            
            result_text += f"**Final Consensus (Manager):**\n{manager_consensus}"
            
            return {
                "content": [{
                    "type": "text",
                    "text": result_text
                }]
            }
        
        elif name == "personality_feedback":
            proposal = arguments.get("proposal", "")
            focus_areas = arguments.get("focus_areas", [])
            
            focus_text = f"\n\nPlease focus on: {', '.join(focus_areas)}" if focus_areas else ""
            full_query = f"Please provide feedback on this proposal: {proposal}{focus_text}"
            
            feedback_responses = {}
            for personality_type in PersonalityType:
                if personality_type != PersonalityType.MANAGER:  # Get feedback from all except manager first
                    response = await self.get_personality_response(personality_type, full_query)
                    feedback_responses[personality_type.value] = response
            
            # Manager reviews all feedback and provides final assessment
            manager_assessment = await self.get_personality_response(
                PersonalityType.MANAGER,
                f"Review all team feedback and provide final assessment on: {proposal}\n\nTeam feedback: {json.dumps(feedback_responses, indent=2)}"
            )
            
            result_text = f"**Feedback on Proposal:**\n{proposal}\n\n"
            for personality_type, response in feedback_responses.items():
                personality = self.personality_manager.personalities[PersonalityType(personality_type)]
                result_text += f"**{personality.name} ({personality.role}):**\n{response}\n\n"
            
            result_text += f"**Manager Assessment:**\n{manager_assessment}"
            
            return {
                "content": [{
                    "type": "text",
                    "text": result_text
                }]
            }
        
        elif name == "assign_task":
            personality_str = arguments.get("personality", "")
            task = arguments.get("task", "")
            priority = arguments.get("priority", "medium")
            
            try:
                personality_type = PersonalityType(personality_str)
                personality = self.personality_manager.personalities[personality_type]
                
                # Add task to personality's task list
                task_entry = f"[{priority.upper()}] {task}"
                personality.tasks_assigned.append(task_entry)
                
                # Log the task assignment
                self.personality_manager.log_interaction(
                    personality_type,
                    "task_assigned",
                    f"Task assigned: {task_entry}"
                )
                
                # Get acknowledgment from the personality
                response = await self.get_personality_response(
                    personality_type,
                    f"You have been assigned a new task: {task}. Priority: {priority}. Please acknowledge and provide your initial approach."
                )
                
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Task assigned to {personality.name}.\n\n**{personality.name}'s Response:**\n{response}"
                    }]
                }
            except ValueError:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown personality: {personality_str}"
                    }]
                }
        
        elif name == "get_personality_status":
            status_text = "**Personality Status Report**\n\n"
            
            for personality_type, personality in self.personality_manager.personalities.items():
                status_text += f"**{personality.name} ({personality.role}):**\n"
                status_text += f"- Status: {'Active' if personality.active else 'Inactive'}\n"
                status_text += f"- Assigned Tasks: {len(personality.tasks_assigned)}\n"
                status_text += f"- Conversation History: {len(personality.conversation_history)} interactions\n"
                status_text += f"- Last Activity: {personality.last_activity.strftime('%Y-%m-%d %H:%M:%S') if personality.last_activity else 'Never'}\n"
                
                if personality.tasks_assigned:
                    status_text += f"- Current Tasks:\n"
                    for task in personality.tasks_assigned[-3:]:  # Show last 3 tasks
                        status_text += f"  • {task}\n"
                
                status_text += "\n"
            
            # Add session information
            if self.personality_manager.collaborative_session:
                status_text += f"**Current Session:**\n"
                status_text += f"- Topic: {self.personality_manager.collaborative_session.get('topic', 'N/A')}\n"
                status_text += f"- Status: {self.personality_manager.collaborative_session.get('status', 'N/A')}\n"
                status_text += f"- Started: {self.personality_manager.collaborative_session.get('started_at', 'N/A')}\n"
            
            return {
                "content": [{
                    "type": "text",
                    "text": status_text
                }]
            }
        
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Unknown tool: {name}"
                }]
            }
    
    async def get_personality_response(self, personality_type: PersonalityType, query: str) -> str:
        """Generate a response from a specific personality"""
        
        # Get personality context
        context = self.personality_manager.get_personality_context(personality_type)
        personality = self.personality_manager.personalities[personality_type]
        
        # Log the interaction
        self.personality_manager.log_interaction(personality_type, "query", query)
        
        # For demo purposes, we'll create characteristic responses
        # In a real implementation, this would call an actual LLM API
        demo_response = self.generate_demo_response(personality_type, query, context)
        
        # Log the response
        self.personality_manager.log_interaction(personality_type, "response", demo_response)
        
        return demo_response
    
    def generate_demo_response(self, personality_type: PersonalityType, query: str, context: Dict[str, Any]) -> str:
        """Generate a demo response for each personality type"""
        
        personality = self.personality_manager.personalities[personality_type]
        
        if personality_type == PersonalityType.MANAGER:
            return f"""As the {personality.role}, I understand the request: "{query[:100]}..."

Let me coordinate our team approach:

1. **Analysis Phase**: Logic will examine the requirements and data
2. **Creative Phase**: Spark will generate innovative solutions
3. **Review Phase**: Guardian will assess quality and risks
4. **Implementation Phase**: Builder will create actionable plans

I'll monitor progress and ensure we deliver a comprehensive solution that meets all requirements. Each team member will provide their expertise, and I'll synthesize the final recommendation.

Next steps: Assigning specific tasks to each personality based on their strengths."""
        
        elif personality_type == PersonalityType.ANALYST:
            return f"""Looking at this request analytically: "{query[:100]}..."

**Key Analysis Points:**
- Data Requirements: Need to identify what information is available
- Risk Assessment: Potential challenges and mitigation strategies
- Success Metrics: How we'll measure effectiveness
- Resource Requirements: Time, tools, and expertise needed

**Logical Framework:**
1. Define the problem scope clearly
2. Gather relevant data and evidence
3. Identify patterns and relationships
4. Evaluate feasibility and constraints
5. Recommend evidence-based solutions

**Initial Concerns:**
- Need more specific requirements
- Should consider scalability factors
- Important to validate assumptions

I recommend we proceed with structured information gathering before moving to solution design."""
        
        elif personality_type == PersonalityType.CREATIVE:
            return f"""This is exciting! For "{query[:100]}...", I see amazing possibilities!

**Creative Opportunities:**
✨ **Innovation Potential**: We can approach this from unique angles
🎨 **User Experience**: Focus on making it intuitive and engaging
🚀 **Future-Forward**: Consider emerging trends and technologies
💡 **Out-of-the-Box**: Challenge conventional approaches

**Brainstorming Ideas:**
- Interactive elements that engage users
- Visual storytelling to communicate concepts
- Gamification elements to increase engagement
- AI-powered personalization features
- Community-driven components

**Design Thinking Approach:**
1. Empathize with end users
2. Define the core challenge creatively
3. Ideate multiple solution pathways
4. Prototype quick concepts
5. Test and iterate rapidly

Let's push boundaries and create something truly remarkable that users will love!"""
        
        elif personality_type == PersonalityType.CRITIC:
            return f"""Reviewing the request "{query[:100]}...", I have several quality concerns to address:

**Critical Review Points:**
⚠️ **Potential Issues:**
- Scope clarity needs improvement
- Risk factors require assessment
- Quality standards must be defined
- Testing procedures should be established

**Quality Assurance Checklist:**
□ Requirements are well-defined
□ Success criteria are measurable
□ Error handling is considered
□ Performance standards are set
□ Security implications are reviewed
□ Maintenance requirements are planned

**Constructive Feedback:**
- Need more specific deliverables
- Timeline should be realistic
- Resource allocation requires scrutiny
- Dependencies must be identified

**Recommendations for Improvement:**
1. Clarify ambiguous requirements
2. Establish quality gates
3. Define acceptance criteria
4. Plan for edge cases
5. Include rollback procedures

I'll monitor the project closely to ensure we maintain high standards throughout."""
        
        elif personality_type == PersonalityType.IMPLEMENTER:
            return f"""Ready to tackle "{query[:100]}..."! Let's make this happen.

**Implementation Strategy:**
🔧 **Technical Approach:**
- Break down into manageable tasks
- Identify required tools and technologies
- Set up development environment
- Create implementation timeline

**Action Plan:**
1. **Phase 1**: Requirements gathering and setup
2. **Phase 2**: Core functionality development
3. **Phase 3**: Testing and refinement
4. **Phase 4**: Deployment and documentation

**Practical Considerations:**
- Available resources and constraints
- Technology stack selection
- Integration requirements
- Performance optimization
- Error handling and logging

**Next Steps:**
- Set up project structure
- Begin core component development
- Implement testing framework
- Create deployment pipeline

**Delivery Focus:**
- Working solution first
- Iterative improvements
- User feedback integration
- Continuous optimization

Ready to start coding and building the solution immediately!"""
        
        return f"Response from {personality.name}: {query}"
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC request"""
        try:
            method = request.get("method", "")
            params = request.get("params", {})
            request_id = request.get("id")
            
            logger.info(f"Handling request: {method}")
            
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list(params)
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.error(traceback.format_exc())
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run(self):
        """Run the server"""
        logger.info("Starting MCP Server...")
        
        # Send server info
        server_info = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        print(json.dumps(server_info), flush=True)
        
        # Process requests
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                request = json.loads(line)
                response = await self.handle_request(request)
                
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                logger.error(traceback.format_exc())
                break


async def main():
    """Main function to start the server"""
    server = MCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())