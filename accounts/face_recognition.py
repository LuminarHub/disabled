import os
import cv2
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class FaceRecognition:
    def __init__(self, known_faces_dir='student image'):
        """
        Initialize face recognition system
        :param known_faces_dir: Directory to store known face images

        Set up a directory for known faces:

        Creates a folder named student image inside Django's MEDIA_ROOT to store registered faces.
        os.makedirs(self.known_faces_dir, exist_ok=True) ensures the directory exists (creates it if it doesn't).
        Load the Haar Cascade Classifier:

        Uses OpenCV's pre-trained Haar Cascade (haarcascade_frontalface_default.xml) to detect faces in images.
        """
        self.known_faces_dir = os.path.join(settings.MEDIA_ROOT, known_faces_dir)
        os.makedirs(self.known_faces_dir, exist_ok=True)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect_and_crop_face(self, image_path):
        """
        Detect and crop face from an image
        :param image_path: Path to the input image
        :return: Cropped face image or None

        Reads the Image:

        Loads the image from the given image_path.
        If the image cannot be read (like a corrupted file), it returns None.
        Convert to Grayscale:

        Converts the image to grayscale (simpler and faster for face detection).
        Detect Faces:

        Uses OpenCV’s detectMultiScale() to identify faces in the image.
        Parameters:
        scaleFactor=1.1: Image is scaled down by 10% at each pass to detect faces of different sizes.
        minNeighbors=5: Higher values mean fewer detections but more accuracy.
        minSize=(30, 30): Ignores objects smaller than 30x30 pixels.
        Crop and Resize the Face:

        If faces are detected, it crops the first detected face (assumes it's the main face).
        Resizes the face to 100x100 pixels to standardize its size.
        Returns: Cropped and resized face image. If no face is detected, it returns None.
        """
        img = cv2.imread(image_path)
        if img is None:
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        if len(faces) == 0:
            return None
        (x, y, w, h) = faces[0]
        face_crop = gray[y:y+h, x:x+w]
        face_crop_resized = cv2.resize(face_crop, (100, 100))   
        return face_crop_resized


    def compare_faces(self, face1, face2):
        """
        Compare two face images using template matching
        :param face1: First face image
        :param face2: Second face image
        :return: Similarity score


        Normalize the Images:

        Scales both face images to a range of 0-255 for consistency.
        Template Matching:

        Compares the two face images using cv2.matchTemplate.
        Uses cv2.TM_CCOEFF_NORMED to calculate a similarity score (between -1 and 1).
        Return Similarity:

        The similarity score indicates how similar the two faces are.
        Higher score (closer to 1) = Higher similarity.
        Returns: Similarity score between face1 and face2.
        """
        face1_norm = cv2.normalize(face1, None, 0, 255, cv2.NORM_MINMAX)
        face2_norm = cv2.normalize(face2, None, 0, 255, cv2.NORM_MINMAX)        
        result = cv2.matchTemplate(face1_norm, face2_norm, cv2.TM_CCOEFF_NORMED)
        similarity = result[0][0]      
        return similarity


    def register_face(self, username, image_path):
        """
        Register a user's face
        :param username: Username to associate with the face
        :param image_path: Path to the user's face image
        :return: Boolean indicating success


        Detect and Crop Face:

        Uses detect_and_crop_face() to crop the face from the input image.
        If no face is detected, it returns False.
        Save the Face Image:

        Names the file as {username}_face.jpg.
        Saves the face in the known faces directory.
        Returns:

        True if registration was successful.
        False if no face was detected.
        """
        # Detect and crop face
        face = self.detect_and_crop_face(image_path)
        if face is None:
            return False
        
        # Save the face image
        face_filename = f"{username}_face.jpg"
        face_save_path = os.path.join(self.known_faces_dir, face_filename)
        cv2.imwrite(face_save_path, face)
        
        return True

    def authenticate_by_face(self, image_path):
        """
        Authenticate a user by face
        :param image_path: Path to the input image
        :return: Username if authenticated, None otherwise

        Detect and Crop Input Face:

        Detects the face from the input image.
        If no face is found, it returns None.
        Check Against Known Faces:

        Loops through all images in the known faces directory.
        Skips files that are not images (.jpg, .png, etc.).
        Compare with Known Faces:

        Detects and crops the face from each known face image.
        Compares it with the input face using compare_faces().
        Similarity Check:

        If the similarity score is greater than 0.4, it's considered a match.
        Extracts the username from the image filename (e.g., "john_face.jpg" → "john").
        Return Best Match:

        Sorts matches by similarity and returns the username with the highest similarity.
        Returns:

        The username of the best match.
        None if no matches are found.


        """
        # Detect and crop input face
        input_face = self.detect_and_crop_face(image_path)
        if input_face is None:
            return None

        matches = []

        for filename in os.listdir(self.known_faces_dir):
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                continue

            try:
                known_face_path = os.path.join(self.known_faces_dir, filename)
                known_face = self.detect_and_crop_face(known_face_path)
                
                if known_face is not None:
                    # Compare faces
                    similarity = self.compare_faces(input_face, known_face)
                    print(f"Comparing with {filename}: Similarity = {similarity}")

                    # Adjust threshold as needed
                    if similarity > 0.4:
                        # Extract username from filename
                        username = filename.split('_')[0]
                        matches.append((username, similarity))

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            print(f"Best match: {matches[0][0]} with similarity {matches[0][1]}")
            return matches[0][0]

        return None