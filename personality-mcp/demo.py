#!/usr/bin/env python3
"""
Demo script for Multi-Personality MCP Server

This script demonstrates the collaborative personality system in action
with a realistic project scenario.
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Dict, Any, Optional


class PersonalityDemo:
    """Demo class to showcase the personality system"""
    
    def __init__(self):
        self.server_process = None
        self.request_id = 1
    
    def get_next_id(self) -> int:
        """Get next request ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    async def start_server(self):
        """Start the MCP server"""
        print("🚀 Starting Multi-Personality MCP Server...")
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, "mcp_personality_server.py",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Give server time to initialize
        await asyncio.sleep(2)
        print("✅ Server started successfully")
    
    async def stop_server(self):
        """Stop the MCP server"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            print("🛑 Server stopped")
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Send request to MCP server"""
        if not self.server_process or not self.server_process.stdin or not self.server_process.stdout:
            raise RuntimeError("Server not available")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_json.encode())
        await self.server_process.stdin.drain()
        
        # Read response
        response_line = await self.server_process.stdout.readline()
        if response_line:
            try:
                return json.loads(response_line.decode().strip())
            except json.JSONDecodeError:
                return None
        return None
    
    def print_separator(self, title: str):
        """Print a formatted separator"""
        print(f"\n{'='*60}")
        print(f"🎭 {title}")
        print(f"{'='*60}")
    
    def print_personality_response(self, personality_name: str, response: str):
        """Print a personality response with formatting"""
        print(f"\n💬 **{personality_name}** says:")
        print("-" * 50)
        print(response)
        print("-" * 50)
    
    async def demo_project_planning(self):
        """Demo: Project planning scenario"""
        self.print_separator("DEMO: New E-commerce Project Planning")
        
        print("🎯 Scenario: A startup wants to build a new e-commerce platform")
        print("🎭 Let's see how our AI personalities collaborate...")
        
        # Initialize server
        await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "demo-client", "version": "1.0.0"}
        })
        
        # Start collaborative session
        print("\n🚀 Starting collaborative session...")
        response = await self.send_request("tools/call", {
            "name": "start_collaborative_session",
            "arguments": {
                "topic": "E-commerce Platform Development",
                "initial_request": "We need to build a modern e-commerce platform that can handle high traffic, provide excellent user experience, and be scalable for future growth."
            }
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(content)
        
        await asyncio.sleep(2)
        
        # Consult each personality
        personalities = [
            ("analyst", "What are the key technical requirements and risks we should consider?"),
            ("creative", "How can we make the user experience exceptional and engaging?"),
            ("critic", "What potential problems should we be aware of in this project?"),
            ("implementer", "What's the best technical approach for building this platform?")
        ]
        
        for personality, question in personalities:
            print(f"\n🤔 Consulting {personality.title()}...")
            response = await self.send_request("tools/call", {
                "name": "consult_personality",
                "arguments": {
                    "personality": personality,
                    "question": question,
                    "context": "E-commerce platform for startup, needs to be scalable and user-friendly"
                }
            })
            
            if response and "result" in response:
                content = response["result"]["content"][0]["text"]
                # Extract personality name from response
                lines = content.split('\n')
                if lines:
                    personality_header = lines[0].replace('**', '').replace(':', '')
                    personality_response = '\n'.join(lines[2:]) if len(lines) > 2 else content
                    self.print_personality_response(personality_header, personality_response)
            
            await asyncio.sleep(1)
        
        # Get team consensus
        print("\n🤝 Getting team consensus on technology stack...")
        response = await self.send_request("tools/call", {
            "name": "get_team_consensus",
            "arguments": {
                "topic": "Technology Stack Selection",
                "details": "Should we use React + Node.js + MongoDB or Vue.js + Python + PostgreSQL for our e-commerce platform?"
            }
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(content)
        
        await asyncio.sleep(2)
        
        # Assign tasks
        print("\n📋 Assigning tasks to personalities...")
        tasks = [
            ("analyst", "Create detailed technical requirements document", "high"),
            ("creative", "Design user interface mockups and user journey", "high"),
            ("critic", "Review and test the initial prototypes", "medium"),
            ("implementer", "Set up development environment and basic architecture", "high")
        ]
        
        for personality, task, priority in tasks:
            print(f"\n📝 Assigning task to {personality.title()}...")
            response = await self.send_request("tools/call", {
                "name": "assign_task",
                "arguments": {
                    "personality": personality,
                    "task": task,
                    "priority": priority
                }
            })
            
            if response and "result" in response:
                content = response["result"]["content"][0]["text"]
                print(f"✅ Task assigned: {content.split('Response:')[0] if 'Response:' in content else content[:100]}...")
        
        # Check status
        print("\n📊 Checking personality status...")
        response = await self.send_request("tools/call", {
            "name": "get_personality_status",
            "arguments": {}
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(content)
        
        self.print_separator("DEMO COMPLETED")
        print("🎉 The Multi-Personality AI system has successfully collaborated!")
        print("🔍 Key benefits demonstrated:")
        print("   • Multiple perspectives on the same problem")
        print("   • Specialized expertise from each personality")
        print("   • Collaborative decision-making process")
        print("   • Task assignment and tracking")
        print("   • Comprehensive project planning")
        print("\n💡 This system helps ensure thorough analysis and well-rounded solutions!")
    
    async def run_demo(self):
        """Run the complete demo"""
        try:
            await self.start_server()
            await self.demo_project_planning()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
        finally:
            await self.stop_server()


async def main():
    """Main demo function"""
    print("🎭 Multi-Personality MCP Server Demo")
    print("=" * 60)
    print("This demo shows how multiple AI personalities")
    print("collaborate to solve complex problems together.")
    print("=" * 60)
    
    demo = PersonalityDemo()
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())