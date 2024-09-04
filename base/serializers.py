from rest_framework.serializers import ModelSerializer
from .models import ParsedResume

class ParsedResumeSerializer(ModelSerializer):
    class Meta:
        model = ParsedResume
        fields = "__all__"
    
    def create(self, validated_data):
        # Custom logic for handling file uploads
        return super().create(validated_data)