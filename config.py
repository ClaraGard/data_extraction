class Config:
    def __init__(self, account, date, multipliers, timings, misc):
        self.account = account
        self.date = date
        self.multipliers = multipliers
        self.timings = timings
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
    
    class Misc:
        def __init__(self, see_more):
            self.see_more = see_more