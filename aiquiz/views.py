import google.generativeai as genai
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Max, Avg
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy

from .models import UserResponse, Quiz, Question

genai.configure(api_key=settings.GEMINI_API_KEY)

def logout_view(request):
    logout(request)
    return redirect('account_login')

def registeruser(request):
    return redirect('account_signup')


@login_required(login_url='account_login')
def quiz_view(request):
    # Initialize default values at the start of the function
    suggested_topic = "General Knowledge"
    suggested_difficulty = "medium"
    has_history = UserResponse.objects.filter(user=request.user).exists()

    # If user has history, ALWAYS calculate personalized suggestions
    if has_history:
        weak_topics = UserResponse.objects.filter(user=request.user).values('topic').annotate(
            accuracy=Avg('is_correct')
        ).order_by('accuracy')

        if weak_topics:
            suggested_topic = weak_topics[0]['topic']
            weakest_accuracy = weak_topics[0]['accuracy'] or 0
            
            # Adjust difficulty based on performance
            if weakest_accuracy < 0.6:
                suggested_difficulty = 'easy'
            elif weakest_accuracy > 0.85:
                suggested_difficulty = 'hard'

    # =====================================
    # 1. VIEW SAVED QUIZ RESULTS (GET)
    # =====================================
    if request.method == 'GET' and 'quiz_id' in request.GET:
        quiz_id = request.GET.get('quiz_id')
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        saved_responses = UserResponse.objects.filter(user=request.user, quiz=quiz)
        response_map = {resp.question_id: resp for resp in saved_responses}

        score = 0
        results_details = []
        for question in quiz.questions.all():
            resp = response_map.get(question.id)
            if resp:
                if resp.is_correct:
                    score += 1
                results_details.append({
                    'question': question.question_text,
                    'user_answer': resp.user_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': resp.is_correct,
                    'explanation': question.explanation
                })

        return render(request, 'quiz.html', {
            'quiz': quiz,
            'results': {
                'score': score,
                'total': quiz.questions.count(),
                'details': results_details
            },
            'show_history_button': True,
            'show_results_only': True,
            'first_time_user': not has_history,
            'next_topic': suggested_topic,  # Add this
            'next_difficulty': suggested_difficulty  # Add this
        })

    # =====================================
    # 2. SUBMIT QUIZ ANSWERS (POST with quiz_id)
    # =====================================
    if request.method == 'POST' and 'quiz_id' in request.POST:
        quiz_id = request.POST.get('quiz_id')
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        questions = quiz.questions.all()

        score = 0
        results_details = []

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}', '').strip()
            correct_answer = (question.correct_answer or "").strip()

            is_correct = (
                correct_answer and
                user_answer and
                user_answer.lower() == correct_answer.lower()
            )

            UserResponse.objects.create(
                user=request.user,
                quiz=quiz,
                question=question,
                user_answer=user_answer,
                is_correct=is_correct,
                topic=quiz.topic,
                question_type=question.question_type,
                difficulty=getattr(question, 'difficulty', 'medium'),
                time_taken=None
            )

            if is_correct:
                score += 1

            results_details.append({
                'question': question.question_text,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.explanation
            })

        # Recalculate suggestions after new quiz data
        weak_topics = UserResponse.objects.filter(user=request.user).values('topic').annotate(
            accuracy=Avg('is_correct')
        ).order_by('accuracy')

        if weak_topics:
            suggested_topic = weak_topics[0]['topic']
            weakest_accuracy = weak_topics[0]['accuracy'] or 0
            if weakest_accuracy < 0.6:
                suggested_difficulty = 'easy'
            elif weakest_accuracy > 0.85:
                suggested_difficulty = 'hard'

        return render(request, 'quiz.html', {
            'results': {
                'score': score,
                'total': questions.count(),
                'details': results_details
            },
            'show_history_button': False,
            'next_topic': suggested_topic,
            'next_difficulty': suggested_difficulty,
            'first_time_user': False  # They definitely have history now
        })

    # =====================================
    # 3. GENERATE NEW QUIZ (POST with topic)
    # =====================================
    
    if request.method == 'POST' and 'topic' in request.POST:
        topic = request.POST.get('topic')

        # Use the already calculated suggestions or the provided topic
        weakest_topic = topic
        difficulty = request.POST.get('difficulty', suggested_difficulty)  # Use user-selected or suggested

        # If user has history and not using recommended, still allow custom difficulty
        # But for recommended, difficulty is posted from hidden field

        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = f"""
                You are an expert quiz generator.

                Generate number of  unique quiz questions  according to "{difficulty}" level for the topic: "{weakest_topic}"  
                The difficulty level is: "{difficulty}".  
                Difficulty meanings:
                - easy = simple facts, definitions, basic recall, no of question:8
                - medium = moderate reasoning, short problem-solving,but  generate double the number of questions than easy 
                - hard = in-depth analysis, multi-step reasoning,generate Question atleast 25

                Return ONLY a valid JSON array (no markdown, no code block, no extra text).  
                Each element in the array must be an object with the following keys:

                - "type": One of "MCQ", "Fill-in-the-Blank", "True/False", or "Logical Reasoning"
                - "question": The full question text. For Fill-in-the-Blank, use "____" for the blank.
                - "options": A list of possible answers (empty list for Fill-in-the-Blank or Logical Reasoning if not needed)
                - "answer": The correct answer exactly as it should be matched
                - "explanation": A short explanation (1-2 sentences) for why the answer is correct

                Rules:
                1. For MCQ and True/False, ensure exactly one correct answer.
                2. Avoid ambiguity in answers.
                3. Ensure questions match the difficulty level specified.
                4. Do not include numbering or formatting outside the JSON.
                """

            response = model.generate_content(prompt)
            cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
            quiz_data_from_ai = json.loads(cleaned_response_text)

            new_quiz = Quiz.objects.create(topic=weakest_topic)
            for q_data in quiz_data_from_ai:
                Question.objects.create(
                    quiz=new_quiz,
                    question_type=q_data.get('type', 'MCQ')[:3].upper(),
                    question_text=q_data.get('question'),
                    options=q_data.get('options', []),
                    correct_answer=q_data.get('answer'),
                    explanation=q_data.get('explanation', ''),
                    difficulty=difficulty
                )

            return render(request, 'quiz.html', {
                'quiz': new_quiz,
                'show_history_button': True,
                'first_time_user': not has_history,
                'next_topic': suggested_topic,
                'next_difficulty': suggested_difficulty
            })

        except Exception as e:
            return render(request, 'quiz.html', {
                'error': f"An error occurred: {e}",
                'show_history_button': True,
                'first_time_user': not has_history,
                'next_topic': suggested_topic,
                'next_difficulty': suggested_difficulty
            })

    # =====================================
    # 4. DEFAULT VIEW (Homepage)
    # =====================================
    return render(request, 'quiz.html', {
        'show_history_button': True,
        'first_time_user': not has_history,
        'next_topic': suggested_topic,      # This ensures suggestions always appear
        'next_difficulty': suggested_difficulty
    })

