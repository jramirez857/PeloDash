import pylotoncycle
import peloton_parser

username, password = peloton_parser.get_credentials()
conn = pylotoncycle.PylotonCycle(username, password)
workouts = conn.GetRecentWorkouts(1)
print(workouts)