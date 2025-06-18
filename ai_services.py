"""
AI Services for CodeVerse Online Judge
Integrates with free online AI APIs for code assistance
"""

import os
import requests
import json
from typing import Dict, List, Optional
from django.conf import settings

class AIServiceManager:
    """Manages multiple AI service providers with fallback support"""
    
    def __init__(self):
        self.huggingface_key = os.getenv('HUGGINGFACE_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.cohere_key = os.getenv('COHERE_API_KEY')
    
    def get_code_hint(self, problem_description: str, user_code: str, language: str) -> Dict:
        """Get a helpful hint for solving a coding problem"""
        prompt = f"""
        Problem: {problem_description}
        
        Current code ({language}):
        {user_code}
        
        Please provide a helpful hint (not the full solution) to guide the user toward solving this problem.
        Be encouraging and educational.
        """
        
        # Try Groq first (fastest)
        result = self._try_groq(prompt, "hint")
        if result:
            return result
            
        # Fallback to Hugging Face
        result = self._try_huggingface(prompt, "hint")
        if result:
            return result
            
        # Final fallback to Gemini
        return self._try_gemini(prompt, "hint")
    
    def get_problem_recommendation(self, user_level: str, solved_problems: List[str]) -> Dict:
        """Recommend next problems based on user progress"""
        prompt = f"""
        User level: {user_level}
        Previously solved problems: {', '.join(solved_problems) if solved_problems else 'None'}
        
        Recommend 3 coding problems that would be good for this user's next challenge.
        Consider their skill level and what they've already solved.
        """
        
        result = self._try_groq(prompt, "recommendation")
        if result:
            return result
            
        return self._try_huggingface(prompt, "recommendation")
    
    def chat_with_ai(self, user_message: str, context: str = "") -> Dict:
        """General chat interface for coding help"""
        prompt = f"""
        Context: {context}
        User question: {user_message}
        
        You are a helpful coding mentor. Provide clear, educational responses about programming and problem-solving.
        """
        
        result = self._try_groq(prompt, "chat")
        if result:
            return result
            
        return self._try_gemini(prompt, "chat")
    
    def _try_groq(self, prompt: str, request_type: str) -> Optional[Dict]:
        """Try Groq API (Llama 3 - very fast and free)"""
        if not self.groq_key:
            return None
            
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama3-8b-8192",  # Fast, free model
                "messages": [
                    {"role": "system", "content": "You are a helpful coding mentor and teaching assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "content": result["choices"][0]["message"]["content"],
                    "provider": "Groq (Llama 3)",
                    "type": request_type
                }
        except Exception as e:
            print(f"Groq API error: {e}")
            
        return None
    
    def _try_huggingface(self, prompt: str, request_type: str) -> Optional[Dict]:
        """Try Hugging Face Inference API"""
        if not self.huggingface_key:
            return None
            
        try:
            # Using a good free model for code
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            headers = {
                "Authorization": f"Bearer {self.huggingface_key}",
                "Content-Type": "application/json"
            }
            data = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 200,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                content = result[0].get("generated_text", "").replace(prompt, "").strip()
                return {
                    "success": True,
                    "content": content,
                    "provider": "Hugging Face",
                    "type": request_type
                }
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            
        return None
    
    def _try_gemini(self, prompt: str, request_type: str) -> Optional[Dict]:
        """Try Google Gemini API"""
        if not self.gemini_key:
            return None
            
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_key}"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "success": True,
                    "content": content,
                    "provider": "Google Gemini",
                    "type": request_type
                }
        except Exception as e:
            print(f"Gemini API error: {e}")
            
        return None

# Global instance
ai_service = AIServiceManager()
