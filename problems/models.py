from django.db import models

# Create your models here.
from django.db import models

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    COMPANY_CHOICES = [
        ('Google', 'Google'),
        ('Meta', 'Meta'),
        ('Amazon', 'Amazon'),
        ('Microsoft', 'Microsoft'),
        ('Apple', 'Apple'),
        ('Netflix', 'Netflix'),
        ('Tesla', 'Tesla'),
        ('Uber', 'Uber'),
        ('LinkedIn', 'LinkedIn'),
        ('Twitter', 'Twitter'),
        ('Spotify', 'Spotify'),
        ('Airbnb', 'Airbnb'),
        ('ByteDance', 'ByteDance'),
        ('Goldman Sachs', 'Goldman Sachs'),
        ('JPMorgan', 'JPMorgan'),
        ('Other', 'Other'),
    ]

    title = models.CharField(max_length=100)
    statement = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    company = models.CharField(max_length=50, choices=COMPANY_CHOICES, default='Other')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


from django.contrib.auth.models import User

class Submission(models.Model):
    LANGUAGE_CHOICES = [
        ('py', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.problem.title}"
class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='testcases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)

    def __str__(self):
        return f"TestCase for {self.problem.title}"
