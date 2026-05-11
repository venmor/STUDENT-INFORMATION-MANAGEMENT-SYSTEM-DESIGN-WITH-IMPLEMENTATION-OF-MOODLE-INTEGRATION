from rest_framework import generics, permissions, status
from rest_framework.response import Response

from apps.structure.models import Department, Programme, School, Stream
from apps.structure.serializers import (
    DepartmentSerializer,
    ProgrammeSerializer,
    SchoolSerializer,
    StreamSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.primary_role == "ADMIN"


class SchoolListCreateView(generics.ListCreateAPIView):
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = School.objects.all()
        if self.request.query_params.get("active"):
            qs = qs.filter(is_active=True)
        return qs


class SchoolDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SchoolSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = School.objects.all()
    lookup_field = "pk"
    lookup_url_kwarg = "school_id"


class DepartmentListCreateView(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Department.objects.select_related("school")
        school = self.request.query_params.get("school")
        if school:
            qs = qs.filter(school_id=school)
        if self.request.query_params.get("active"):
            qs = qs.filter(is_active=True)
        return qs


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Department.objects.select_related("school")
    lookup_field = "pk"
    lookup_url_kwarg = "department_id"


class ProgrammeListCreateView(generics.ListCreateAPIView):
    serializer_class = ProgrammeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Programme.objects.select_related("department")
        department = self.request.query_params.get("department")
        if department:
            qs = qs.filter(department_id=department)
        level = self.request.query_params.get("level")
        if level:
            qs = qs.filter(level=level)
        if self.request.query_params.get("active"):
            qs = qs.filter(is_active=True)
        return qs


class ProgrammeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProgrammeSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Programme.objects.select_related("department")
    lookup_field = "pk"
    lookup_url_kwarg = "programme_id"


class StreamListCreateView(generics.ListCreateAPIView):
    serializer_class = StreamSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Stream.objects.select_related("programme")
        programme = self.request.query_params.get("programme")
        if programme:
            qs = qs.filter(programme_id=programme)
        if self.request.query_params.get("active"):
            qs = qs.filter(is_active=True)
        return qs


class StreamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StreamSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Stream.objects.select_related("programme")
    lookup_field = "pk"
    lookup_url_kwarg = "stream_id"
