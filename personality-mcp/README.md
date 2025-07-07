# Multi-Personality MCP Server

A Model Context Protocol (MCP) server that implements multiple AI personalities working together collaboratively. This server features 5 different personalities with distinct roles:

## 🎭 The Personalities

### 1. **Director** (Manager)
- **Role**: Project Manager & Coordinator
- **Responsibilities**: Oversees all operations, coordinates between personalities, makes final decisions
- **Style**: Professional, decisive, diplomatic

### 2. **Logic** (Analyst)
- **Role**: Data Analyst & Strategic Thinker
- **Responsibilities**: Logical analysis, data interpretation, risk assessment, strategic planning
- **Style**: Logical, precise, evidence-based

### 3. **Spark** (Creative)
- **Role**: Creative Innovator & Solution Designer
- **Responsibilities**: Generates innovative ideas, creative solutions, user experience focus
- **Style**: Imaginative, inspiring, enthusiastic

### 4. **Guardian** (Critic)
- **Role**: Quality Assurance & Process Optimizer
- **Responsibilities**: Identifies flaws, provides constructive criticism, ensures quality standards
- **Style**: Constructive, thorough, quality-focused

### 5. **Builder** (Implementer)
- **Role**: Implementation Specialist & Problem Solver
- **Responsibilities**: Practical implementation, technical execution, hands-on problem solving
- **Style**: Practical, action-oriented, solution-focused

## 🚀 Features

- **Collaborative Decision Making**: Multiple personalities provide different perspectives
- **Task Assignment**: Assign specific tasks to appropriate personalities
- **Team Consensus**: Get unified opinions from all personalities
- **Feedback System**: Comprehensive feedback on proposals and ideas
- **Session Management**: Track collaborative sessions and history
- **Resource Access**: Query personality states and session information

## 📋 Available Tools

### 1. **start_collaborative_session**
Start a new collaborative session with all personalities
```json
{
  "topic": "Project planning for new feature",
  "initial_request": "We need to plan a new user authentication system"
}
```

### 2. **consult_personality**
Consult a specific personality for their input
```json
{
  "personality": "analyst",
  "question": "What are the security risks of this approach?",
  "context": "We're implementing OAuth2 authentication"
}
```

### 3. **get_team_consensus**
Get consensus from all personalities on a topic
```json
{
  "topic": "Technology stack selection",
  "details": "Should we use React or Vue for the frontend?"
}
```

### 4. **personality_feedback**
Get feedback from personalities on a proposal
```json
{
  "proposal": "Implement microservices architecture",
  "focus_areas": ["scalability", "maintenance", "cost"]
}
```

### 5. **assign_task**
Assign a specific task to a personality
```json
{
  "personality": "implementer",
  "task": "Create API endpoint for user registration",
  "priority": "high"
}
```

### 6. **get_personality_status**
Get current status of all personalities
```json
{}
```

## 🔧 Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python mcp_personality_server.py
```

## 💡 Usage Examples

### Basic Consultation
```bash
# Consult the Creative personality
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "consult_personality", "arguments": {"personality": "creative", "question": "How can we make our login page more engaging?"}}}' | python mcp_personality_server.py
```

### Team Consensus
```bash
# Get team consensus on a decision
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_team_consensus", "arguments": {"topic": "Database choice", "details": "Should we use PostgreSQL or MongoDB for our user data?"}}}' | python mcp_personality_server.py
```

### Session Management
```bash
# Start a collaborative session
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "start_collaborative_session", "arguments": {"topic": "New Product Launch", "initial_request": "Plan the launch strategy for our new mobile app"}}}' | python mcp_personality_server.py
```

## 📊 Resources

The server provides several resources for accessing personality and session information:

- **personality://[personality_type]**: Access individual personality states
- **session://current**: Current collaborative session information
- **session://history**: Complete interaction history

## 🔍 Monitoring

The server logs all activities to `mcp_server.log` for debugging and monitoring purposes.

## 🛠️ Configuration

The server runs on stdio by default (MCP standard). All personalities are initialized automatically when the server starts.

## 📝 Example Workflow

1. **Start a session**: Begin with `start_collaborative_session`
2. **Consult personalities**: Use `consult_personality` for specific expertise
3. **Get feedback**: Use `personality_feedback` for proposal evaluation
4. **Assign tasks**: Use `assign_task` for implementation
5. **Check status**: Use `get_personality_status` to monitor progress

## 🧪 Testing

The server includes demo responses for each personality type. In a production environment, you would integrate with actual LLM APIs to generate dynamic responses.

## 🤝 Contributing

This is a demonstration MCP server. To extend it:

1. Add new personality types to the `PersonalityType` enum
2. Implement corresponding response generation logic
3. Add new tools for additional functionality
4. Integrate with real LLM APIs for dynamic responses

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🔗 MCP Protocol

This server implements the Model Context Protocol (MCP) specification, making it compatible with MCP clients like Claude Desktop, N8N, and other MCP-compatible tools.

For more information about MCP, visit the [MCP Documentation](https://modelcontextprotocol.io/).
