def general_query_fuseki(query=None):
    return """PREFIX ex:<http://www.example.org/>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>
PREFIX dbo:<http://dbpedia.org/ontology/>
PREFIX dbp:<http://dbpedia.org/property/>
PREFIX dct:<http://purl.org/dc/terms/>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbr:<http://dbpedia.org/resource/>
PREFIX owl:<http://www.w3.org/2002/07/owl#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
select
     ?sameAs ?type ?name ?phoneSubs ?gdp ?literacy ?corpsValue ?area ?coastline ?migration ?density ?population
     ?serviceRate ?birthRate ?infantMortality ?arable ?climateType ?sameAs ?anthem ?subArea
	 (group_concat(distinct(?relatedAlias); separator = "|") as ?relatedCountry)
	 (group_concat(distinct(?relatedName); separator = "|") as ?relatedCountryName)
	 (group_concat(distinct(?countryMemberAlias); separator = "|") as ?member)
	 (group_concat(distinct(?countryMemberName); separator = "|") as ?memberName)
where
{
    {?object a ?type, dbo:Country .
    ?object foaf:name ?name .
    ?object owl:sameAs ?sameAs.
    optional
        {?object ex:phoneSubs ?phoneSubs.}
    optional
        {?object ex:gdpValue ?gdp.}
    optional
        {?object ex:literacyRate ?literacy.}
    optional
        {?object ex:corpsValue ?corpsValue.}
    optional
        {?object ex:area ?area.}
    optional
        {?object ex:coastline ?coastline.}
    optional
        {?object ex:netMigration ?migration.}
    optional
        {?object ex:populationDensity ?density.}
    optional
        {?object ex:population ?population.}
    optional
        {?object ex:serviceRate ?serviceRate.}
    optional
        {?object ex:deathRate ?dateRate.}
    optional
        {?object ex:agricultureRate ?agriculture.}
    optional
        {?object ex:industryRate ?industryRate.}
    optional
        {?object ex:birthRate ?birthRate.}
    optional
        {?object ex:infantMortalityRate ?infantMortality.}
    optional
        {?object ex:arableRate ?arable.}
    optional
        {?object owl:sameAs ?sameAs.}
    optional
        {?object ex:climateType ?climateType .}
    optional
    {
        ?object ex:subAreaOf ?sub.
        ?related ex:subAreaOf ?sub;
                 owl:sameAs ?relatedAlias;
                 foaf:name ?relatedName.
        ?sub foaf:name ?subArea.
        filter(?object != ?related)
        filter(?type=dbo:Country)
    }}
union
    {
        ?object a ?type.
        ?object a dbo:Place.
        ?object foaf:name ?name.
        ?object owl:sameAs ?sameAs.
        ?countryMember ex:subAreaOf ?object;
                owl:sameAs ?countryMemberAlias;
                foaf:name ?countryMemberName.
        filter(?type=dbo:Place)
    }
filter(regex(lcase(xsd:string(?name)), '(^|[\\\\s\\\\.,-_])"""+query+"""([\\\\s\\\\.,-_]|$)') || regex(str(?sameAs), '^"""+query+"""$'))
}
group by ?sameAs ?type ?name ?phoneSubs ?gdp ?literacy ?corpsValue ?area ?coastline ?migration ?density ?population
         ?serviceRate ?birthRate ?infantMortality ?arable ?climateType ?sameAs ?anthem ?subArea
"""

def general_query_dbpedia(query=None):
    return """
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
    ?object
    (group_concat(distinct ?abstract,'|') as ?abstract)
    (group_concat(distinct ?object_name,'|') as ?object_name)
    (group_concat(distinct ?capital,'|') as ?capital)
    ?currency
    (group_concat(distinct ?language,'|') as ?language)
    (max(?foundingDate) as ?foundingDate) (group_concat(distinct ?leader,'|') as ?leader)
    (group_concat(distinct ?governmentType,'|') as ?governmentType)
    (group_concat(distinct ?anthem,'|') as ?anthem)
    (group_concat(distinct ?callingCode,'|') as ?callingCode)
    (group_concat(distinct ?thumbnail,'|') as ?thumbnail)
WHERE
    {?object a dbo:Country.
        {?object foaf:name ?name, ?object_name.
        optional{
           ?object dbo:capital ?capitalCity.
           {?capitalCity foaf:name ?capital.
            filter(lang(?capital)='en')}
        union
           {?capitalCity dbp:enName ?capital.}}
        filter(lang(?name)='en' and ?name=?object_name)}
    UNION
        {?object foaf:name ?object_name; a dbo:Country; dbo:capital ?capitalCity.
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
            ?object dbo:abstract ?abstract.
            FILTER(lang(?abstract)='en')
        }
    OPTIONAL
        {?object dbp:currencyCode ?currency.}
    OPTIONAL
        {?object dbo:language ?lang. ?lang rdfs:label ?language.
        FILTER(lang(?language)='en')}
    OPTIONAL
        {?object dbo:foundingDate ?foundingDate.}
    OPTIONAL
        {?object dbo:governmentType ?government. ?government rdfs:label ?governmentType.
        FILTER(lang(?governmentType)='en')}
    OPTIONAL
        {?object dbo:anthem ?song. ?song rdfs:label ?anthem.
        FILTER(lang(?anthem)='en')}
    OPTIONAL
        {?object dbo:leader ?lead. ?lead foaf:name ?leader; dct:description ?lead_desc.
        FILTER(regex(lcase(?lead_desc),'^(president|king|prime minister) of'))
        FILTER(lang(?leader)='en')}
    OPTIONAL
        {?object dbp:callingCode ?code.
            {?code rdfs:label ?callingCode.}
        UNION
            {?code dbp:countryCallingCode ?callingCode.}
        FILTER(regex(?callingCode,'^\\\\+\\\\d+$'))}
    OPTIONAL
        {?object dbo:thumbnail ?thumbnail.}
    FILTER(regex(lcase(xsd:string(?name)), '(^|[\\\\s\\\\.,-_])"""+query+"""([\\\\s\\\\.,-_]|$)'))}
"""


def get_thumbnails(query=None):
    return """
select
   ?object
   ?thumbnail
where
{
   ?object dbo:thumbnail ?thumbnail.
   ?object a dbo:Country.
   filter(regex(?object, '[/]("""+query+""")$'))
}
"""
