## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment tool (optional but recommended)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/computer_vision_01.git
   cd computer_vision_01
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv myvenv
   source myvenv/bin/activate  # On Windows use `myvenv\Scripts\activate`
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

## Running the Application

1. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

2. **Open your browser and navigate to:**
   ```
   http://127.0.0.1:8000/
   ```

## Deployment

### Deploying to Render

1. **Create a `Procfile` in the root directory:**

   ```plaintext
   web: gunicorn yolo_pose_project.wsgi:application
   ```

2. **Push your code to GitHub:**

   ```bash
   git add .
   git commit -m "Prepare project for deployment on Render"
   git push origin main
   ```

3. **Create a new web service on Render:**

   - Go to the Render dashboard.
   - Click on "New" and select "Web Service".
   - Connect your GitHub account and select the repository.
   - Configure the web service:
     - **Name**: Choose a name for your service.
     - **Region**: Select a region.
     - **Branch**: Select the branch you want to deploy (e.g., `main`).
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn yolo_pose_project.wsgi:application`

4. **Add environment variables in the Render dashboard:**

   - `DJANGO_SETTINGS_MODULE`: `yolo_pose_project.settings`
   - `SECRET_KEY`: A secret key for your Django project (generate one using Django's `get_random_secret_key` function).
   - `DATABASE_URL`: The URL for your database (if using a database service like PostgreSQL).

5. **Deploy the service:**
   - Click "Create Web Service" to start the deployment process.
   - Monitor the build and deployment logs in the Render dashboard.

## Usage

1. **Upload an image or video:**

   - Navigate to the upload page.
   - Select an image or video file and click "Upload".

2. **View the results:**

   - After processing, you will be redirected to the results page.
   - View the processed image or video.

3. **Download the processed video:**
   - Click the download link to download the processed video.

## Contributing

1. **Fork the repository.**
2. **Create a new branch:**
   ```bash
   git checkout -b my-feature-branch
   ```
3. **Make your changes and commit them:**
   ```bash
   git commit -m "Add some feature"
   ```
4. **Push to the branch:**
   ```bash
   git push origin my-feature-branch
   ```
5. **Submit a pull request.**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
