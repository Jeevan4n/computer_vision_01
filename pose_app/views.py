import cv2
import numpy as np
import os
from ultralytics import YOLO

from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.conf import settings

from .forms import VideoUploadForm
from .models import UploadedVideo

# -----------------------------------------------------------------------------
# Load YOLO Models (update the paths as needed)
# -----------------------------------------------------------------------------
custom_model = YOLO(r"D:\ZANGO-Projects\yolo_pose_project\computer_vision_01\best.pt")
pose_model = YOLO("yolov8n-pose.pt")

# -----------------------------------------------------------------------------
# Utility Functions (from your sample code)
# -----------------------------------------------------------------------------
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def classify_pose(keypoints, frame_height):
    if keypoints is None or len(keypoints) < 17:
        return ["Unknown"]

    # Unpack keypoints (assuming the first 17 follow this order)
    nose, left_eye, right_eye, left_ear, right_ear = keypoints[:5]
    left_shoulder, right_shoulder, left_elbow, right_elbow = keypoints[5:9]
    left_wrist, right_wrist, left_hip, right_hip = keypoints[9:13]
    left_knee, right_knee, left_ankle, right_ankle = keypoints[13:17]

    detected_actions = []

    # Calculate key angles
    left_arm_angle = calculate_angle(left_hip, left_shoulder, left_elbow)
    right_arm_angle = calculate_angle(right_hip, right_shoulder, right_elbow)
    bending_angle = calculate_angle(left_shoulder, left_hip, left_knee)
    leaning_angle = calculate_angle(left_shoulder, right_shoulder, right_hip)
    climbing_angle = calculate_angle(left_elbow, left_knee, left_ankle)
    left_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_leg_angle = calculate_angle(right_hip, right_knee, right_ankle)

    # Detect Bending
    if bending_angle < 130:
        detected_actions.append("Bending")

    # Detect arm raising
    if left_arm_angle > 50:
        detected_actions.append("Left Arm Raised")
    if right_arm_angle > 50:
        detected_actions.append("Right Arm Raised")

    # Detect Running (based on knee height difference and arm angles)
    if ((110 <= left_leg_angle <= 170 and right_knee[1] < left_knee[1]) or
        (110 <= right_leg_angle <= 170 and left_knee[1] < right_knee[1])) and \
       (50 <= left_arm_angle <= 140 or 50 <= right_arm_angle <= 140):
        detected_actions.append("Running")

    # Detect Lying on the Floor (if hips and shoulders are close to the ground)
    hip_avg_y = (left_hip[1] + right_hip[1]) / 2
    shoulder_avg_y = (left_shoulder[1] + right_shoulder[1]) / 2
    if hip_avg_y < 0.9 * frame_height and shoulder_avg_y < 0.9 * frame_height:
        detected_actions.append("Lying on the Floor")

    # Detect Touching Face (if a wrist is close to the face keypoints)
    if (np.linalg.norm(left_wrist - nose) < 50 or np.linalg.norm(right_wrist - nose) < 50 or
        np.linalg.norm(left_wrist - left_eye) < 50 or np.linalg.norm(right_wrist - right_eye) < 50 or
        np.linalg.norm(left_wrist - left_ear) < 50 or np.linalg.norm(right_wrist - right_ear) < 50):
        detected_actions.append("Touching Face")

    # Detect Jumping (if ankles are positioned higher than a threshold relative to the frame)
    if left_ankle[1] > 0.1 * frame_height and right_ankle[1] > 0.1 * frame_height:
        detected_actions.append("Jumping")

    # Detect Leaning (based on the shoulder-hip alignment)
    if leaning_angle < 80:
        detected_actions.append("Leaning Forward")
    elif leaning_angle > 100:
        detected_actions.append("Leaning Backward")

    # Detect Climbing (if the climbing angle is low and there is a noticeable knee-hip difference)
    if climbing_angle < 100 and abs(left_knee[1] - left_hip[1]) > 50:
        detected_actions.append("Climbing")

    return detected_actions if detected_actions else ["Standing"]

def process_video(video_path, output_path):
    """
    Reads the input video, processes each frame by performing object detection and pose estimation,
    annotates the frame with detected actions and keypoints, and writes the output video.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video file:", video_path)
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run object detection using the custom model
        obj_results = custom_model(frame)
        frame_with_boxes = obj_results[0].plot()  # Draw bounding boxes on the frame

        # Run pose estimation using the pose model
        pose_results = pose_model(frame_with_boxes)
        for result in pose_results:
            if hasattr(result, "keypoints") and result.keypoints is not None:
                keypoints = result.keypoints.xy.cpu().numpy()

                # Process each set of keypoints
                for kp in keypoints:
                    actions = classify_pose(kp, frame_height)
                    y_offset = 50  # Vertical offset for text labels
                    for action in actions:
                        cv2.putText(frame_with_boxes, action, (50, y_offset),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        y_offset += 40

                    # Optionally log detected actions to the console
                    print("Detected Actions:", ', '.join(actions))

                    # Draw keypoints on the frame
                    for x, y in kp:
                        cv2.circle(frame_with_boxes, (int(x), int(y)), 5, (0, 255, 0), -1)

        out.write(frame_with_boxes)

        # If you wish to display frames for debugging, uncomment these lines:
        # cv2.imshow("Processed Frame", frame_with_boxes)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Video processing completed. Output saved to:", output_path)

# -----------------------------------------------------------------------------
# Django Views
# -----------------------------------------------------------------------------
def upload_video(request):
    """
    View to handle video file uploads and process them using the YOLO models.
    """
    if request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded video instance
            video_instance = form.save()
            video_path = video_instance.video_file.path  # Adjust field name as needed

            # Construct output path (appending "_output" before the extension)
            file_name, file_ext = os.path.splitext(video_path)
            output_path = file_name + "_output" + file_ext

            # Process the video with the defined function
            process_video(video_path, output_path)

            # Save the processed file path to the model instance (assumes a field like "processed_video")
            video_instance.processed_video = output_path
            video_instance.save()

            return redirect("video_result", video_id=video_instance.id)
    else:
        form = VideoUploadForm()
    return render(request, "pose_app/upload.html", {"form": form})

def video_result(request, video_id):
    """
    View to display details about the processed video.
    """
    try:
        video_instance = UploadedVideo.objects.get(id=video_id)
        return render(request, "pose_app/result.html", {"video": video_instance})
    except UploadedVideo.DoesNotExist:
        return HttpResponse("Video not found.", status=404)

def download_video(request, video_id):
    """
    View to allow users to download the processed video file.
    """
    try:
        video_instance = UploadedVideo.objects.get(id=video_id)
        file_path = video_instance.processed_video.path  # Adjust according to your model field
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type="video/mp4")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
        else:
            return HttpResponse("File not found.", status=404)
    except UploadedVideo.DoesNotExist:
        return HttpResponse("Video not found.", status=404)