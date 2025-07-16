"""
AI Views for CodeVerse Online Judge
Handles AI-powered features like hints, recommendations, and chat
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .ai_services import ai_service
from .models import Problem, Submission

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def get_ai_hint(request):
    """Get AI-powered hint for a specific problem"""
    try:
        data = json.loads(request.body)
        problem_id = data.get('problem_id')
        user_code = data.get('user_code', '')
        language = data.get('language', 'python')
        
        if not problem_id:
            return JsonResponse({'error': 'Problem ID required'}, status=400)
        
        try:
            problem = Problem.objects.get(id=problem_id)
        except Problem.DoesNotExist:
            return JsonResponse({'error': 'Problem not found'}, status=404)
        
        # Use 'statement' instead of 'description' if that's the correct field
        problem_description = getattr(problem, 'description', None) or getattr(problem, 'statement', None)
        if not problem_description:
            return JsonResponse({'error': "Problem object has no 'description' or 'statement' attribute"}, status=500)
        
        # Get AI hint
        result = ai_service.get_code_hint(
            problem_description=problem_description,
            user_code=user_code,
            language=language
        )
        
        if result and result.get('success'):
            return JsonResponse({
                'success': True,
                'hint': result['content'],
                'provider': result['provider']
            })
        else:
            return JsonResponse({
                'error': 'AI service temporarily unavailable. Please try again later.'
            }, status=503)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_ai_recommendations(request):
    """Get AI-powered problem recommendations"""
    try:
        # Get user's solved problems
        user_submissions = Submission.objects.filter(
            user=request.user, 
            verdict='Accepted'
        ).values_list('problem__title', flat=True)
        
        solved_problems = list(set(user_submissions))
        
        # Determine user level based on solved problems count
        solved_count = len(solved_problems)
        if solved_count == 0:
            user_level = "Beginner"
        elif solved_count < 10:
            user_level = "Intermediate"
        else:
            user_level = "Advanced"
        
        result = ai_service.get_problem_recommendation(
            user_level=user_level,
            solved_problems=solved_problems
        )
        
        if result and result.get('success'):
            return JsonResponse({
                'success': True,
                'recommendations': result['content'],
                'provider': result['provider'],
                'user_level': user_level,
                'solved_count': solved_count
            })
        else:
            return JsonResponse({
                'error': 'AI service temporarily unavailable. Please try again later.'
            }, status=503)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def ai_chat(request):
    """AI chat endpoint for general coding help"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message required'}, status=400)
        
        # Add context about CodeVerse
        context = """
        You are helping a user on CodeVerse Online Judge, a platform for practicing coding problems.
        Provide helpful, educational responses about programming, algorithms, and problem-solving.
        """
        
        result = ai_service.chat_with_ai(
            user_message=user_message,
            context=context
        )
        
        if result and result.get('success'):
            return JsonResponse({
                'success': True,
                'response': result['content'],
                'provider': result.get('provider', 'AI Assistant')
            })
        else:
            # Provide a helpful fallback response
            return JsonResponse({
                'success': True,
                'response': """I'm here to help with coding questions! 🤖

To unlock full AI capabilities with personalized responses:

🚀 **Quick Setup (2 minutes):**
1. Visit: https://console.groq.com/
2. Sign up (free, no credit card required)
3. Create an API key
4. Add to your .env file: `GROQ_API_KEY=your_key_here`
5. Restart the server

💡 **For now, try asking about:**
- "How do I solve array problems?"
- "Explain time complexity"
- "What's the best sorting algorithm?"
- "Binary search help"

What coding topic would you like to explore?""",
                'provider': 'Demo Assistant'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        print(f"Chat error: {e}")  # For debugging
        return JsonResponse({
            'success': True,
            'response': """Sorry, I encountered a technical issue! 😅

While I get back online, here are some general coding tips:

🎯 **Problem-Solving Steps:**
1. Understand the problem completely
2. Think of examples and edge cases
3. Plan your approach (algorithm)
4. Code step by step
5. Test with examples

🚀 **Common Patterns:**
- **Two Pointers**: For array problems
- **Hash Maps**: For fast lookups
- **Sliding Window**: For substring problems
- **DFS/BFS**: For tree/graph problems

Need help with a specific topic? Try asking again!""",
            'provider': 'Fallback Assistant'
        }, status=200)
