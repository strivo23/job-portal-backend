from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    JobApplyView,
    JobApplicationsListView,
    JobApplicationStatusUpdateView,
    MyApplicationsListView,
)

urlpatterns = [
    #Job URLs
    path('jobs/', JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:pk>/', JobDetailView.as_view(), name='job-detail'),

    #Job Application URLs
    path('jobs/<int:pk>/apply/', JobApplyView.as_view(), name='job-apply'),
    path('jobs/<int:pk>/applications/', JobApplicationsListView.as_view(), name='job-application-detail'),
    path('applications/<int:pk>/update-status/', JobApplicationStatusUpdateView.as_view(), name='job-application-status-update'),
    path('my-applications/', MyApplicationsListView.as_view(), name='my-applications'),
]