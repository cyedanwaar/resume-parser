from django.conf import settings
from .models import ParsedResume
from .serializers import ParsedResumeSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import PyPDF2
import json


GENAI_KEY = settings.GENAI_KEY
genai.configure(api_key=GENAI_KEY) 


def parse_resume(file):
    def pdf_to_string(file):
        pdf_text = ""
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            pdf_text += page.extract_text()
        return pdf_text
        
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }
    
    pdf_content = pdf_to_string(file)

    responses = {}
    try:
        responses['basic_profile'] = model.generate_content(
            "Find Basic profile info of the candidate with following parameters: Name, age, phone number, language, email address, home address, introduction :\n" + pdf_content,
            safety_settings=safety_settings
        )
        responses['education'] = model.generate_content(
            "Find Educational details of the candidate with following parameters: Name of the Degree, institute of Degree awarded, field of study, Degree start date, Degree end date :\n" + pdf_content,
            safety_settings=safety_settings
        )
        responses['certification'] = model.generate_content(
            "Find certification done by the candidate with following parameters: Certificate name or title, institute name of certificate, description of certificate, certificate issued date, certification start date, certification end date, validity :\n" + pdf_content,
            safety_settings=safety_settings
        )
        responses['job_experience'] = model.generate_content(
            "Find Job Experience with following parameters: position held, short job description, company name, job start date, job end date :\n" + pdf_content,
            safety_settings=safety_settings
        )
        responses['skills'] = model.generate_content(
            "Find soft skills of the candidate :\n" + pdf_content,
            safety_settings=safety_settings
        )
        responses['project'] = model.generate_content(
            "Find projects done by the candidate with following parameters: project name, short description, project start date project end date :\n" + pdf_content,
            safety_settings=safety_settings
        )
        responses['social_links'] = model.generate_content(
            "Find profile links of the candidate with following parameters: linkedin profile, github profile, facebook profile, instagram profile :\n" + pdf_content,
            safety_settings=safety_settings
        )
    
    except Exception as e:
        return f"Exception occurred: {str(e)}"

    parsed_dicts = {}
    for key, response in responses.items():
        if response:
            try:
                parsed_dicts[key] = json.loads(response.text)
            except json.JSONDecodeError as e:
                return f"Error decoding JSON from response for {key}: {str(e)}"

    merged_dict = {}
    for d in parsed_dicts.values():
        merged_dict.update(d)

    merged_json = json.dumps(merged_dict, indent=2)

    return merged_json


# Create your views here.

class ParsedResumeView(APIView):
    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        if not uploaded_file.name.endswith('.pdf'):
            return Response({"error": "Invalid file type. Please upload a PDF."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            parsed_data = parse_resume(uploaded_file)

            parsed_resume = ParsedResume(
                name=uploaded_file.name.split('.')[0],
                resume=uploaded_file,
                parsed_data=parsed_data
            )
            parsed_resume.save()

            serializer = ParsedResumeSerializer(parsed_resume)
            return Response({"message": "Resume parsed successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetResume(APIView):
    def post(self, request):
        return Response({"message":"Post is working"})
    def get(self, request):
        return Response({"message":"Get is working"})