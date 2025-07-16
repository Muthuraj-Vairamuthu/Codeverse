from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Problem, Submission, TestCase
from .utils import run_code
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

def problem_list(request):
    problems = Problem.objects.all()
    
    # Get filter parameters (support multiple values)
    difficulties = request.GET.getlist('difficulty')
    company = request.GET.get('company')
    tags = request.GET.getlist('tags')
    search = request.GET.get('search')
    
    # Apply filters
    if difficulties:
        problems = problems.filter(difficulty__in=difficulties)
    if company:
        problems = problems.filter(company=company)
    if tags:
        # Filter problems that contain any of the selected tags
        tag_filter = None
        for tag in tags:
            if tag_filter is None:
                tag_filter = problems.filter(tags__icontains=tag)
            else:
                tag_filter = tag_filter | problems.filter(tags__icontains=tag)
        if tag_filter is not None:
            problems = tag_filter.distinct()
    if search:
        problems = problems.filter(title__icontains=search)
    
    # Get filter options for the UI
    companies = ['Google', 'Meta', 'Amazon', 'Microsoft', 'Apple', 'Netflix']
    all_tags = set()
    for problem in Problem.objects.all():
        if problem.tags:
            all_tags.update([tag.strip() for tag in problem.tags.split(',')])
    all_tags = sorted(list(all_tags))
    
    context = {
        'problems': problems,
        'companies': companies,
        'tags': all_tags,
        'selected_difficulties': difficulties,
        'selected_company': company,
        'selected_tags': tags,
    }
    
    return render(request, "problems/problem_list.html", context)

@login_required
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    if request.method == 'POST':
        code = request.POST['code']
        language = request.POST['language']
        Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            verdict="Pending"
        )
        messages.success(request, "Your submission was received! Verdict: Pending")
        return redirect('problem_detail', problem_id=problem_id)

    return render(request, "problems/problem_detail.html", {"problem": problem})

@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(user=request.user).order_by('-submitted_at')
    return render(request, 'problems/my_submissions.html', {'submissions': submissions})

@csrf_exempt
@login_required
def run_submission(request, problem_id):
    """Run code against test cases (for testing purposes)"""
    problem = get_object_or_404(Problem, pk=problem_id)
    if request.method == "POST":
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")
        
        # Run against all test cases
        all_passed = True
        results = []
        
        test_cases = problem.testcases.all()
        
        for i, test in enumerate(test_cases, 1):
            try:
                output = run_code(code, test.input_data, language)
                passed = output.strip() == test.expected_output.strip()
                
                results.append({
                    "input": test.input_data,
                    "expected": test.expected_output,
                    "actual": output.strip(),
                    "passed": passed
                })
                
                if not passed:
                    all_passed = False
            except Exception as e:
                results.append({
                    "input": test.input_data,
                    "expected": test.expected_output,
                    "actual": f"Error: {str(e)}",
                    "passed": False
                })
                all_passed = False
        
        return render(request, "problems/modal_results.html", {
            "problem": problem,
            "code": code,
            "language": language,
            "results": results,
            "all_passed": all_passed,
            "is_submission": False
        })

@csrf_exempt
@login_required
def submit_solution(request, problem_id):
    """Submit solution for official evaluation"""
    problem = get_object_or_404(Problem, pk=problem_id)
    if request.method == "POST":
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")
        
        # Run against all test cases
        all_passed = True
        results = []
        
        test_cases = problem.testcases.all()
        
        for i, test in enumerate(test_cases, 1):
            try:
                output = run_code(code, test.input_data, language)
                passed = output.strip() == test.expected_output.strip()
                
                results.append({
                    "input": test.input_data,
                    "expected": test.expected_output,
                    "actual": output.strip(),
                    "passed": passed
                })
                
                if not passed:
                    all_passed = False
            except Exception as e:
                results.append({
                    "input": test.input_data,
                    "expected": test.expected_output,
                    "actual": f"Error: {str(e)}",
                    "passed": False
                })
                all_passed = False

        # Create submission entry
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
            verdict="Accepted" if all_passed else "Wrong Answer"
        )
        
        # Redirect to submissions with success message
        if all_passed:
            messages.success(request, f"🎉 Solution Accepted! Your solution passed all test cases.")
        else:
            passed_count = len([r for r in results if r['passed']])
            total_count = len(results)
            messages.warning(request, f"❌ Wrong Answer. {passed_count}/{total_count} test cases passed.")
        
        # Redirect to submissions page
        return redirect('my_submissions')

