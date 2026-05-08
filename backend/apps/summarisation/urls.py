from django.urls import path

from .views import SummariseApproveView, SummariseView

urlpatterns = [
    path("ai/summarise/", SummariseView.as_view(), name="summarise-request"),
    path("ai/summarise/<uuid:summarisation_id>/approve/", SummariseApproveView.as_view(), name="summarise-approve"),
]
