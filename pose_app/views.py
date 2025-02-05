from django.shortcuts import render, redirect
from .forms import FileUploadForm
from .models import UploadedFile
import cv2
import os
from ultralytics import YOLO
from django.conf import settings
from django.http import HttpResponse, FileResponse

# Load YOLO Model
model = YOLO(os.path.join(settings.BASE_DIR, "yolov8n-pose.pt"))

def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()

            # Check file type (image or video)
            file_path = uploaded_file.file.path
            file_name, file_ext = os.path.splitext(file_path)
            output_path = file_name + "_output" + file_ext

            if file_ext.lower() in [".jpg", ".jpeg", ".png"]:
                img = cv2.imread(file_path)
                results = model(img)

                for result in results:
                    img = result.plot()

                cv2.imwrite(output_path, img)
                uploaded_file.processed_file = output_path
                uploaded_file.save()

            elif file_ext.lower() in [".mp4", ".avi", ".mov"]:
                cap = cv2.VideoCapture(file_path)
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(output_path, fourcc, int(cap.get(5)),
                                      (int(cap.get(3)), int(cap.get(4))))

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    results = model(frame)
                    for result in results:
                        frame = result.plot()
                    out.write(frame)

                cap.release()
                out.release()

                uploaded_file.processed_file = output_path
                uploaded_file.save()

            return redirect("result", uploaded_file.id)
    else:
        form = FileUploadForm()
    return render(request, "upload.html", {"form": form})

def result(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        return render(request, "result.html", {"file": uploaded_file})
    except UploadedFile.DoesNotExist:
        return HttpResponse("File not found.", status=404)

def download_video_view(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(id=file_id)
        file_path = uploaded_file.processed_file.path  # Get the actual file path
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
        else:
            return HttpResponse("File not found.", status=404)
    except UploadedFile.DoesNotExist:
        return HttpResponse("File not found.", status=404)