# Scrape the channel page and extract the video information
import requests
from bs4 import BeautifulSoup

channel_url = os.environ['CHANNEL_URL']
response = requests.get(channel_url)
soup = BeautifulSoup(response.content, 'html.parser')
video_elements = soup.select('ytd-grid-video-renderer')
latest_video_id = video_elements[0]['video-id']

# Compare the latest video ID to the last video ID
if latest_video_id != LAST_VIDEO_ID:
  # Do something with the new video, e.g. send a notification
  print(f'New video detected: {latest_video_id}')

  # Save the latest video ID to file
  echo "$latest_video_id" > "$LAST_VIDEO_FILE"
else:
  print('No new videos detected')
