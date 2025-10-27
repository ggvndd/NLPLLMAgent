"""
Ollama LLM Client for Career Coach Agent

This module provides an async interface to interact with Ollama's local LLM API.
Supports chat completions with structured prompts for career coaching tasks.
"""

import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
import logging
from utils.logger import setup_logger


class OllamaClient:
    """
    Async client for Ollama local LLM API.
    
    Features:
    - Chat completions with customizable models
    - Structured prompt formatting for career coaching
    - Error handling and retry logic
    - Performance monitoring
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (default: localhost:11434)
            model: Model name to use (default: llama3.1:8b)
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.logger = setup_logger(__name__)
        self._session = None
        
        self.logger.info(f"Initialized Ollama client - Model: {model}, URL: {base_url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def health_check(self) -> bool:
        """
        Check if Ollama service is running and responsive.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    self.logger.info(f"Ollama health check passed. Available models: {models}")
                    return self.model in models
                else:
                    self.logger.warning(f"Ollama health check failed: HTTP {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Ollama health check error: {e}")
            return False
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generate text completion using Ollama.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system message for context
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            # Prepare the request payload
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "num_predict": kwargs.get("max_tokens", 2000),
                }
            }
            
            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt
            
            # Remove None values
            payload["options"] = {k: v for k, v in payload["options"].items() if v is not None}
            
            self.logger.debug(f"Sending request to Ollama: {self.model}")
            
            session = await self._get_session()
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)  # Increased timeout for complex requests
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error (HTTP {response.status}): {error_text}")
                
                data = await response.json()
                
                # Extract the response content
                if "response" in data:
                    response_text = data["response"]
                    self.logger.info(f"Generated response ({len(response_text)} chars)")
                    return response_text.strip()
                else:
                    raise Exception(f"Unexpected response format: {data}")
                    
        except asyncio.TimeoutError:
            self.logger.error("Ollama request timed out")
            raise Exception("Request to Ollama timed out")
        except Exception as e:
            self.logger.error(f"Ollama generation error: {e}")
            raise
    
    async def generate_career_analysis(self, prompt: str) -> str:
        """
        Generate career analysis with optimized system prompt.
        
        Args:
            prompt: Career analysis prompt
            
        Returns:
            Structured JSON response for career recommendations
        """
        system_prompt = """You are an expert career coach AI with deep knowledge of:
- Job market trends and salary data
- Skills requirements across industries
- Career progression paths
- Resume optimization
- Interview best practices

Provide detailed, actionable advice in structured JSON format.
Be specific with salary ranges, skill requirements, and career paths.
Focus on practical next steps the user can take immediately."""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
    
    async def generate_resume_review(self, prompt: str) -> str:
        """
        Generate resume review with specialized system prompt.
        
        Args:
            prompt: Resume review prompt
            
        Returns:
            Structured JSON response with resume feedback
        """
        system_prompt = """You are a professional resume reviewer with expertise in:
- ATS (Applicant Tracking System) optimization
- Industry-specific resume formats
- Keyword optimization
- Achievement quantification
- Modern hiring practices

Provide constructive feedback in JSON format with:
- Numerical scores (0-100)
- Specific improvement suggestions
- Industry keywords to include
- Formatting recommendations"""

        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=1500
        )
    
    async def generate_interview_questions(self, role: str) -> str:
        """
        Generate interview questions for a specific role.
        
        Args:
            role: Target job role
            
        Returns:
            JSON array of interview questions
        """
        system_prompt = f"""You are an experienced hiring manager creating interview questions for a {role} position.

Generate 8-10 diverse questions including:
- Behavioral questions (STAR method)
- Technical/skill-based questions
- Situational problem-solving
- Culture fit assessment

Return as a JSON array of strings."""

        prompt = f"Generate comprehensive interview questions for a {role} position."
        
        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=1000
        )
    
    async def list_models(self) -> list:
        """
        List available models on the Ollama server.
        
        Returns:
            List of model names
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model["name"] for model in data.get("models", [])]
                    self.logger.info(f"Available models: {models}")
                    return models
                else:
                    self.logger.error(f"Failed to list models: HTTP {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []
    
    async def close(self):
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None


# Utility functions for easy integration
async def test_ollama_connection(model: str = "llama3.1:8b") -> bool:
    """
    Test Ollama connection and model availability.
    
    Args:
        model: Model name to test
        
    Returns:
        True if connection successful, False otherwise
    """
    async with OllamaClient(model=model) as client:
        return await client.health_check()


async def quick_chat(prompt: str, model: str = "llama3.1:8b") -> str:
    """
    Quick chat completion for testing.
    
    Args:
        prompt: User prompt
        model: Model to use
        
    Returns:
        Generated response
    """
    async with OllamaClient(model=model) as client:
        return await client.generate(prompt)


# CLI test function
async def main():
    """Test Ollama client functionality."""
    print("🤖 Testing Ollama Client")
    print("=" * 30)
    
    # Test connection
    print("\n1. Testing connection...")
    if await test_ollama_connection():
        print("✅ Ollama connection successful!")
    else:
        print("❌ Ollama connection failed!")
        return
    
    # Test quick generation
    print("\n2. Testing text generation...")
    async with OllamaClient() as client:
        response = await client.generate(
            "What are the top 3 skills needed for a software engineer in 2025? Be concise."
        )
        print(f"Response: {response}")
        
        # Test career analysis
        print("\n3. Testing career analysis...")
        career_prompt = """
        Analyze career opportunities for someone with these skills: Python, SQL, Excel, 2 years experience.
        Return JSON with 2 job recommendations including match percentage, salary range, and skill gaps.
        """
        career_response = await client.generate_career_analysis(career_prompt)
        print(f"Career Analysis: {career_response[:200]}...")
    
    print("\n✅ Ollama client test completed!")


if __name__ == "__main__":
    asyncio.run(main())