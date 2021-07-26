from workouts_connector import WorkoutConnector


class WorkoutsQuerier:
    def __init__(self):
        self.workouts_collection = WorkoutConnector().workouts

    def get_unique_ride_instructors(self):
        unique_instructors = self.workouts_collection.distinct(field="details.ride.instructor_id")
        return [
            instructor
            for instructor in unique_instructors
            if instructor is not None
        ]

    def get_num_rides_with_instructor(self, instructor_id):
        return self.workouts_collection.count_documents(
            {
                "details.ride.instructor_id": instructor_id
            }
        )
