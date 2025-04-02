import os
from django.shortcuts import render
from django.http import JsonResponse
import pyttsx3
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

MEDIA_FOLDER = os.path.join(settings.BASE_DIR, "media")

if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)  # Ensure media folder exists


@csrf_exempt
def text_to_speech(request):
    """Converts text to speech with pitch & speed settings, and saves the file"""
    engine = pyttsx3.init()

    voices = engine.getProperty("voices")
    if request.method == "POST":
        text = request.POST.get("text")
        speed = float(request.POST.get("speed", 150))  # Default to 150 WPM
        pitch = float(request.POST.get("pitch", 1.0))  # Default pitch
        voice = request.POST.get("voice")

        if not (text or voice) :
            return JsonResponse({"error": "Text field is required."}, status=400)

        engine.setProperty("rate", speed)  # Adjust speaking rate
        engine.setProperty("pitch", pitch)  # Adjust pitch (Note: Some engines might not support pitch)
        engine.setProperty("voice",voice)

        file_name = f"output_{len(os.listdir(MEDIA_FOLDER)) + 1}.mp3"
        file_path = os.path.join(MEDIA_FOLDER, file_name)

        engine.save_to_file(text, file_path)
        engine.runAndWait()

        # Return updated file list after creation
        files = [f for f in os.listdir(MEDIA_FOLDER) if f.endswith(".mp3")]
        return JsonResponse({"audio_url": f"/media/{file_name}", "files": files})

    files = [f for f in os.listdir(MEDIA_FOLDER) if f.endswith(".mp3")]

    voice_options = [{"id": voice.id, "name": voice.name} for voice in voices]
    return render(request, "index.html", {"files": files, "voice_options": voice_options})


@csrf_exempt
def delete_audio(request):
    """Deletes a selected audio file from media folder"""
    if request.method == "POST":
        file_name = request.POST.get("file_name")
        file_path = os.path.join(MEDIA_FOLDER, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            files = [f for f in os.listdir(MEDIA_FOLDER) if f.endswith(".mp3")]
            return JsonResponse({"message": f"{file_name} deleted!", "files": files})
        else:
            return JsonResponse({"error": "File not found."}, status=404)

    return JsonResponse({"error": "Invalid request."}, status=400)
