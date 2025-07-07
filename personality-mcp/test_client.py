#!/usr/bin/env python3
"""
Test client for the Multi-Personality MCP Server

This script demonstrates how to interact with the MCP server
and test its various functionalities.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, Optional


class MCPTestClient:
    """Simple test client for the MCP server"""
    
    def __init__(self, server_script: str = "mcp_personality_server.py"):
        self.server_script = server_script
        self.server_process = None
        self.request_id = 1
    
    def get_next_id(self) -> int:
        """Get next request ID"""
        current_id = self.request_id
        self.request_id += 1
        return current_id
    
    async def start_server(self):
        """Start the MCP server process"""
        self.server_process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("🚀 MCP Server started")
        
        # Wait for initialization
        await asyncio.sleep(1)
    
    async def stop_server(self):
        """Stop the MCP server process"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            print("🛑 MCP Server stopped")
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Send a request to the MCP server"""
        if not self.server_process or not self.server_process.stdin or not self.server_process.stdout:
            raise RuntimeError("Server not started or stdin/stdout not available")
        
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
                response = json.loads(response_line.decode().strip())
                return response
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                return None
        return None
    
    async def test_initialization(self):
        """Test server initialization"""
        print("\n🔧 Testing server initialization...")
        
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        })
        
        if response and "result" in response:
            print("✅ Server initialized successfully")
            print(f"   Server: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
            return True
        else:
            print("❌ Server initialization failed")
            return False
    
    async def test_tools_list(self):
        """Test listing available tools"""
        print("\n📋 Testing tools list...")
        
        response = await self.send_request("tools/list")
        
        if response and "result" in response:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            return True
        else:
            print("❌ Failed to list tools")
            return False
    
    async def test_resources_list(self):
        """Test listing available resources"""
        print("\n📊 Testing resources list...")
        
        response = await self.send_request("resources/list")
        
        if response and "result" in response:
            resources = response["result"]["resources"]
            print(f"✅ Found {len(resources)} resources:")
            for resource in resources:
                print(f"   - {resource['name']}: {resource['description']}")
            return True
        else:
            print("❌ Failed to list resources")
            return False
    
    async def test_personality_consultation(self):
        """Test consulting a specific personality"""
        print("\n🎭 Testing personality consultation...")
        
        response = await self.send_request("tools/call", {
            "name": "consult_personality",
            "arguments": {
                "personality": "creative",
                "question": "How can we make our user interface more engaging and user-friendly?",
                "context": "We're building a task management application"
            }
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Creative personality consultation successful")
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("❌ Failed to consult personality")
            return False
    
    async def test_team_consensus(self):
        """Test getting team consensus"""
        print("\n🤝 Testing team consensus...")
        
        response = await self.send_request("tools/call", {
            "name": "get_team_consensus",
            "arguments": {
                "topic": "Technology stack selection",
                "details": "Should we use React or Vue.js for our frontend framework?"
            }
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Team consensus successful")
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("❌ Failed to get team consensus")
            return False
    
    async def test_task_assignment(self):
        """Test assigning a task to a personality"""
        print("\n📋 Testing task assignment...")
        
        response = await self.send_request("tools/call", {
            "name": "assign_task",
            "arguments": {
                "personality": "implementer",
                "task": "Create a RESTful API endpoint for user authentication",
                "priority": "high"
            }
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Task assignment successful")
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("❌ Failed to assign task")
            return False
    
    async def test_personality_status(self):
        """Test getting personality status"""
        print("\n📊 Testing personality status...")
        
        response = await self.send_request("tools/call", {
            "name": "get_personality_status",
            "arguments": {}
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Personality status retrieval successful")
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("❌ Failed to get personality status")
            return False
    
    async def test_collaborative_session(self):
        """Test starting a collaborative session"""
        print("\n🚀 Testing collaborative session...")
        
        response = await self.send_request("tools/call", {
            "name": "start_collaborative_session",
            "arguments": {
                "topic": "New Product Development",
                "initial_request": "We need to design and develop a new mobile app for task management. Please coordinate the team approach."
            }
        })
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print("✅ Collaborative session started successfully")
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("❌ Failed to start collaborative session")
            return False
    
    async def test_resource_access(self):
        """Test accessing personality resource"""
        print("\n📖 Testing resource access...")
        
        response = await self.send_request("resources/read", {
            "uri": "personality://manager"
        })
        
        if response and "result" in response:
            content = response["result"]["contents"][0]["text"]
            print("✅ Resource access successful")
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("❌ Failed to access resource")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting MCP Server Tests")
        print("=" * 50)
        
        try:
            await self.start_server()
            
            tests = [
                ("Initialization", self.test_initialization),
                ("Tools List", self.test_tools_list),
                ("Resources List", self.test_resources_list),
                ("Personality Consultation", self.test_personality_consultation),
                ("Team Consensus", self.test_team_consensus),
                ("Task Assignment", self.test_task_assignment),
                ("Personality Status", self.test_personality_status),
                ("Collaborative Session", self.test_collaborative_session),
                ("Resource Access", self.test_resource_access)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                try:
                    success = await test_func()
                    if success:
                        passed += 1
                except Exception as e:
                    print(f"❌ {test_name} failed with error: {e}")
            
            print("\n" + "=" * 50)
            print(f"🏁 Test Results: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All tests passed! The MCP server is working correctly.")
            else:
                print(f"⚠️  {total - passed} tests failed. Check the logs for details.")
        
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
        
        finally:
            await self.stop_server()


async def main():
    """Main test function"""
    client = MCPTestClient()
    await client.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())