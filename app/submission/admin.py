from django.contrib import admin

from submission.models import Submission, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = (
        "question",
        "get_selected_letter",
        "get_is_correct",
    )
    fields = ("question", "get_selected_letter", "get_is_correct")

    def get_selected_letter(self, obj):
        if obj.selected_alternative:
            return obj.selected_alternative.get_option_display()
        return "-"

    get_selected_letter.short_description = "Selected alternative"

    def get_is_correct(self, obj):
        return "Yes" if obj.is_correct else "No"

    get_is_correct.short_description = "Correct"


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    readonly_fields = (
        "student",
        "exam",
    )