@login_required(login_url='account_login')
def quiz_history_view(request):
    """
    Displays a list of all previously generated quizzes.
    """
    user_quizzes = Quiz.objects.filter(userresponse__user=request.user).distinct().order_by('-created_at')
    
    return render(request, 'quiz_history.html', {
        'all_quizzes': user_quizzes,
    })
@login_required(login_url='account_login')
def score_chart_view(request):
    # Get all quizzes the user has attempted
    user_quizzes = Quiz.objects.filter(userresponse__user=request.user).distinct().order_by('created_at')
    
    chart_data = []
    total_quizzes = 0
    total_score = 0
    
    for quiz in user_quizzes:
        # Calculate score for this quiz
        user_responses = UserResponse.objects.filter(user=request.user, quiz=quiz)
        quiz_score = user_responses.filter(is_correct=True).count()
        total_questions = quiz.questions.count()
        
        # Add to chart data
        chart_data.append({
            'date': quiz.created_at.strftime('%Y-%m-%d'),
            'score': quiz_score,
            'total': total_questions,
            'topic': quiz.topic
        })
        
        total_quizzes += 1
        total_score += quiz_score
    
    # Calculate overall percentage (assuming 5 questions per quiz)
    max_possible_score = total_quizzes * 5
    overall_percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
    
    if not chart_data:
        chart_data = []
        total_quizzes = 0
        total_score = 0
        overall_percentage = 0

    context = {
        'statistics': {
            'total_quizzes': total_quizzes,
            'total_score': total_score,
            'overall_percentage': round(overall_percentage, 1),
        },
        'chart_data': json.dumps(chart_data),
        'has_data': True
    }
    return render(request, 'aiquiz/score_chart.html', context)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/pass_reset_form.html'
    email_template_name = 'account/pass_reset_form_key.html'
    subject_template_name = 'account/pass_reset_done.txt'
    success_url = reverse_lazy('pass_reset')