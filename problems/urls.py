from django.urls import path
from . import views, ai_views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),
    path('test/', views.test_page, name='test_page'),
    path('<int:problem_id>/', views.problem_detail, name='problem_detail'),
    path('<int:problem_id>/run/', views.run_submission, name='run_submission'),
    path('<int:problem_id>/submit/', views.submit_solution, name='submit_solution'),
    path('<int:problem_id>/custom/', views.run_custom_input, name='run_custom_input'),
    path('submissions/mine/', views.my_submissions, name='my_submissions'),
    
    # AI Feature URLs
    path('ai/hint/', ai_views.get_ai_hint, name='get_ai_hint'),
    path('ai/recommendations/', ai_views.get_ai_recommendations, name='get_ai_recommendations'),
    path('ai/chat/', ai_views.ai_chat, name='ai_chat'),
    path('ai/dashboard/', views.ai_chat_dashboard, name='ai_dashboard'),
    
    # Admin URLs
    path('admin/problems/', views.admin_problems, name='admin_problems'),
    path('admin/problems/create/', views.admin_create_problem, name='admin_create_problem'),
    path('admin/problems/<int:problem_id>/edit/', views.admin_edit_problem, name='admin_edit_problem'),
    path('admin/problems/<int:problem_id>/delete/', views.admin_delete_problem, name='admin_delete_problem'),
    path('admin/problems/<int:problem_id>/testcases/', views.admin_manage_testcases, name='admin_manage_testcases'),
    path('admin/testcases/<int:testcase_id>/delete/', views.admin_delete_testcase, name='admin_delete_testcase'),
]
