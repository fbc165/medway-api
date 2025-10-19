from rest_framework import serializers
from submission.models import Submission, Answer
from question.models import Alternative


class AnswerInputSerializer(serializers.Serializer):
    """
    Serializer para receber as respostas do estudante
    """

    question_id = serializers.IntegerField()
    alternative_id = serializers.IntegerField()

    def validate(self, data):
        """
        Validar que a alternativa pertence à questão
        """
        question_id = data.get("question_id")
        alternative_id = data.get("alternative_id")

        try:
            alternative = Alternative.objects.get(id=alternative_id)
            if alternative.question_id != question_id:
                raise serializers.ValidationError(
                    f"Alternative {alternative_id} does not belong to question {question_id}"
                )
        except Alternative.DoesNotExist:
            raise serializers.ValidationError(
                f"Alternative {alternative_id} does not exist"
            )

        return data


class SubmitExamSerializer(serializers.Serializer):
    """
    Serializer para enviar uma prova completa
    """

    student_id = serializers.IntegerField()
    exam_id = serializers.IntegerField()
    answers = AnswerInputSerializer(many=True)

    def validate_answers(self, value):
        """
        Validar que não há questões duplicadas
        """
        question_ids = [ans["question_id"] for ans in value]
        if len(question_ids) != len(set(question_ids)):
            raise serializers.ValidationError(
                "Not allowed to answer the same question more than once"
            )
        return value

    def validate(self, data):
        """
        Validar que o estudante ainda não enviou este exame
        """
        student_id = data.get("student_id")
        exam_id = data.get("exam_id")

        if Submission.objects.filter(student_id=student_id, exam_id=exam_id).exists():
            raise serializers.ValidationError(
                "This student has already submitted this exam"
            )

        return data


class AnswerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalhar cada resposta
    """

    question_content = serializers.CharField(source="question.content", read_only=True)
    selected_alternative_content = serializers.CharField(
        source="selected_alternative.content", read_only=True
    )
    selected_alternative_option = serializers.SerializerMethodField()
    is_correct = serializers.BooleanField(read_only=True)
    correct_alternative_id = serializers.SerializerMethodField()
    correct_alternative_option = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            "id",
            "question_id",
            "question_content",
            "selected_alternative_id",
            "selected_alternative_content",
            "selected_alternative_option",
            "is_correct",
            "correct_alternative_id",
            "correct_alternative_option",
        ]

    def get_selected_alternative_option(self, obj):
        """
        Retorna a letra da alternativa selecionada
        """
        return obj.selected_alternative.get_option_display()

    def get_correct_alternative_id(self, obj):
        """Retorna o ID da alternativa correta."""
        correct = obj.question.alternatives.filter(is_correct=True).first()
        return correct.id if correct else None

    def get_correct_alternative_option(self, obj):
        """
        Retorna a letra da alternativa correta
        """
        correct = obj.question.alternatives.filter(is_correct=True).first()
        if correct:
            return correct.get_option_display()
        return None


class SubmissionResultSerializer(serializers.ModelSerializer):
    """
    Serializer para retornar o resultado completo da prova
    """

    student_name = serializers.CharField(source="student.name", read_only=True)
    exam_name = serializers.CharField(source="exam.name", read_only=True)
    answers = AnswerDetailSerializer(many=True, read_only=True)
    score_data = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id",
            "student_id",
            "student_name",
            "exam_id",
            "exam_name",
            "submitted_at",
            "score_data",
            "answers",
        ]

    def get_score_data(self, obj):
        """
        Retorna os dados de pontuação calculados dinamicamente
        """
        return obj.calculate_score()
