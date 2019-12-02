import json
import re
from json import JSONEncoder

from SPARQLWrapper import SPARQLWrapper, JSON

from country_detail.apps import country_graph


class CountryInfo(object):
    json_number = None
    def __init__(self, **kwargs):
        format_id_dict = self.reformat(kwargs['query'])
        for field in ('query', 'res'):
            setattr(self, field, format_id_dict[field])

    def reformat(self,query):
        res = {'query': query, 'res': self.remote_dbpedia(query)}
        return res

    @staticmethod
    def remote_dbpedia(query):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("""
        PREFIX ex:<http://www.example.org/> 
        PREFIX foaf:<http://xmlns.com/foaf/0.1/> 
        PREFIX dbo:<http://dbpedia.org/ontology/> 
        PREFIX dbp:<http://dbpedia.org/property/>
        PREFIX dct:<http://purl.org/dc/terms/> 
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbr:<http://dbpedia.org/resource/> 
        PREFIX owl:<http://www.w3.org/2002/07/owl#> 
        SELECT
            ?country
            (group_concat(distinct ?abstract,'|') as ?abstract)
            (group_concat(distinct ?country_name,'|') as ?country_name)
            (group_concat(distinct ?capital,'|') as ?capital) ?currency
            (group_concat(distinct ?language,'|') as ?language)
            (max(?foundingDate) as ?foundingDate) (group_concat(distinct ?leader,'|') as ?leader)
            (group_concat(distinct ?governmentType,'|') as ?governmentType)
            (group_concat(distinct ?anthem,'|') as ?anthem)
            (group_concat(distinct ?callingCode,'|') as ?callingCode)
            (group_concat(distinct ?thumbnail,'|') as ?thumbnail)
        WHERE
            {?country a dbo:Country.
                {?country foaf:name ?name, ?country_name.
                optional{
                   ?country dbo:capital ?capitalCity.
                   {?capitalCity foaf:name ?capital.
                    filter(lang(?capital)='en')}
                union
                   {?capitalCity dbp:enName ?capital.}}
            UNION
                {?country foaf:name ?country_name; dbo:capital ?capitalCity.
                {{
                    ?capitalCity foaf:name ?capital, ?name.
                    filter(?capital=?name and lang(?capital)='en')
                }
                union
                {
                    ?capitalCity dbp:enName ?capital, ?name.
                    FILTER(xsd:string(?capital)=xsd:string(?name))
                }}
                FILTER(?capital=?name)}
            OPTIONAL
                {
                    ?country dbo:abstract ?abstract.
                    FILTER(lang(?abstract)='en')
                }
            OPTIONAL
                {?country dbp:currencyCode ?currency.}
            OPTIONAL
                {?country dbo:language ?lang. ?lang rdfs:label ?language.
                FILTER(lang(?language)='en')}
            OPTIONAL
                {?country dbo:foundingDate ?foundingDate.}
            OPTIONAL
                {?country dbo:governmentType ?government. ?government rdfs:label ?governmentType.
                FILTER(lang(?governmentType)='en')}
            OPTIONAL
                {?country dbo:anthem ?song. ?song rdfs:label ?anthem.
                FILTER(lang(?anthem)='en')}
            OPTIONAL
                {?country dbo:leader ?lead. ?lead foaf:name ?leader; dct:description ?lead_desc.
                FILTER(regex(lcase(?lead_desc),'^(president|king|prime minister) of'))
                FILTER(lang(?leader)='en')}
            OPTIONAL
                {?country dbp:callingCode ?code.
                    {?code rdfs:label ?callingCode.}
                UNION
                    {?code dbp:countryCallingCode ?callingCode.}
                FILTER(regex(?callingCode,'^\\\\+\\\\d+$'))}
            OPTIONAL
                {?country dbo:thumbnail ?thumbnail.}
            FILTER(regex(lcase(xsd:string(?name)), '"""+query.lower()+"""'))}
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        res = []
        for result in results['results']['bindings']:
            res_i = {}
            for key in result.keys():
                if not result[key]['value'] == '':
                    res_i[key] = result[key]['value']
            res.append(res_i)

        max_res = 0
        res_return = {}
        for index_res in range(len(res)):
            if max_res < len(res[index_res]):
                res_return = res[index_res]
                max_res = len(res[index_res])
        return res_return

    def remote_local(query):
        pass


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
