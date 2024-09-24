import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

logging.basicConfig(
    filename='/Users/rohannankani/Desktop/programming/temp/check_course.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

biol239 = 'https://classes.uwaterloo.ca/cgi-bin/cgiwrap/infocour/salook.pl?sess=1249&level=under&subject=BIOL&cournum=239'

def check_course_availability(url):
    response = requests.get(url)

    if response.status_code != 200:
        logging.debug("Failed to fetch the webpage.")
        return False

    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table')
    
    table_rows = table.find_all('tr')
    
    for row in table_rows:
        cells = row.find_all('td', align='center')
        if len(cells) > 6:
            capacity = cells[4].text.strip()
            enrolled = cells[5].text.strip()
            if capacity.isdigit() and enrolled.isdigit():
                capacity = int(capacity)
                available_spots = capacity - int(enrolled)
                logging.debug(f"Capacity: {capacity}, Enrolled: {enrolled}, Available Spots: {available_spots}")
                
                return available_spots
            
def send_email_alert(available_spots):
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECEIVER_EMAIL')
    password = os.getenv('EMAIL_PASSWORD')

    subject = "Course Availability Alert"
    body = f"There are {available_spots} spots available in the course."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        logging.debug("Email sent successfully!")
    except Exception as e:
        logging.debug(f"Failed to send email: {e}")

biol239Spots = check_course_availability(biol239)

if biol239Spots > 0:
    logging.debug(f"Alert! There are spots available in the BIOL 239 course.")
    send_email_alert(biol239Spots)
else:
    logging.debug("Course is not available.")
