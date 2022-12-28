#!./venv/bin/python
import os

from dotenv import load_dotenv

load_dotenv()
import csv
from pathlib import Path, PurePath

from pylotoncycle import PylotonCycle


def GetWorkoutCSV(
    connection: PylotonCycle, path: str = "", timezone: str = "America/New_York"
) -> dict:
    workouts_url = f"{connection.base_url}/api/user/{connection.userid}/workout_history_csv?timezone={timezone}"
    resp = connection.s.get(workouts_url, headers=connection.headers, timeout=10)
    p = Path(path).joinpath("workouts.csv") if path else PurePath("workouts.csv")
    writer = csv.writer(open(p, "w"))
    for row in csv.reader(resp.text.splitlines()):
        writer.writerow(row)
    print(f"Workouts saved to {r['path']}")
    return {"response": resp, "path": p}


if __name__ == "__main__":
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]

    conn = PylotonCycle(username, password)
    r = GetWorkoutCSV(connection=conn, timezone="America/New_York")