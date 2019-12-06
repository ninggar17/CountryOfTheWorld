import json
import re
from json import JSONEncoder

from SPARQLWrapper import SPARQLWrapper, JSON
from executor.query import general_query_dbpedia, general_query_fuseki, get_thumbnails

dbpedia_enpoint = 'http://dbpedia.org/sparql'
fuseki_endpoint = 'http://localhost:3030/Data/query'


class CountryInfo(object):
    json_number = None

    def __init__(self, **kwargs):
        input = self.search(kwargs['query'])
        for field in ('query', 'res'):
            setattr(self, field, input[field])

    def search(self, query):
        try:
            res = {'query': query, 'res': self.query(query)}
        except Exception:
            res = {'query': query, 'res': []}
        return res

    @staticmethod
    def remote(endpoint, query, keyword):
        sparql = SPARQLWrapper(endpoint)
        sparql_query = query(keyword)
        sparql.setQuery(sparql_query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        res = []
        xsd = 'http://www.w3.org/2001/XMLSchema#'
        for result in results['results']['bindings']:
            res_i = {}
            for key in result.keys():
                if not result[key]['value'] == '':
                    try:
                        if result[key]['datatype'] == xsd + 'float':
                            res_i[key] = float(result[key]['value'])
                        elif result[key]['datatype'] == xsd + 'integer':
                            res_i[key] = int(result[key]['value'])
                    except Exception:
                        if re.search(r'\|', result[key]['value']):
                            res_i[key] = re.split(r'\|', result[key]['value'])
                        elif key == 'type':
                            res_i[key] = re.search(r'/([^/]+)$', result[key]['value']).group(1)
                        else:
                            res_i[key] = result[key]['value']
            res.append(res_i)
        return res
        pass

    def query(self, query):
        # print(general_query_dbpedia(query.lower()))
        res_dbpedia = self.remote(dbpedia_enpoint, general_query_dbpedia, query.lower())
        uris = '((' + query.lower() + ')'
        try:
            for object in res_dbpedia:
                uris = uris + '|(' +re.sub('\'', '\\\\\'',(re.sub('\\)', '\\\\\\\\)', re.sub('\\(', '\\\\\\\\(', object['object'])) + ')'))
        except Exception:
            uris = uris + '|' + str(res_dbpedia['object'])
        uris = uris + ')'
        try:
            res_fuseki = self.remote(fuseki_endpoint, general_query_fuseki, uris)
            res = self.join_result(res_dbpedia, res_fuseki)
        except Exception:
            res = res_dbpedia
        return res

    def join_result(self, dict1, dict2):
        res = []
        res_len = 0
        # print(json.dumps(dict1, indent=4))
        # print(json.dumps(dict2, indent=4))
        try:
            if dict1 and dict2:
                for object1 in dict1:
                    for object2 in dict2:
                        if object1['object'] == object2['sameAs']:
                            dict_merge = lambda a, b: a.update(b) or a
                            new_object = dict_merge(object1, object2)
                            res.append(new_object)
            elif dict2:
                res = dict2
        except Exception:
            if dict1['object'] == dict2['sameAs']:
                dict_merge = lambda a, b: a.update(b) or a
                # res = dict_merge(dict1, dict2)
                res.append(dict_merge(dict1, dict2))
        if not res:
            res = dict2
        try:
            for obj in res:
                if obj['type'] == 'Country':
                    obj['relatedCountry'] = self.get_thumbnail_dbpedia(obj['relatedCountry'], obj['relatedCountryName'])
                    del obj['relatedCountryName']
                else:
                    obj['member'] = self.get_thumbnail_dbpedia(obj['member'], obj['memberName'])
                    del obj['memberName']
        except Exception:
            pass
        return res

    def get_thumbnail_dbpedia(self, uris, name):
        pattern = ''
        for uri in uris:
            pattern = pattern + '|' + re.search(r'/([^/]+$)', uri).group(1)
        data = self.remote(dbpedia_enpoint, get_thumbnails, pattern[1:])
        res = {}
        for obj in data:
            res[name[uris.index(obj['object'])]] = obj['thumbnail']
        return res


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