@staff_member_required
def admin_problems(request):
    """Admin view to manage problems"""
    problems = Problem.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(problems, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'problems/admin_problems.html', {
        'page_obj': page_obj,
        'problems': page_obj
    })

@staff_member_required
def admin_create_problem(request):
    """Create a new problem"""
    if request.method == 'POST':
        try:
            problem = Problem.objects.create(
                title=request.POST['title'],
                statement=request.POST['statement'],
                input_format=request.POST['input_format'],
                output_format=request.POST['output_format'],
                sample_input=request.POST['sample_input'],
                sample_output=request.POST['sample_output'],
                difficulty=request.POST['difficulty'],
                company=request.POST.get('company', 'Other'),
                tags=request.POST.get('tags', '')
            )
            messages.success(request, f'Problem "{problem.title}" created successfully!')
            return redirect('admin_problems')
        except Exception as e:
            messages.error(request, f'Error creating problem: {str(e)}')
    
    return render(request, 'problems/admin_create_problem.html', {
        'difficulties': Problem.DIFFICULTY_CHOICES,
        'companies': Problem.COMPANY_CHOICES
    })

@staff_member_required
def admin_edit_problem(request, problem_id):
    """Edit an existing problem"""
    problem = get_object_or_404(Problem, id=problem_id)
    
    if request.method == 'POST':
        try:
            problem.title = request.POST['title']
            problem.statement = request.POST['statement']
            problem.input_format = request.POST['input_format']
            problem.output_format = request.POST['output_format']
            problem.sample_input = request.POST['sample_input']
            problem.sample_output = request.POST['sample_output']
            problem.difficulty = request.POST['difficulty']
            problem.company = request.POST.get('company', 'Other')
            problem.tags = request.POST.get('tags', '')
            problem.save()
            
            messages.success(request, f'Problem "{problem.title}" updated successfully!')
            return redirect('admin_problems')
        except Exception as e:
            messages.error(request, f'Error updating problem: {str(e)}')
    
    return render(request, 'problems/admin_edit_problem.html', {
        'problem': problem,
        'difficulties': Problem.DIFFICULTY_CHOICES,
        'companies': Problem.COMPANY_CHOICES
    })

@staff_member_required
@require_http_methods(["DELETE"])
def admin_delete_problem(request, problem_id):
    """Delete a problem"""
    try:
        problem = get_object_or_404(Problem, id=problem_id)
        title = problem.title
        problem.delete()
        return JsonResponse({
            'success': True,
            'message': f'Problem "{title}" deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting problem: {str(e)}'
        }, status=400)

@staff_member_required
def admin_manage_testcases(request, problem_id):
    """Manage test cases for a problem"""
    problem = get_object_or_404(Problem, id=problem_id)
    testcases = problem.testcases.all()
    
    if request.method == 'POST':
        try:
            TestCase.objects.create(
                problem=problem,
                input_data=request.POST['input_data'],
                expected_output=request.POST['expected_output'],
                is_sample=request.POST.get('is_sample') == 'on'
            )
            messages.success(request, 'Test case added successfully!')
            return redirect('admin_manage_testcases', problem_id=problem_id)
        except Exception as e:
            messages.error(request, f'Error adding test case: {str(e)}')
    
    return render(request, 'problems/admin_testcases.html', {
        'problem': problem,
        'testcases': testcases
    })

@staff_member_required
@require_http_methods(["DELETE"])
def admin_delete_testcase(request, testcase_id):
    """Delete a test case"""
    try:
        testcase = get_object_or_404(TestCase, id=testcase_id)
        testcase.delete()
        return JsonResponse({
            'success': True,
            'message': 'Test case deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting test case: {str(e)}'
        }, status=400)

@csrf_exempt
@login_required
def run_custom_input(request, problem_id):
    """Run code with custom input"""
    problem = get_object_or_404(Problem, pk=problem_id)
    if request.method == "POST":
        code = request.POST.get("code")
        custom_input = request.POST.get("custom_input", "")
        language = request.POST.get("language", "python")
        use_docker = request.POST.get("use_docker") == "true"
        
        # Run with custom input
        output = run_code(code, custom_input, language, use_docker)
        
        return JsonResponse({
            "success": True,
            "output": output,
            "input": custom_input,
            "language": language,
            "docker_used": use_docker
        })
    
    return JsonResponse({"success": False, "error": "Invalid request method"})

def test_page(request):
    """Test page for debugging code execution"""
    return render(request, 'test_page.html')

@login_required
def ai_chat_dashboard(request):
    return render(request, 'ai/dashboard.html')
