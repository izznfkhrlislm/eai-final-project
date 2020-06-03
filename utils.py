import requests
import json
from bs4 import BeautifulSoup
from http import HTTPStatus
from requests.exceptions import ConnectTimeout


class Covid19APIUtils:
    HOST_URL = "https://covid19.mathdro.id/api/"
    CONFIRMED_ACTION = "confirmed/"
    RECOVERED_ACTION = "recovered/"
    DEATHS_ACTION = "deaths/"
    DAILY_ACTION = "daily/"
    COUNTRIES_LIST_ACTION = "countries/"

    def __init__(self):
        self.requestObject = requests

    def get_countries_list_and_codes(self):
        try :
            countries_name_list = []
            countries_response = self.requestObject.get(
                self.HOST_URL + self.COUNTRIES_LIST_ACTION
            )
            
            if countries_response.status_code == HTTPStatus.OK:
                for country_data in countries_response.json()["countries"]:
                    country_dict = {
                        "name": country_data["name"],
                        "code": None if "iso2" not in list(country_data.keys()) else country_data["iso2"]
                    }
                    countries_name_list.append(country_dict)

            return countries_name_list
        
        except ConnectTimeout:
            return HTTPStatus.REQUEST_TIMEOUT
    
    def get_worldwide_stats(self):
        response = {}
        try:
            response_object = self.requestObject.get(
                self.HOST_URL
            )

            if response_object.status_code == HTTPStatus.OK:
                response = {
                    "confirmed_case": response_object.json()["confirmed"]["value"],
                    "recovered_case": response_object.json()["recovered"]["value"],
                    "deaths_case": response_object.json()["deaths"]["value"]
                }
            
            return response
        
        except ConnectTimeout:
            return HTTPStatus.REQUEST_TIMEOUT
    
    def get_stats_per_country(self, country):
        country_code_request = country + "/"
        response = {}
        try:
            response_object = self.requestObject.get(
                self.HOST_URL + self.COUNTRIES_LIST_ACTION + country_code_request
            )

            if response_object.status_code == HTTPStatus.OK:
                response = {
                    "country_code": country,
                    "confirmed_case": response_object.json()["confirmed"]["value"],
                    "recovered_case": response_object.json()["recovered"]["value"],
                    "deaths_case": response_object.json()["deaths"]["value"]
                }
            
            return response
        
        except ConnectTimeout:
            return HTTPStatus.REQUEST_TIMEOUT


class Covid19WebScrapperDataUtils:
    HOST_URL = "https://worldpopulationreview.com/"

    def __init__(self):
        self.website_request = requests.get(self.HOST_URL)
        self.scrapper = BeautifulSoup(self.website_request.content, 'html.parser')
    
    def get_worldwide_population_data_with_countries(self):
        worldwide_population_data = []
        worldwide_population_table = self.scrapper.find(
            'table', 
            class_='datatableStyles__StyledTable-bwtkle-1 cyosFW table table-striped'
        )
        
        for table_body_item in worldwide_population_table.find_all('tbody'):
            for row_content in table_body_item.find_all('tr'):
                country_name = row_content.find_all('td')[1].get_text()
                current_population = row_content.find_all('td')[2].get_text()
                country_area = row_content.find_all('td')[4].get_text()
                
                worldwide_population_data.append({
                    "country": country_name,
                    "population": current_population,
                    "area": country_area
                })
        
        return worldwide_population_data
    
    def get_total_worldwide_population(self):
        total_worldwide_population_scrap = self.scrapper.find(
            'span',
            class_='popNumber'
        )

        return total_worldwide_population_scrap.get_text().split(" ")[3]
                
            
if __name__ == "__main__":
    covidWrapper = Covid19WebScrapperDataUtils()
    print(covidWrapper.get_total_worldwide_population())
        
        