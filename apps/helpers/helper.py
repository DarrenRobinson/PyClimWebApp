class Helper():
    __shared_state = {}
    def __init__(self):
        self.__dict__ = self.__shared_state
        self.features = []
        self.time_var = {'start_month': 1, 'start_day': 1, 'end_month': 12, 'end_day': 31, 'start_hour': 1, 'end_hour': 24}
