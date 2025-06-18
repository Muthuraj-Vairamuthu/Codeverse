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
        
        # Check if any API keys are configured
        if not any([self.huggingface_key, self.groq_key, self.gemini_key, self.cohere_key]):
            return {
                "success": True,
                "content": f"""🤖 Welcome to AI-Powered Hints!

To unlock intelligent code hints, you'll need a FREE API key from one of these services:

🚀 **Quick Setup (2 minutes):**
1. Visit https://console.groq.com/ (recommended - super fast!)
2. Sign up with email (no credit card needed)
3. Create an API key
4. Add it to your .env file as: GROQ_API_KEY=your_key_here
5. Restart the server

💡 **For now, here's a general hint for {language} problems:**
- Break the problem into smaller steps
- Think about the input and expected output
- Consider edge cases (empty input, single element, etc.)
- Use appropriate data structures for the problem type
- Test with the provided examples first

Check the AI_SETUP_GUIDE.md file for detailed instructions!""",
                "provider": "Setup Guide",
                "type": "hint"
            }
        
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
        
        # Check if any API keys are configured
        if not any([self.huggingface_key, self.groq_key, self.gemini_key, self.cohere_key]):
            return {
                "success": True,
                "content": f"""🎯 **Personalized Recommendations for {user_level} Level**

📊 **Your Progress:** {len(solved_problems)} problems solved

🚀 **To unlock AI-powered recommendations:**
1. Get a free API key from https://console.groq.com/
2. Add to .env: GROQ_API_KEY=your_key_here
3. Restart server

💡 **General recommendations for {user_level} level:**

🟢 **If you're a Beginner:**
- Start with basic array problems (Two Sum, Find Maximum)
- Practice string manipulation problems
- Learn about loops and conditionals
- Try easy math problems

🟡 **If you're Intermediate:**
- Dive into sorting and searching algorithms
- Practice with hash maps and sets
- Try medium difficulty problems
- Learn about recursion and dynamic programming basics

🔴 **If you're Advanced:**
- Challenge yourself with hard algorithmic problems
- Practice system design concepts
- Explore advanced data structures (graphs, trees)
- Try competitive programming problems

Check out the problems list and pick ones that match your comfort level!""",
                "provider": "Setup Guide",
                "type": "recommendation"
            }
            
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
        
        # Check if any API keys are configured
        if not any([self.huggingface_key, self.groq_key, self.gemini_key, self.cohere_key]):
            # Provide helpful responses based on common questions
            user_lower = user_message.lower()
            
            if any(word in user_lower for word in ['time', 'complexity', 'big o', 'algorithm']):
                response = """🎯 **Time Complexity Guide**

Time complexity measures how execution time grows with input size:

• **O(1)** - Constant: Hash table lookup, array access
• **O(log n)** - Logarithmic: Binary search, balanced tree operations  
• **O(n)** - Linear: Single loop through array
• **O(n log n)** - Log-linear: Merge sort, heap sort
• **O(n²)** - Quadratic: Nested loops, bubble sort
• **O(2ⁿ)** - Exponential: Recursive solutions (avoid when possible!)

💡 **Pro tip:** Always analyze your loops and recursive calls to determine complexity!

🚀 **Setup AI for personalized help:** Get a free API key from https://console.groq.com/"""
            
            elif any(word in user_lower for word in ['sort', 'sorting']):
                response = """🔄 **Sorting Algorithms Cheat Sheet**

**Quick Reference:**
• **Bubble Sort**: O(n²) - Simple but slow, good for learning
• **Merge Sort**: O(n log n) - Stable, consistent performance
• **Quick Sort**: O(n log n) avg - Fast in practice, unstable
• **Heap Sort**: O(n log n) - In-place, not stable

**When to use:**
- **Small arrays (<50)**: Insertion sort
- **Nearly sorted**: Bubble sort or insertion sort
- **General purpose**: Quick sort or merge sort
- **Guaranteed performance**: Heap sort or merge sort

🎯 **Try implementing merge sort - it's a great interview favorite!**"""
            
            elif any(word in user_lower for word in ['binary', 'search']):
                response = """🔍 **Binary Search Mastery**

**The Algorithm:**
1. Start with low=0, high=len(array)-1
2. While low <= high:
   - mid = (low + high) // 2
   - If target == array[mid]: Found it!
   - If target < array[mid]: high = mid - 1
   - If target > array[mid]: low = mid + 1

**Key Points:**
• Array MUST be sorted first
• Time complexity: O(log n)
• Space complexity: O(1) iterative, O(log n) recursive

**Common Variations:**
- Find first/last occurrence
- Search in rotated sorted array
- Find peak element

💡 **Remember:** Binary search eliminates half the search space each step!"""
            
            elif any(word in user_lower for word in ['help', 'start', 'begin']):
                response = """👋 **Welcome to CodeVerse AI Assistant!**

I can help you with:
• 🧮 **Algorithms & Data Structures**
• ⚡ **Time/Space Complexity Analysis**  
• 🐛 **Debugging Tips & Strategies**
• 💡 **Problem-Solving Approaches**
• 📚 **Concept Explanations**

**Popular Topics:**
- Arrays, Linked Lists, Trees, Graphs
- Sorting & Searching algorithms
- Dynamic Programming basics
- Hash tables and maps

🤖 **Want personalized AI help?** 
1. Get free API key: https://console.groq.com/
2. Add to .env: GROQ_API_KEY=your_key
3. Restart server and enjoy full AI features!

What coding topic interests you most?"""
            
            else:
                response = f"""🤖 **AI Assistant (Demo Mode)**

I noticed you asked: "{user_message}"

I'd love to give you a personalized response! To unlock full AI capabilities:

🚀 **Quick Setup (2 minutes):**
1. Visit: https://console.groq.com/
2. Sign up (free, no credit card)
3. Create API key
4. Add to .env: GROQ_API_KEY=your_key_here
5. Restart server

💡 **For now, try asking about:**
- "Time complexity help"
- "Sorting algorithms"
- "Binary search explanation"
- "How to start coding"

Check out the AI_SETUP_GUIDE.md for detailed instructions!"""
            
            return {
                "success": True,
                "content": response,
                "provider": "Demo Assistant",
                "type": "chat"
            }
        
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
