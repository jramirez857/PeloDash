from workouts_connector import WorkoutConnector
from workouts_inserter import WorkoutsInserter
from api.peloton_api_wrapper import PelotonAPIWrapper
from config.config_peloton import API_PELOTON_USERNAME, API_PELOTON_PASSWORD
import logging


class WorkoutsPopulater:
    def __init__(self) -> None:
        self.workouts_collection = WorkoutConnector()
        self.workouts_inserter = WorkoutsInserter(workouts_collection=self.workouts_collection)
        self.api_wrapper = PelotonAPIWrapper(un=API_PELOTON_USERNAME, pw=API_PELOTON_PASSWORD)

    def get_num_workouts_in_collection(self):
        return self.workouts_collection.workouts.count()

    def update_db(self):
        logging.basicConfig(
            level=logging.DEBUG,
            filename="../db.log",
            filemode="w",
            format="%(name)s - %(levelname)s - %(message)s",
        )
        num_workouts_in_db = self.get_num_workouts_in_collection()
        logging.debug(f'Found {num_workouts_in_db} workouts in collection.')
        num_missing_workouts = self.api_wrapper.get_total_user_workouts() - num_workouts_in_db
        logging.debug(f'Inserting {num_missing_workouts} workouts into database')
        missing_workouts = self.api_wrapper.get_workouts(num_missing_workouts)
        logging.debug(f'Retrieved {len(missing_workouts)} workouts from API.')
        self.workouts_inserter.insert_recent_workouts(missing_workouts)
        logging.debug(f'Finished inserting workouts.')


if __name__ == "__main__":
    WorkoutsPopulater().update_db()
