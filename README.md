# data_extraction
See requirements.txt for dependancies.

Launch main.py to begin the scrapping.
Edit groups.json to choose the groups to scrape.
Edit config.json for various configurations.
	Date, multipliers and misc may need to be changed to match the text of your facebook's language, they are used to have a correct scrapping of date, KPIs and long texts.
	It never happened during our testing but the provided account might be banned for bot behaviour, if needed use "email": "dataextracproject@gmail.com", "password": "DauphineIASD1!" instead.
	Timings may be ajusted according to your internet connection, 4 seconds was enough to wait for pages to load successfuly on my side, you can also change the timeout.
