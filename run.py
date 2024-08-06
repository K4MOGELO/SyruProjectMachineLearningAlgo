import requests

# Define the URL of the Flask endpoint
url = 'http://127.0.0.1:5000/api/upload'

# Path to the image file you want to upload
file_path = 'image4.jpg'

# Prepare the file to be sent in the request
files = {'image': open(file_path, 'rb')}

# Send the POST request with the file
response = requests.post(url, files=files)

# Print the response from the server
print(response.json())

