import requests
import csv


class PelotonLoginException(Exception):
    pass


class PeloDash:
    def __init__(self, username, password):
        self.base_url = 'https://api.onepeloton.com'
        self.s = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'pelodash'
        }

        self.userid = None
        self.instructor_id_dict = {}

        self.login(username, password)

    def login(self, username, password):
        auth_login_url = '%s/auth/login' % self.base_url
        auth_payload = {
            'username_or_email': username,
            'password': password
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'pyloton'
        }
        resp = self.s.post(
            auth_login_url,
            json=auth_payload, headers=headers, timeout=10).json()

        if (('status' in resp) and (resp['status'] == 401)):
            raise PelotonLoginException(resp['message'] if ('message' in resp)
                  else "Login Failed")

        self.userid = resp['user_id']
    
    def get_workouts_csv(self):
        workouts_url = '%s/api/user/%s/workout_history_csv?timezone=America/New_York' % (self.base_url, self.userid)
        resp = self.s.get(workouts_url, headers=self.headers, timeout=10).text
        writer = csv.writer(open('workouts.csv', 'w'))
        for row in csv.reader(resp.splitlines()):
            writer.writerow(row)
        return resp
