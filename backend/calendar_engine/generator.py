from datetime import datetime, timedelta, timezone
from typing import List

from icalendar import Alarm, Calendar, Event

from backend.models.contest import Contest


class CalendarGenerator:
    """
    Constructs RFC-5545 compliant iCalendar (.ics) feeds.
    """

    @staticmethod
    def generate_ics(
        contests: List[Contest],
        calendar_name: str = "ContestPulse Contests",
        reminder_minutes: int = 15,
        alarm_name: str = "🚨 ContestPulse Alarm",
    ) -> bytes:
        cal = Calendar()

        cal.add("prodid", "-//ContestPulse//Coding Contest Agent//EN")
        cal.add("version", "2.0")
        cal.add("calscale", "GREGORIAN")
        cal.add("method", "PUBLISH")
        cal.add("x-wr-calname", calendar_name)
        cal.add("x-wr-timezone", "UTC")
        cal.add("refresh-interval;value=duration", "PT4H")
        cal.add("x-published-ttl", "PT4H")

        now_utc = datetime.now(timezone.utc)
        alarm_label = alarm_name.strip() if alarm_name else "🚨 ContestPulse Alarm"

        for contest in contests:
            event = Event()

            event.add("uid", f"{contest.id}@contestpulse")
            event.add("summary", f"[{contest.platform.capitalize()}] {contest.title}")
            
            description = (
                f"Platform: {contest.platform.capitalize()}\n"
                f"Category: {contest.division or 'Open'}\n"
                f"Contest Link: {contest.url}\n\n"
                f"Alarm Label: {alarm_label}\n"
                f"Automated reminder set by ContestPulse."
            )
            event.add("description", description)
            event.add("url", contest.url)
            event.add("dtstart", contest.start_time)
            event.add("dtend", contest.end_time)
            event.add("dtstamp", now_utc)

            # Native Phone Alarm (VALARM)
            alarm = Alarm()
            alarm.add("action", "DISPLAY")
            alarm.add(
                "description",
                f"{alarm_label}: {contest.title} starts in {reminder_minutes} minutes! Time to code."
            )
            alarm.add("trigger", -timedelta(minutes=reminder_minutes))
            event.add_component(alarm)

            cal.add_component(event)

        return cal.to_ical()
