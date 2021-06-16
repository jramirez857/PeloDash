import configparser

def get_credentials():
    config = configparser.ConfigParser(interpolation=None)
    config.read("./config/peloton.ini")
    username = config.get('PeloJose', 'username')
    password = config.get('PeloJose', 'password')
    return (username, password)
