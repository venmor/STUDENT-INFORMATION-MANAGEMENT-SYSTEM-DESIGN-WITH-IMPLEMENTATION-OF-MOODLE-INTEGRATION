"""
URL configuration for sis_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("lti/", include("apps.integration.lti_urls")),
    path("api/v1/", include("apps.accounts.api.urls")),
    path("api/v1/", include("apps.academics.api.urls")),
    path("api/v1/", include("apps.students.api.urls")),
    path("api/v1/", include("apps.integration.api.urls")),
    path("api/v1/", include("apps.notifications.api.urls")),
    path("api/v1/", include("apps.audit.api.urls")),
    path("api/v1/", include("apps.calendar.api.urls")),
    path("api/v1/", include("apps.reporting.api.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.analytics.urls")),
    path("api/v1/", include("apps.knowledge.urls")),
    path("api/v1/", include("apps.copilot.urls")),
    path("api/v1/", include("apps.summarisation.urls")),
    path("api/v1/", include("apps.atrisk.urls")),
    path("api/v1/", include("apps.wellbeing.urls")),
    path("api/v1/", include("apps.structure.urls")),
    path("api/v1/", include("apps.admissions.urls")),
]
