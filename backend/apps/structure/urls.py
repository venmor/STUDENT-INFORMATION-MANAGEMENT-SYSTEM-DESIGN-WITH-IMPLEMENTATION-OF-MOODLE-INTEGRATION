from django.urls import path

from apps.structure.views import (
    DepartmentDetailView,
    DepartmentListCreateView,
    ProgrammeDetailView,
    ProgrammeListCreateView,
    SchoolDetailView,
    SchoolListCreateView,
    StreamDetailView,
    StreamListCreateView,
)

urlpatterns = [
    path("structure/schools", SchoolListCreateView.as_view(), name="school-list"),
    path("structure/schools/<uuid:school_id>", SchoolDetailView.as_view(), name="school-detail"),
    path("structure/departments", DepartmentListCreateView.as_view(), name="department-list"),
    path("structure/departments/<uuid:department_id>", DepartmentDetailView.as_view(), name="department-detail"),
    path("structure/programmes", ProgrammeListCreateView.as_view(), name="programme-list"),
    path("structure/programmes/<uuid:programme_id>", ProgrammeDetailView.as_view(), name="programme-detail"),
    path("structure/streams", StreamListCreateView.as_view(), name="stream-list"),
    path("structure/streams/<uuid:stream_id>", StreamDetailView.as_view(), name="stream-detail"),
]
