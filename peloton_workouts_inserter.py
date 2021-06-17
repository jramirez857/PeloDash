import pyloton_scraper
from pymongo import MongoClient

class WorkoutsInserter:
    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
    
    def connect_to_db(self) -> None:
        client = MongoClient(self.host, self.port)
        self.db = client.PeloDash

    @staticmethod
    def get_workouts():
        return pyloton_scraper.main()

    def insert_workouts(self) -> None:
        for workout in WorkoutsInserter.get_workouts():
            workouts = self.db.workouts
            workout_id = workouts.insert_one(workout).inserted_id
            print(workout_id)

def main() -> None:
    inserter = WorkoutsInserter(host='localhost', port=27017)
    inserter.connect_to_db()
    inserter.insert_workouts()

if __name__ == '__main__':
    main()
