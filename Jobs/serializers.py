from rest_framework import serializers
from .models import Job, JobApplication

#Job List Serializer
class JobListSerializer(serializers.ModelSerializer):
    posted_by = serializers.StringRelatedField()#shows the username instead of the user_id
    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'company',
            'location',
            'posted_by',
            'created_at',
            'deadline',
            'salary_min',
            'salary_max',
        ]
class JobDetailSerializer(serializers.ModelSerializer):
    posted_by = serializers.StringRelatedField()
    total_applications = serializers.SerializerMethodField()#custom field to count total applications for a job
    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'company',
            'location',
            'description',
            'job_type',
            'salary_min',
            'salary_max',
            'status',
            'deadline',
            'posted_by',
            'created_at',
            'updated_at',
            'total_applications',
        ]

    def get_total_applications(self, obj):
        return obj.applications.count()#count the number of applications related to the job

class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title',
            'company',
            'location',
            'description',
            'job_type',
            'salary_min',
            'salary_max',
            'status',
            'deadline',
        ]

    def validate(self, data):
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            raise serializers.ValidationError("Minimum salary cannot be greater than maximum salary.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request is None:
            return Job.objects.create(**validated_data)
        return Job.objects.create(posted_by=request.user, **validated_data)
class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = serializers.StringRelatedField(read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id',
            'job',
            'job_title',
            'applicant',
            'applicant_email',
            'resume',
            'cover_letter',
            'applied_at',
            'status',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        if request is not None and 'applicant' not in validated_data:
            validated_data['applicant'] = request.user
        return JobApplication.objects.create(**validated_data)
        
class JobApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['status']