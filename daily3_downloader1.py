import requests
import csv
from datetime import datetime

url = "https://www.michiganlottery.com/api"

query = """
query Game($gameCode: String!, $startDateString: String!, $endDateString: String!) {
  gameByCode(code: $gameCode) {
    logicalGameIdentifier
    drawResultsBetweenDates(
      startDateString: $startDateString
      endDateString: $endDateString
    ) {
      drawDate
      drawSequence
      hasPayoutData
      isBonusDraw
      winningNumbers {
        drawNumbers
      }
    }
  }
}
"""

variables = {
    "gameCode": "T",
    "startDateString": "1990-07-01T04:00:00.000Z",
    "endDateString": "2026-07-01T04:00:00.000Z"
}

payload = {
    "operationName": "Game",
    "query": query,
    "variables": variables
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print("Status code:", response.status_code)

if response.status_code != 200:
    print("Something went wrong:")
    print(response.text)
    quit()

data = response.json()

draws = data["data"]["gameByCode"]["drawResultsBetweenDates"]

rows = []

for draw in draws:
    draw_date_raw = draw["drawDate"]
    draw_date = datetime.fromisoformat(draw_date_raw.replace("Z", "+00:00"))

    numbers = draw["winningNumbers"]["drawNumbers"]

    if not numbers or len(numbers) < 3:
        continue

    digit_1 = numbers[0]
    digit_2 = numbers[1]
    digit_3 = numbers[2]

    number_text = f"{digit_1}{digit_2}{digit_3}"

    rows.append({
        "date": draw_date.strftime("%Y-%m-%d"),
        "year": draw_date.year,
        "month": draw_date.month,
        "day": draw_date.day,
        "day_of_week": draw_date.strftime("%A"),
        "draw_sequence": draw["drawSequence"],
        "number": number_text,
        "digit_1": digit_1,
        "digit_2": digit_2,
        "digit_3": digit_3,
        "sum": digit_1 + digit_2 + digit_3,
        "is_double": len(set(numbers)) == 2,
        "is_triple": len(set(numbers)) == 1,
        "has_payout_data": draw["hasPayoutData"],
        "is_bonus_draw": draw["isBonusDraw"]
    })

filename = "daily_3_1990_to_2026.csv"

with open(filename, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Done!")
print("Rows saved:", len(rows))
print("File created:", filename)