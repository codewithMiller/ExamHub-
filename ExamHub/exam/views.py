from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Exam, Question, ExamAttempt, StudentAnswer
from django.contrib.auth.decorators import login_required


def get_grade(pct):
    if pct >= 80: return 'A'
    if pct >= 70: return 'B'
    if pct >= 60: return 'C'
    if pct >= 50: return 'D'
    if pct >= 40: return 'E'
    return 'F'


# ── Home ──────────────────────────────────────────────────────────────────────
def home(request):
    exams = Exam.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'exam/home.html', {'exams': exams})


# ── Exam Management ───────────────────────────────────────────────────────────
def is_exam_admin(user, exam):
    return user.is_superuser or exam.created_by == user
    
@login_required    
def manage_exams(request):
    exams = Exam.objects.all().order_by('-created_at')
    return render(request, 'exam/manage_exams.html', {'exams': exams})

@login_required
def create_exam(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        duration = request.POST.get('duration', 30)
        if not title:
            messages.error(request, 'Exam title is required.')
            return render(request, 'exam/create_exam.html')
        exam = Exam.objects.create(title=title, description=description, duration_minutes=int(duration),created_by=request.user)
        messages.success(request, f'Exam "{exam.title}" created! Now add questions.')
        return redirect('add_question', exam_id=exam.id)
    return render(request, 'exam/create_exam.html')

@login_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if not is_exam_admin(request.user, exam):
        messages.error(request, 'You are not authorized to delete this exam.')
        return redirect('manage_exams')
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted.')
    return redirect('manage_exams')


# ── Question Management ───────────────────────────────────────────────────────
@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if not is_exam_admin(request.user, exam):
        messages.error(request, 'You are not authorized to edit this exam.')
        return redirect('manage_exams')
    questions = exam.questions.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            text = request.POST.get('text', '').strip()
            opt_a = request.POST.get('option_a', '').strip()
            opt_b = request.POST.get('option_b', '').strip()
            opt_c = request.POST.get('option_c', '').strip()
            opt_d = request.POST.get('option_d', '').strip()
            correct = request.POST.get('correct_answer', '').strip().upper()

            if not all([text, opt_a, opt_b, opt_c, opt_d, correct]):
                messages.error(request, 'All fields are required.')
            elif correct not in ['A', 'B', 'C', 'D']:
                messages.error(request, 'Correct answer must be A, B, C, or D.')
            else:
                order = questions.count() + 1
                Question.objects.create(
                    exam=exam, text=text,
                    option_a=opt_a, option_b=opt_b,
                    option_c=opt_c, option_d=opt_d,
                    correct_answer=correct, order=order
                )
                messages.success(request, f'Question {order} added!')
                return redirect('add_question', exam_id=exam.id)

        elif action == 'delete':
            q_id = request.POST.get('question_id')
            Question.objects.filter(id=q_id, exam=exam).delete()
            # Re-number
            for i, q in enumerate(exam.questions.all(), 1):
                q.order = i
                q.save()
            messages.success(request, 'Question deleted.')
            return redirect('add_question', exam_id=exam.id)

        elif action == 'done':
            return redirect('manage_exams')

    return render(request, 'exam/add_question.html', {'exam': exam, 'questions': questions})


# ── Take Exam ─────────────────────────────────────────────────────────────────

def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, is_active=True)
    questions = exam.questions.all()

    if not questions.exists():
        messages.error(request, 'This exam has no questions yet.')
        return redirect('home')

    if request.method == 'POST':
        student_name = request.POST.get('student_name', '').strip() or 'Anonymous'
        attempt = ExamAttempt.objects.create(
    exam=exam,
    student=request.user if request.user.is_authenticated else None,
    student_name=request.user.username if request.user.is_authenticated else student_name,
    total=questions.count()
)
        score = 0
        results = []

        for q in questions:
            selected = request.POST.get(f'q_{q.id}', '').upper()
            is_correct = (selected == q.correct_answer)
            if is_correct:
                score += 1
            StudentAnswer.objects.create(
                attempt=attempt, question=q,
                selected=selected, is_correct=is_correct
            )
            results.append({
                'question': q,
                'selected': selected,
                'selected_text': q.get_option_text(selected) if selected else '(no answer)',
                'is_correct': is_correct,
                'correct_answer': q.correct_answer,
                'correct_text': q.correct_option_text(),
            })

        pct = (score / questions.count()) * 100 if questions.count() else 0
        grade = get_grade(pct)
        attempt.score = score
        attempt.percentage = round(pct, 1)
        attempt.grade = grade
        attempt.save()

        return render(request, 'exam/results.html', {
            'attempt': attempt,
            'results': results,
            'score': score,
            'total': questions.count(),
            'percentage': round(pct, 1),
            'grade': grade,
            'exam': exam,
        })

    return render(request, 'exam/take_exam.html', {
        'exam': exam,
        'questions': questions,
    })


# ── Leaderboard ───────────────────────────────────────────────────────────────
@login_required
def leaderboard(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = exam.attempts.order_by('-percentage', 'submitted_at')[:20]
    return render(request, 'exam/leaderboard.html', {'exam': exam, 'attempts': attempts})