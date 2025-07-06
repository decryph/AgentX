# test_calendar.py

from datetime import datetime, timedelta
from gcalendar import book_appointment

from datetime import timezone
start = datetime.now(timezone.utc) + timedelta(days=1, hours=5)
end = start + timedelta(hours=1)

link = book_appointment("TailorTalk Booking", start, end)
print("Event created:", link)

