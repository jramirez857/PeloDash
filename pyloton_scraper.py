import pylotoncycle
import config_peloton as cfg

class PylotonScraper:
    def __init__(self, username, password, num_workouts=10, **kwargs) -> None:
        self.username = username
        self.password = password
        self.num_workouts = num_workouts
        if kwargs:
            pass
    
    def connect_to_pyloton(self) -> object:
        self.conn = pylotoncycle.PylotonCycle(self.username, self.password)
    
    def get_recent_workouts(self) -> list:
        workouts = self.conn.GetRecentWorkouts(num_workouts=self.num_workouts)
        return workouts
    
def main() -> list:
    scraper = PylotonScraper(username=cfg.API_PELOTON_USERNAME, password=cfg.API_PELOTON_PASSWORD)
    scraper.connect_to_pyloton()
    return scraper.get_recent_workouts()

if __name__ == '__main__':
    main()
