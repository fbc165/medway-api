from django.urls import path
from submission.views import SubmissionView

urlpatterns = [
    path("", SubmissionView.as_view(), name="exam-submission"),
    path("<int:pk>/", SubmissionView.as_view(), name="submission-detail"),
]
