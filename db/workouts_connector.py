from pymongo import MongoClient
from config.config_peloton import DB_HOST, DB_PORT

class WorkoutConnector:
    def __init__(self):
        self.conn = MongoClient(host=DB_HOST, port=DB_PORT)
        self.workouts = self.conn.PeloDash.workouts
