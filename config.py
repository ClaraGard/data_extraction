import pandas as pd

def setconfig():
    config_json = pd.read_json('config.json')
    account = Config.Account(config_json["account"]["email"], config_json["account"]["password"])
    date = Config.Date(config_json["date"]["years"], config_json["date"]["months"], config_json["date"]["weeks"], config_json["date"]["days"], config_json["date"]["hours"], config_json["date"]["minutes"], config_json["date"]["months of the year"])
    multipliers = Config.Multipliers(config_json["multipliers"]["thousands"], config_json["multipliers"]["millions"], config_json["multipliers"]["millions"])
    timings = Config.Timings(config_json["timings"]["time to load page"], config_json["timings"]["timeout"])
    files = Config.Files(config_json["files"]["input"], config_json["files"]["output"])
    misc = Config.Misc(config_json["misc"]["see more"], config_json["misc"]["know more"])
    config = Config(account, date, multipliers, timings, files, misc)
    return config


class Config:
    def __init__(self, account, date, multipliers, timings, files, misc):
        self.account = account
        self.date = date
        self.multipliers = multipliers
        self.timings = timings
        self.files = files
        self.misc = misc

    class Account:
        def __init__(self, email, password):
            self.email = email
            self.password = password

    class Date:
        def __init__(self, years, months, weeks, days, hours, minutes, months_of_the_year):
            self.years = years
            self.months = months
            self.weeks = weeks
            self.days = days
            self.hours = hours
            self.minutes = minutes
            self.months_of_the_year = months_of_the_year

    class Multipliers:
        def __init__(self, thousands, millions, billions):
            self.thousands = thousands
            self.millions = millions
            self.billions = billions
    
    class Timings:
        def __init__(self, time_to_load, timeout):
            self.time_to_load = time_to_load
            self.timeout = timeout

    class Files:
        def __init__(self, input, output):
            self.input = input
            self.output = output
    
    class Misc:
        def __init__(self, see_more, know_more):
            self.see_more = see_more
            self.know_more = know_more

config = setconfig()
