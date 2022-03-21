from PIL import Image, ImageFont, ImageDraw
from init_cal_service import Create_Service
from datetime import datetime


CLIENT_SECRET_FILE = 'client_secret_calendar_api.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
DISCOVERY_URL = 'https://www.googleapis.com/calendar/v3/calendars/primary/events'
endpoint = 'calget_endpoint'
SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly']


cal_service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, DISCOVERY_URL, endpoint, SCOPES)

def cal_query():
  page_token = None
  todaysdate = datetime.now()
  start_rfc_date = convert_to_RFC_datetime(todaysdate.year, todaysdate.month, todaysdate.day, 0, 0)
  end_rfc_date = convert_to_RFC_datetime(todaysdate.year, todaysdate.month, todaysdate.day, 23, 59, 59)
  print('Todays Calendar')
  print(todaysdate)
  while True:
    cal_query_result = ''
    events = cal_service.events().list(calendarId='primary', pageToken=page_token, timeMin=start_rfc_date, timeMax=end_rfc_date, orderBy='startTime', singleEvents=True).execute()
    for event in events['items']:
        cal_query_result = cal_query_result + event.get('summary') + '     ' + datetime.fromisoformat(event.get('start', {}).get('dateTime')).strftime("%I:%M %p") + '   ' + datetime.fromisoformat(event.get('end', {}).get('dateTime')).strftime("%I:%M %p") + '\n'
    print(cal_query_result)
    page_token = events.get('nextPageToken')
    if not page_token:
      return cal_query_result


def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0, seconds=0):
  dt = datetime(year, month, day, hour, minute, seconds).isoformat() + '-00:00'
  return dt


def main():
    current_date = datetime.now().strftime("%B %d, %Y")
    print(current_date)
    my_image = Image.open("bg/autumn.jpg")
    header_font = ImageFont.truetype('fonts/oswald-bold.ttf', 100)
    date_font = ImageFont.truetype('fonts/oswald-bold.ttf', 75)
    content_font = ImageFont.truetype('fonts/oswald-bold.ttf', 50)
    image_editable = ImageDraw.Draw(my_image)
    image_editable.text((45, 0), 'Todays Calendar', (245, 155, 66), font=header_font)
    image_editable.text((45, 150), str(current_date), (245, 155, 66), font=date_font)
    image_editable.text((45,300), cal_query(), (245, 155, 66), font=content_font)
    my_image.save("CacheFolder/result.jpg")

if __name__ == "__main__":
    main()