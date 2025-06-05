import sys
import pytest

from app.services.quiz import evaluate_quiz_answer, generate_quiz_feedback, extract_answer_data
from app.db.database import get_supabase_client


def run_quiz_test(question_type, answer_text, correct_answers, expected_is_correct, expected_feedback=None):
    """Допоміжна функція для тестування оцінювання відповідей."""
    question = {"type": question_type}
    
    if question_type == "number":
        question["tolerance"] = 0.1
        
    correct_answers_data = [{"answer_text": ans} for ans in correct_answers]
    result = evaluate_quiz_answer(question, answer_text, correct_answers_data)
    
    assert result["is_correct"] == expected_is_correct
    
    if expected_feedback:
        assert result["feedback"] == expected_feedback
    else:
        expected = "Correct! Good job." if expected_is_correct else "Incorrect answer."
        assert result["feedback"] == expected


def test_single_choice_answers():
    """Тестування питань з одиночним вибором."""
    run_quiz_test("single", "Option A", ["Option A"], True)
    run_quiz_test("single", "Option B", ["Option A"], False)
    
    question = {"type": "single", "text": "Скільки буде 2+2?"}
    correct_answers = [{"answer_text": "4"}]
    
    result = evaluate_quiz_answer(question, "4", correct_answers)
    assert result["is_correct"] is True
    
    result = evaluate_quiz_answer(question, "5", correct_answers)
    assert result["is_correct"] is False


def test_multi_choice_answers():
    """Тестування питань з множинним вибором."""
    question = {"type": "multi", "text": "Виберіть прості числа:"}
    correct_answers = [
        {"answer_text": "2"},
        {"answer_text": "3"},
        {"answer_text": "5"}
    ]
    
    result = evaluate_quiz_answer(question, "2, 3, 5", correct_answers)
    assert result["is_correct"] is True
    
    result = evaluate_quiz_answer(question, "2, 3", correct_answers)
    assert result["is_correct"] is False
    
    result = evaluate_quiz_answer(question, "2, 3, 5, 4", correct_answers)
    assert result["is_correct"] is False


def test_text_answers():
    """Тестування текстових відповідей."""
    run_quiz_test("text", "hello world", ["Hello World"], True)
    run_quiz_test("text", "Wrong Answer", ["Correct Answer"], False)
    
    # Тест на нечутливість до регістру
    question = {"type": "text", "text": "Яка столиця Франції?"}
    correct_answers = [{"answer_text": "Paris"}]
    
    result = evaluate_quiz_answer(question, "paris", correct_answers)
    assert result["is_correct"] is True


def test_number_answers():
    """Тестування числових відповідей."""
    question = {"type": "number", "text": "Скільки π (пі) до 1 десяткового знаку?", "tolerance": 0.05}
    correct_answers = [{"answer_text": "3.1"}]
    
    result = evaluate_quiz_answer(question, "3.14", correct_answers)
    assert result["is_correct"] is True
    
    result = evaluate_quiz_answer(question, "3.2", correct_answers)
    assert result["is_correct"] is False
    
    result = evaluate_quiz_answer(question, "pi", correct_answers)
    assert result["is_correct"] is False
    assert result["feedback"] == "Invalid number format"


@pytest.mark.parametrize("score,expected", [
    (95, "Excellent work! You've mastered this module."),
    (90, "Excellent work! You've mastered this module."),
    (85, "Great job! You have a solid understanding of the material."),
    (80, "Great job! You have a solid understanding of the material."),
    (75, "Good work! You've passed the quiz."),
    (70, "Good work! You've passed the quiz."),
    (69, "You need to score at least 70% to pass. Review the material and try again."),
    (0, "You need to score at least 70% to pass. Review the material and try again.")
])
def test_quiz_feedback_thresholds(score, expected):
    """Тестування генерації відгуків залежно від балів."""
    feedback = generate_quiz_feedback(score)
    assert feedback == expected


def test_data_extraction():
    """Тестування діставання даних."""
    answer_data = {"question_id": 5, "answer_text": "Sample answer"}
    result = extract_answer_data(answer_data)
    
    assert result["question_id"] == 5
    assert result["answer_text"] == "Sample answer"

    class AnswerObj:
        def __init__(self, qid, text):
            self.question_id = qid
            self.answer_text = text
    
    answer_obj = AnswerObj(10, "Object answer")
    result = extract_answer_data(answer_obj)
    
    assert result["question_id"] == 10
    assert result["answer_text"] == "Object answer"


def test_missing_data():
    """Тестування діставання даних з відсутніми полями."""
    result = extract_answer_data({})
    assert result["question_id"] is None
    assert result["answer_text"] == ""
    
    result = extract_answer_data(None)
    assert result["question_id"] is None
    assert result["answer_text"] == ""


# Тести бази даних
@pytest.fixture
def db_client():
    """Фікстура для отримання клієнта бази даних."""
    try:
        return get_supabase_client()
    except Exception as e:
        pytest.fail(f"Не вдалося підключитися до бази даних: {str(e)}")


def test_questions_have_correct_answers(db_client):
    """Перевірка наявності правильних відповідей для питань."""
    questions_response = db_client.table("questions").select("*").execute()
    
    if not questions_response.data:
        pytest.skip("Немає питань для тестування в базі даних")
    
    for question in questions_response.data:
        question_id = question["id"]
        question_text = question.get("question_text", "Unknown")
        
        answers_response = db_client.table("answers").select("*").eq("question_id", question_id).execute()
        
        assert answers_response.data and len(answers_response.data) > 0, \
            f"Питання {question_id} ({question_text}) не має жодної відповіді"
        
        correct_answers = [a for a in answers_response.data if a.get("is_correct")]
        assert len(correct_answers) > 0, \
            f"Питання {question_id} ({question_text}) не має жодної правильної відповіді"


def test_number_questions_have_tolerance(db_client):
    """Перевірка наявності значень tolerance для числових питань."""
    questions_response = db_client.table("questions").select("*").eq("type", "number").execute()
    
    for question in questions_response.data:
        assert question.get("tolerance") is not None, \
            f"Числове питання {question['id']} не має значення tolerance"

if __name__ == "__main__":
    pytest.main(sys.argv)
