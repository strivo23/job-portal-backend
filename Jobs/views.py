from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import Job, JobApplication
from .serializers import (
        JobListSerializer, 
        JobDetailSerializer, 
        JobCreateSerializer,
        JobApplicationSerializer,
        JobApplicationStatusUpdateSerializer
        )

class JobListCreateView(APIView):

    def get_permissions(self):
        #Anyone can view the list of jobs, but only logged users can create or apply for jobs
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]
        
    def get(self, request):
        jobs = Job.objects.filter(status='open').order_by('-created_at')
        serializer = JobListSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        #only employer can post the job openings
        if request.user.userprofile.user_type != 'employer':
            return Response({"detail": "Only employers can post job openings."}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            job = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#retrieve, update, delete a specific job
class JobDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]
        
    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        serializer = JobDetailSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        #only the employer who posted the job can update it
        if job.posted_by != request.user:
            return Response({"detail": "You do not have permission to update this job."}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobCreateSerializer(job, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        #only the employer who posted the job can delete it
        if job.posted_by != request.user:
            return Response({"detail": "You do not have permission to delete this job."}, status=status.HTTP_403_FORBIDDEN)
        job.delete()
        return Response({"message": "Job deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class JobApplyView(APIView):#Apply to a Job
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        #only job seekers can apply for jobs
        if request.user.userprofile.user_type != 'job_seeker':
            return Response({"detail": "Only job seekers can apply for jobs."}, status=status.HTTP_403_FORBIDDEN)
        
        #check if the user has already applied for the job
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            return Response({"detail": "You have already applied for this job."}, status=status.HTTP_400_BAD_REQUEST)
    
    #check if the job is open for applications
        if job.status != 'open':
            return Response({"error": "This job is not open for applications."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JobApplicationSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(applicant=request.user, job=job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#List all applications for a specific job (only for the employer who posted the job)
class JobApplicationsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        #only the employer who posted the job can view the applications
        if job.posted_by != request.user:
            return Response({"detail": "You do not have permission to view applications for this job."}, status=status.HTTP_403_FORBIDDEN)
        applications = JobApplication.objects.filter(job=job).order_by('-applied_at')
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
#Update the status of a job application (only for the employer who posted the job)
class JobApplicationStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        application = get_object_or_404(JobApplication, pk=pk)
        
        #only the employer who posted the job can update the application status
        if application.job.posted_by != request.user:
            return Response({"detail": "You do not have permission to update the status of this application."}, status=status.HTTP_403_FORBIDDEN)
        serializer = JobApplicationStatusUpdateSerializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)#Allows only updating statuss field of the application
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MyApplicationsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
        serializer = JobApplicationSerializer(applications, many=True)
        return Response(serializer.data)