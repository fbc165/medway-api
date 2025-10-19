from django.db import models

from exam.models import Exam
from student.models import Student
from question.models import Question, Alternative


class Submission(models.Model):
    """
    Submissão/envio de uma prova
    """

    student = models.ForeignKey(
        Student,
        related_name="submissions",
        on_delete=models.CASCADE,
    )

    exam = models.ForeignKey(Exam, related_name="submissions", on_delete=models.CASCADE)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "submission"
        unique_together = ("student", "exam")
        ordering = ["exam"]

    def __str__(self):
        return f"{self.exam} - {self.student} ({self.id})"

    def calculate_score(self):
        """
        Calcula a pontuação baseada nas alternativas corretas
        """
        total = self.answers.count()
        if total == 0:
            return {"total_questions": 0, "correct_answers": 0, "score": 0}

        correct = self.answers.filter(selected_alternative__is_correct=True).count()

        score = round((correct / total) * 100, 2)

        return {"total_questions": total, "correct_answers": correct, "score": score}


class Answer(models.Model):
    """
    Resposta de uma questão
    """

    submission = models.ForeignKey(
        Submission, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )

    selected_alternative = models.ForeignKey(
        Alternative,
        related_name="answers",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "answer"
        unique_together = ("submission", "question")

    def __str__(self):
        return f"Answer ID {self.id}"

    @property
    def is_correct(self):
        """
        Propriedade computada que retorna se a resposta está correta.
        Consulta direto a alternativa, sem armazenar no banco.
        """
        return self.selected_alternative.is_correct or False
