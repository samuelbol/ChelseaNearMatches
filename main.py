import os
from datetime import datetime

import pytz
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from keep_alive import keep_alive

keep_alive()

API_URL = "https://footapi7.p.rapidapi.com/api/team/38/matches/near"
BOT_TOKEN = os.environ.get("bot_token")
CHAT_ID = os.environ.get("chat_id")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

API_HEADERS = {
    "X-RapidAPI-Key": os.environ.get("x-rapidapi-key"),
    "X-RapidAPI-Host": "footapi7.p.rapidapi.com"
}

HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36"
}


def date_time(time_stamp):
    return datetime.fromtimestamp(time_stamp, tz=None)


def get_match_data():
    try:
        response = requests.get(API_URL, headers=API_HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions:
        print(f"Error: Unable to fetch data.")
        return None


def format_match_message(match, match_type):
    if match:
        tournament = match["tournament"]["name"]
        round_info = match["roundInfo"].get("name") if match_type.lower() == "previous" else match["roundInfo"].get(
            "round", "name")
        home_team = match["homeTeam"]["shortName"]
        away_team = match["awayTeam"]["shortName"]

        message = f"🏆 {tournament} - {round_info}\n\n"

        if match_type.lower() == "previous":
            home_score = match["homeScore"]["current"]
            away_score = match["awayScore"]["current"]
            message += f"🏠 *{home_team} {home_score} - {away_score} {away_team}* 🚌"

        if match_type.lower() == "next":
            start_timestamp = match["startTimestamp"]
            start_date = date_time(start_timestamp).strftime("%a, %d %b")
            start_time = date_time(start_timestamp).strftime("%H:%M")
            message += f"🏠 *{home_team} 🆚 {away_team}* 🚌"

            message += f"\n\n📅 _{start_date}\n⏰ {start_time} (GMT)_"

        return message

    else:
        return f"No {match_type} match data available."


def send_fixture_to_telegram(message):
    response = requests.post(BASE_URL + "sendMessage",
                             json={
                                 "chat_id": CHAT_ID,
                                 "parse_mode": "Markdown",
                                 "text": message,
                             })

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print(
            f"Message sending failed. Status code: {response.text}")


def main():
    match_data = get_match_data()

    if match_data:
        previous_match_data = match_data.get('previousEvent')
        next_match_data = match_data.get('nextEvent')

        previous_match = format_match_message(previous_match_data, 'Previous')
        next_match = format_match_message(next_match_data, 'Next')

        combined_message = f"🔍 *Chelsea's Last Game*\n{previous_match}\n\n---\n\n📅 *Upcoming Fixture*\n{next_match}\n\n" \
                           f"📲 @JustCFC"

        print(combined_message)

        send_fixture_to_telegram(combined_message)


if __name__ == "__main__":
    nigerian_timezone = pytz.timezone('Africa/Lagos')
    scheduler = BlockingScheduler(timezone=nigerian_timezone)

    # Schedule the job to run daily at 10 am Nigerian time
    scheduler.add_job(main, 'cron', hour=10, minute=0)
    # scheduler.start()
    main()
