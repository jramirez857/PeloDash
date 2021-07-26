import logging


class WorkoutsInserter:
    def __init__(self, workouts_collection) -> None:
        self.workouts_collection = workouts_collection

    def workout_exists(self, workout) -> bool:
        if self.workouts_collection.count() != 0:
            return self.workouts_collection.count_documents(
                {'summary.created_at': workout['summary']['created_at']}
            ) != 0
        else:
            return False

    def insert_workout(self, workout) -> list:
        return self.workouts_collection.insert_one(workout)

    def insert_recent_workouts(self, workouts) -> None:
        inserted_workouts = [self.insert_workout(workout) for workout in workouts
                             if not self.workout_exists(workout)]
        logging.debug(f"Inserted {len(inserted_workouts)} workout(s)")
        logging.debug(f"Found {len(workouts) - len(inserted_workouts)} duplicate workouts")

    def run(self, workouts):
        logging.basicConfig(
            level=logging.DEBUG,
            filename="../db.log",
            filemode="w",
            format="%(name)s - %(levelname)s - %(message)s",
        )
        self.insert_recent_workouts(workouts)
