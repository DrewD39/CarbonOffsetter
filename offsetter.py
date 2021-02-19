import datetime
import json
import requests
import urllib.parse

BASE_URL = 'https://www.wren.co/api/offset-orders'

PORTFOLIO_ENDPOINT = urllib.parse.urljoin(BASE_URL, 'portfolios')
OFFSET_ENDPOINT = urllib.parse.urljoin(BASE_URL, 'offset-orders')

USER_TOKEN = 'XXXXXXXXXXXXXXXXXXXXXX'
AUTH_HEADER = {'Authorization': 'Bearer ' + USER_TOKEN}

LINE_DIVIDE = '-' * 80

class RequestException(Exception):
    """API request failed."""

class Portfolio():

    def __init__(self, portfolio_dict):
        self.cost_per_ton = portfolio_dict['cost_per_ton']
        self.description = portfolio_dict['description']
        self.id = portfolio_dict['id']
        self.name = portfolio_dict['name']
        self.project_percentages = {}
        for project in portfolio_dict['projects']:
            self.project_percentages[project['name']] = project['percentage']

    def __str__(self):
        project_strs = [f'\t{percent * 100}% {name}\n' for name, percent in self.project_percentages.items()]
        return f'{self.name}\n{self.description}\nCost per Ton: {self.cost_per_ton}\n' \
               f'Supported projects:\n{"".join(project_strs)}'

def get_portfolios(show=False):
    response = requests.get(PORTFOLIO_ENDPOINT)
    if response.status_code != 200:
        raise RequestException(f'API request failed with response code {response.status_code}.\n{response.text}')
    portfolios = []
    for portfolio_json in response.json()['portfolios']:
        portfolio = Portfolio(portfolio_json)
        portfolios.append(portfolio)
        if show:
            print(LINE_DIVIDE)
            print(portfolio)
    return portfolios

class OffsetOrder():
    def __init__(self, offset_order_dict):
        self.amount_paid_by_customer = offset_order_dict['amount_paid_by_customer']
        self.id = offset_order_dict['id']
        self.note = offset_order_dict['note']
        self.portfolio_id = offset_order_dict['portfolio_id']
        self.project_id = offset_order_dict['project_id']
        self.source = offset_order_dict['source']
        self.tons = offset_order_dict['tons']

    def __str__(self):
        return f'{self.tons} tons were offset through portfolio {self.portfolio_id} at a cost of ${self.amount_paid_by_customer / 100}'

def get_offset_orders(show=False):
    response = requests.get(OFFSET_ENDPOINT, headers=AUTH_HEADER)
    if response.status_code != 200:
        raise RequestException(f'API request failed with response code {response.status_code}.\n{response.text}')
    if show:
        print('Offset order history:')
    offset_orders = []
    for order_json in response.json():
        offset_order = OffsetOrder(order_json)
        if show:
            print(offset_order)
        offset_orders.append(offset_order)
    return response.json()


def offset_carbon(portfolio_id, tons=1.0, note='', show=False):
    data = {
        "portfolioId": portfolio_id,
        "tons": tons,
        "note": f'{datetime.date.today()} : {note}',
        "dryRun": False
    }
    response = requests.post(OFFSET_ENDPOINT, data=data, headers=AUTH_HEADER)
    if response.status_code != 200:
        raise RequestException(f'API request failed with response code {response.status_code}.\n{response.text}')
    response_json = response.json()
    if show:
        print(f'\nSuccessfully offest {response_json["tons"]} tons of carbon at a price of ${response_json["amountCharged"] / 100}!!!\n')
    return response_json


if __name__ == '__main__':

    get_portfolios(show=True)
    offset_carbon(portfolio_id=1, tons=0.1, show=True)
    get_offset_orders(show=True)
