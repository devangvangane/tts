import os
import pyttsx3
import docx
import PyPDF2
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

MEDIA_FOLDER = os.path.join(settings.BASE_DIR, "media")
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)

engine = pyttsx3.init()

def home(request):
    """Render homepage with all generated files."""
    functionality = request.GET.get("functionality", "tts")
    files = [f for f in os.listdir(MEDIA_FOLDER) if f.endswith(".mp3")]
    return render(request, "index.html", {"functionality": functionality, "files": files})


@csrf_exempt
def text_to_speech(request):
    """Convert text input to speech and return updated file list."""
    if request.method == "POST":
        text = request.POST.get("text")
        speed = float(request.POST.get("speed", 150))
        pitch = float(request.POST.get("pitch", 1.0))

        if not text.strip():
            return JsonResponse({"error": "Text field is required."}, status=400)

        engine.setProperty("rate", speed)
        engine.setProperty("pitch", pitch)

        file_name = f"speech_{len(os.listdir(MEDIA_FOLDER)) + 1}.mp3"
        file_path = os.path.join(MEDIA_FOLDER, file_name)

        engine.save_to_file(text, file_path)
        engine.runAndWait()

        files = [f for f in os.listdir(MEDIA_FOLDER) if f.endswith(".mp3")]
        return JsonResponse({"audio_url": f"/media/{file_name}", "files": files})


@csrf_exempt
def file_to_speech(request):
    """Convert uploaded PDF/DOCX to speech and return updated file list."""
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        file_extension = uploaded_file.name.split(".")[-1].lower()
        speed = float(request.POST.get("speed", 150))
        pitch = float(request.POST.get("pitch", 1.0))

        file_path = os.path.join(MEDIA_FOLDER, uploaded_file.name)
        with default_storage.open(file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        extracted_text = ""

        try:
            if file_extension == "pdf":
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() + " "
            elif file_extension == "docx":
                doc = docx.Document(file_path)
                extracted_text = " ".join([para.text for para in doc.paragraphs])
            else:
                return JsonResponse({"error": "Unsupported file type."}, status=400)

            if not extracted_text.strip():
                return JsonResponse({"error": "No text found in file."}, status=400)

            engine.setProperty("rate", speed)
            engine.setProperty("pitch", pitch)

            audio_filename = f"file_speech_{len(os.listdir(MEDIA_FOLDER)) + 1}.mp3"
            audio_filepath = os.path.join(MEDIA_FOLDER, audio_filename)

            engine.save_to_file(extracted_text, audio_filepath)
            engine.runAndWait()

            files = [f for f in os.listdir(MEDIA_FOLDER) if f.endswith(".mp3")]
            return JsonResponse({"audio_url": f"/media/{audio_filename}", "files": files})

        except Exception as e:
            return JsonResponse({"error": f"Error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request."}, status=400)


@csrf_exempt
def delete_audio(request):
    """Delete selected audio file and update the file list."""
    if request.method == "POST":
        file_name = request.POST.get("file_name")
        file_path = os.path.join(MEDIA_FOLDER, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            files = [f for f in os.listdir(MEDIA_FOLDER) if f.endswith(".mp3")]
            return JsonResponse({"message": "File deleted.", "files": files})
        else:
            return JsonResponse({"error": "File not found."}, status=404)

    return JsonResponse({"error": "Invalid request."}, status=400)
