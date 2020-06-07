from flask import Flask, render_template, request, jsonify
from http import HTTPStatus
from utils import Covid19APIUtils, Covid19WebScrapperDataUtils, Covid19MQUtils

import threading
import json


app = Flask(__name__)
IS_PRODUCTION = False
ROUTING_KEY = "eai-routing-key"
MQ_WEBSOCKET_PORT = 15674

@app.route('/')
def showIndexPage():
    pika_connection = Covid19MQUtils(routing_key=ROUTING_KEY, is_in_production=IS_PRODUCTION)
    api_utils = Covid19APIUtils()
    scrapper_utils = Covid19WebScrapperDataUtils()

    retrieve_data_in_background(pika_connection, api_utils, scrapper_utils)

    return render_template(
        'index.html',
        mq_username=pika_connection.MQ_USERNAME,
        mq_password=pika_connection.MQ_PASSWORD,
        mq_virtual_host=pika_connection.MQ_VIRTUAL_HOST,
        ws_url=f'http://{pika_connection.MQ_HOST}:{MQ_WEBSOCKET_PORT}/stomp',
        subscription_channel=f'/exchange/{pika_connection.MQ_EXCHANGE_NAME}/{ROUTING_KEY}',
    )

def get_datas(pika_connection, api_utils, scrapper_utils):
    overall_worldwide_stats = api_utils.get_worldwide_stats()
    country_data_list = api_utils.get_countries_list_and_codes()
    worldwide_stats = api_utils.get_worldwide_stats()
    worldwide_population_stats = scrapper_utils.get_worldwide_population_data_with_countries()
    country_with_stats = [
        {
            "worldwide_population": scrapper_utils.get_total_worldwide_population(),
            "worldwide_confirmed": overall_worldwide_stats["confirmed_case"],
            "worldwide_recovered": overall_worldwide_stats["recovered_case"],
            "worldwide_deaths": overall_worldwide_stats["deaths_case"]
        }
    ]

    for country_data in country_data_list:
        country_stats = api_utils.get_stats_per_country(country_data["code"])
        country_response = {}
        
        country_response["country_name"] = country_data["name"]
        country_response["population"] = worldwide_population_stats[country_response["country_name"]]["population"] \
            if country_response["country_name"] in list(worldwide_population_stats.keys()) else "N/A"
        country_response["area"] = worldwide_population_stats[country_response["country_name"]]["area"] \
            if country_response["country_name"] in list(worldwide_population_stats.keys()) else "N/A"
        
        country_response.update(country_stats)
        country_response["mortality_rate"] = count_mortality_rate(
            country_stats["deaths_case"], country_stats["confirmed_case"]
        )

        country_with_stats.append(country_response)
        pika_connection.send_message(f'Retrieving Data: {int((len(country_with_stats)/len(country_data_list))*100)}%')
    
    pika_connection.send_message(json.dumps(country_with_stats))
    pika_connection.close_connection()

def retrieve_data_in_background(pika_connection, api_utils, scrapper_utils):
    background_thread = threading.Thread(target=get_datas, args=(pika_connection, api_utils, scrapper_utils))
    background_thread.start()

def count_mortality_rate(deaths_case, confirmed_case):
    return f'{(int(deaths_case)/int(confirmed_case))*100}%' \
        if (confirmed_case != 0 and confirmed_case != 'N/A') \
             and (deaths_case != 0 and deaths_case != 'N/A') else 'N/A'


if __name__ == '__main__':
    app.run(debug=True)