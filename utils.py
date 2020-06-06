import requests
import json
from bs4 import BeautifulSoup
from http import HTTPStatus
from requests.exceptions import ConnectTimeout
from pika import ConnectionParameters, PlainCredentials, BlockingConnection


class Covid19MQUtils:
    MQ_EXCHANGE_TYPE = "direct"
    MQ_EXCHANGE_NAME = '1606875806'
    MQ_HOST = "152.118.148.95"
    MQ_PORT = 5672
    MQ_USERNAME = "0806444524"
    MQ_PASSWORD = "0806444524"
    MQ_VIRTUAL_HOST = "/0806444524"

    def __init__(self, routing_key, is_in_production=False):
        self.routing_key = routing_key
        self.pika_connection = BlockingConnection(
            ConnectionParameters(
                host=self.MQ_HOST,
                virtual_host=self.MQ_VIRTUAL_HOST,
                port=self.MQ_PORT,
                credentials=PlainCredentials(self.MQ_USERNAME, self.MQ_PASSWORD)
            )
        )
        self.connection_channel = self.pika_connection.channel()
        self.connection_channel.exchange_declare(
            exchange=self.MQ_EXCHANGE_NAME,
            exchange_type=self.MQ_EXCHANGE_TYPE
        )
    
    def send_message(self, message):
        self.connection_channel.basic_publish(
            exchange=self.MQ_EXCHANGE_NAME,
            routing_key=self.routing_key,
            body=message
        )
    
    def close_connection(self):
        self.pika_connection.close()

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
        countries_name_list = []
        try :
            countries_response = self.requestObject.get(
                self.HOST_URL + self.COUNTRIES_LIST_ACTION
            )
            
            if countries_response.status_code == HTTPStatus.OK:
                for country_data in countries_response.json()["countries"]:
                    country_dict = {
                        "name": country_data["name"],
                        "code": country_data["name"].lower()
                    }
                    countries_name_list.append(country_dict)
        
        except ConnectTimeout:
            return HTTPStatus.REQUEST_TIMEOUT

        return countries_name_list
    
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
        
        except ConnectTimeout:
            return HTTPStatus.REQUEST_TIMEOUT

        return response

    def get_stats_per_country(self, country_code):
        response = {}
        try:
            country_code_request = country_code + "/"
            response_object = self.requestObject.get(
                self.HOST_URL + self.COUNTRIES_LIST_ACTION + country_code_request
            )
            
            if response_object.status_code == HTTPStatus.OK:
                response = {
                    "country_code": country_code,
                    "confirmed_case": response_object.json()["confirmed"]["value"] \
                        if response_object.json()["confirmed"]["value"] is not None or not 0 else "N/A",
                    "recovered_case": response_object.json()["recovered"]["value"] \
                        if response_object.json()["recovered"]["value"] is not None or not 0 else "N/A",
                    "deaths_case": response_object.json()["deaths"]["value"] \
                        if response_object.json()["deaths"]["value"] is not None or not 0 else "N/A"
                }
            else:
                response = {
                    "country_code": country_code,
                    "confirmed_case": "N/A",
                    "recovered_case": "N/A",
                    "deaths_case": "N/A",
                }
        
        except ConnectTimeout:
            return HTTPStatus.REQUEST_TIMEOUT

        return response

class Covid19WebScrapperDataUtils:
    HOST_URL = "https://worldpopulationreview.com/"

    def __init__(self):
        self.website_request = requests.get(self.HOST_URL)
        self.scrapper = BeautifulSoup(self.website_request.content, 'html.parser')
    
    def get_worldwide_population_data_with_countries(self):
        worldwide_population_data = {}
        worldwide_population_table = self.scrapper.find(
            'table', 
            class_='datatableStyles__StyledTable-bwtkle-1 cyosFW table table-striped'
        )
        
        for table_body_item in worldwide_population_table.find_all('tbody'):
            for row_content in table_body_item.find_all('tr'):
                country_name = row_content.find_all('td')[1].get_text()
                current_population = row_content.find_all('td')[2].get_text()
                country_area = row_content.find_all('td')[4].get_text()
                
                worldwide_population_data[country_name] = {
                    "country": country_name,
                    "population": current_population,
                    "area": country_area,
                }

        return worldwide_population_data
    
    def get_total_worldwide_population(self):
        total_worldwide_population_scrap = self.scrapper.find(
            'span',
            class_='popNumber'
        )

        return total_worldwide_population_scrap.get_text().split(" ")[3]
                
            
if __name__ == "__main__":
    covidWrapper = Covid19WebScrapperDataUtils()
    print(covidWrapper.get_worldwide_population_data_with_countries())