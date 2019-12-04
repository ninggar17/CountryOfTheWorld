from django.apps import AppConfig
from rdflib import Graph

# country_graph = Graph()


class CountryDetailConfig(AppConfig):
    name = 'country_detail'

    def ready(self):
        # update my database here
        pass
        # country_graph.parse('C:/Users/Bukalapak/PycharmProjects/CountryOfTheWorld/country_data.ttl', format='turtle')
