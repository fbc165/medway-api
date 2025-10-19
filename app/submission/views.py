from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from submission.models import Submission, Answer
from submission.serializers import SubmitExamSerializer, SubmissionResultSerializer
from student.models import Student
from exam.models import Exam
from question.models import Question, Alternative


class SubmissionView(APIView):
    """
    Endpoint para o estudante enviar todas as respostas de uma prova
    """

    def post(self, request):
        serializer = SubmitExamSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        student = get_object_or_404(Student, id=data["student_id"])
        exam = get_object_or_404(Exam, id=data["exam_id"])

        try:
            with transaction.atomic():
                submission = Submission.objects.create(student=student, exam=exam)

                answers_to_create = []
                for answer_data in data["answers"]:
                    question = get_object_or_404(
                        Question, id=answer_data["question_id"]
                    )
                    alternative = get_object_or_404(
                        Alternative, id=answer_data["alternative_id"]
                    )

                    answers_to_create.append(
                        Answer(
                            submission=submission,
                            question=question,
                            selected_alternative=alternative,
                        )
                    )

                Answer.objects.bulk_create(answers_to_create)

                return Response({"id": submission.id}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response(
                {"error": "Validation error", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": "Internal Server Error", "detail": "Unexpected error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request, pk):
        """
        Endpoint para obter o resultado de uma prova
        """
        submission = get_object_or_404(
            Submission.objects.prefetch_related(
                "answers__question__alternatives", "answers__selected_alternative"
            ),
            pk=pk,
        )

        serialized_submission = SubmissionResultSerializer(submission)
        return Response(serialized_submission.data, status=status.HTTP_200_OK)
