import requests
import logging

logging.basicConfig(
            level=logging.DEBUG,
            filename="scraper.log",
            filemode="w",
            format="%(name)s - %(levelname)s - %(message)s",
        )


class PelotonLoginException(Exception):
    pass


class PelotonAPIWrapper:
    def __init__(self, un, pw):
        self.base_url = 'https://api.onepeloton.com'
        self.s = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'WorkoutsScraper'
        }
        self.username = un
        self.password = pw
        self.user = None
        self.instructors = {}
        self.authenticate()
        self.get_user_info()

    def authenticate(self):
        auth_login_url = f'{self.base_url}/auth/login'
        auth_payload = {
            'username_or_email': self.username,
            'password': self.password
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PeloDash'
        }
        resp = self.s.post(
            auth_login_url,
            json=auth_payload, headers=headers, timeout=10).json()

        if ('status' in resp) and (resp['status'] == 401):
            raise PelotonLoginException(resp['message'] if ('message' in resp)
                  else "Login Failed")

    def get_url(self, url):
        resp = self.s.get(url, timeout=10).json()
        return resp

    def get_user_info(self):
        self.user = self.get_url(url=f'{self.base_url}/api/me')

    def get_total_user_workouts(self):
        return self.user['total_workouts']

    def get_workout_summary_by_id(self, workout_id):
        url = f'{self.base_url}/api/workout/{workout_id}/summary'
        resp = self.get_url(url)
        return resp

    def get_workout_metrics_by_id(self, workout_id, frequency=50):
        url = f'{self.base_url}/api/workout/{workout_id}/performance_graph?every_n={frequency}'
        resp = self.get_url(url)
        return resp

    def get_workout_by_id(self, workout_id):
        url = f'{self.base_url}/api/workout/{workout_id}'
        resp = self.get_url(url)
        return resp

    def get_instructor_by_id(self, instructor_id):
        if instructor_id in self.instructors:
            return self.instructors[instructor_id]

        url = f'{self.base_url}/api/instructor/{instructor_id}'
        resp = self.get_url(url)
        self.instructors[instructor_id] = resp
        return resp

    def get_base_workout_url(self):
        return f'{self.base_url}/api/user/{self.user["id"]}/workouts?sort_by=-created'

    def _get_workout_details(self, workout_summary):
        return {
            'summary': workout_summary,
            'details': self.get_workout_by_id(workout_summary['id']),
            'performance_metrics': self.get_workout_metrics_by_id(workout_id=workout_summary['id'])
        }

    def get_workouts(self, num_workouts=None) -> list:
        '''
        Gets all workouts if number of workouts not specified
        '''

        if num_workouts is None:
            num_workouts = self.user['total_workouts']

        query_limit = 100
        total_pages = 1
        if num_workouts > query_limit:
            query_amount = query_limit
        else:
            query_amount = num_workouts
        total_pages += (num_workouts // query_amount)
        remaining_workouts = num_workouts
        workouts = []
        current_page = 0
        while remaining_workouts > 0 and current_page <= total_pages:
            logging.debug(
                f'Getting {remaining_workouts} workouts by requesting {query_amount} workouts')
            url = f'{self.get_base_workout_url()}&page={current_page}&limit={query_amount}'
            resp = self.s.get(url, timeout=10).json()
            current_workout_summaries = resp['data'][0:query_amount]
            for workout_summary in current_workout_summaries:
                workouts.append(self._get_workout_details(workout_summary))
            current_page += 1
            remaining_workouts -= query_amount
        logging.debug(f'All workouts fetched.')
        return workouts


if __name__ == '__main__':
    username = 'My_Peloton_User_or_Email'
    password = 'My_Peloton_Password'
    conn = PelotonAPIWrapper(username, password)
