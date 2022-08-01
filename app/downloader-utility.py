from elasticsearch import Elasticsearch
from elasticsearch import RequestsHttpConnection
import argparse
import requests
import os
import sys
from neo4j import GraphDatabase
import pathlib
import warnings


class NeoFourJ:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_rank(self, param):
        with self.driver.session() as session:
            rank = session.write_transaction(self._get_rank, param)
            return rank

    @staticmethod
    def _get_rank(tx, param):
        result = tx.run(
            'MATCH (parent:Taxonomies)-[:CHILD]->(child:Taxonomies) where parent.name=~' '"' '.*' + param + '.*' '"'
                                                                                                            'RETURN parent')
        return result.single()[0]


def download_filea(url, filename, directory, download_location):
    abs_path = create_directory(url, filename, directory, download_location)

    with requests.get(url, stream=True) as r, open(abs_path, "wb") as f:
        print('Download Started !! ' + url)
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
    # print('Download Started !!'+ url)
    # with open(abs_path, 'wb') as f:
    #     response = requests.get(url, stream=True)
    #     total = response.headers.get('content-length')
    # 
    #     if total is None:
    #         f.write(response.content)
    #     else:
    #         downloaded = 0
    #         total = int(total)
    #         for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
    #             downloaded += len(data)
    #             f.write(data)
    #             done = int(50 * downloaded / total)
    #             sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50 - done)))
    #             sys.stdout.flush()
    # sys.stdout.write('\n')


def create_directory(url, filename, directory, parent_dir):
    path = os.path.join(parent_dir, directory)

    try:
        os.makedirs(path, exist_ok=True)

    except OSError as error:
        print("Directory '%s' can not be created" % directory)

    if filename:
        local_filename = os.path.join(path, filename)
    else:
        local_filename = os.path.join(path, filename)

    return local_filename


def main(taxonomyFilter, data_status, experiment_type, download_option, download_location):
    if (download_location == '' or download_location is None) or os.path.exists(download_location) == False:
        print('location is not valid using default location')
        download_location = pathlib.Path(__file__).parent.resolve()

    es = Elasticsearch('http://45.88.81.118:80/elasticsearch', connection_class=RequestsHttpConnection,
                       use_ssl=False, verify_certs=False, timeout=10000)

    query_param = ' { "'"from"'" : 0, "'"size"'" : 5000, "'"query"'" : { "'"bool"'" : { "'"must"'" : [ '
    if taxonomyFilter != '':
        result = neofourJ.get_rank(taxonomyFilter)
        query_param = query_param + '{ "nested" : { "path" : "taxonomies", "query" : { "nested" : { ' \
                                    '"path" : ' \
                                    '"taxonomies.' + result._properties.get(
            'rank') + '"' ', "query" : { "bool" : { ' \
                      '"must" : [{ ' \
                      '"term" : { ' \
                      '"taxonomies.' + result._properties.get(
            'rank') + '.scientificName" :''"' + result._properties.get('name') + '"' '}}]}}}}}} '
    if data_status != None and data_status != '':
        split_array = data_status.split("-")
        if split_array and split_array[0].strip() == 'Biosamples':
            query_param = query_param + ',{ "terms" : { "biosamples" : [''"' + split_array[1].strip() + '"'']}}'
        elif split_array and split_array[0].strip() == 'Raw data':
            query_param = query_param + ',{ "terms" : { "raw_data" : [''"' + split_array[1].strip() + '"'']}}'
        elif split_array and split_array[0].strip() == 'Mapped reads':
            query_param = query_param + ',{ "terms" : { "mapped_reads" : [''"' + split_array[
                1].strip() + '"'']}}'
        elif split_array and split_array[0].strip() == 'Assemblies':
            query_param = query_param + ',{ "terms" : { "assemblies_status" : [''"' + split_array[
                1].strip() + '"'']}}'
        elif split_array and split_array[0].strip() == 'Annotation complete':
            query_param = query_param + ',{ "terms" : { "annotation_complete" : [''"' + split_array[
                1].strip() + '"'']}}'
        elif split_array and split_array[0].strip() == 'Annotation':
            query_param = query_param + ',{ "terms" : { "annotation_status" : [''"' + split_array[
                1].strip() + '"'']}}'
        elif split_array and split_array[0].strip() == 'Genome Notes':
            query_param = query_param + ',{ "nested": {"path": "genome_notes","query": {"bool": {"must": [{"exists": ' \
                                        '{"field": "genome_notes.url"}}]}}}} '
    if experiment_type != '':
        query_param = query_param + ',{ "nested" : { "path": "experiment", "query" : { "bool" : { "must" : [' \
                                    '{ "term" : { "experiment.library_construction_protocol.keyword" : ' + \
                      '"' + experiment_type + '"' '}}]}}}}'

    query_param = query_param + '] }}}'
    print(query_param)
    data_portal = es.search(index="data_portal", size=10000, body=query_param)
    print(len(data_portal['hits']['hits']))
    print(len(data_portal['hits']['hits']) > 0)
    if len(data_portal['hits']['hits']) > 0:
        if download_option == 'assemblies':
            for organism in data_portal['hits']['hits']:
                if organism.get('_source').get("assemblies"):
                    for assemblies in organism.get('_source').get("assemblies"):
                        url = "https://www.ebi.ac.uk/ena/browser/api/fasta/" + assemblies.get("accession") + "?download" \
                                                                                                             "=true&gzip" \
                                                                                                             "=true "

                        download_filea(url, assemblies.get("accession") + '.' + assemblies.get("version") + '.fasta.gz',
                                       'assemblies', download_location)
            print('Downloading Completed ...!!!')
        elif download_option == 'annotations':
            for organism in data_portal['hits']['hits']:
                if organism.get('_source').get("annotation"):
                    for annotationObj in organism.get('_source').get("annotation"):
                        if annotationObj.get('annotation'):
                            urlGFT = annotationObj.get('annotation').get('GTF')
                            download_filea(urlGFT, urlGFT.split('/')[-1],
                                           'annotations/GFT', download_location)
                            urlGFF3 = annotationObj.get('annotation').get('GFF3')
                            download_filea(urlGFF3, urlGFF3.split('/')[-1],
                                           'annotations/GFF3', download_location)
                        if annotationObj.get('proteins'):
                            url_proteins = annotationObj.get('proteins').get('FASTA')
                            download_filea(url_proteins, url_proteins.split('/')[-1],
                                           'annotations/proteins', download_location)
                        if annotationObj.get('softmasked_genome'):
                            url_softmasked_genome = annotationObj.get('softmasked_genome').get('FASTA')
                            download_filea(url_softmasked_genome, url_softmasked_genome.split('/')[-1],
                                           'annotations/softmaskedGenome', download_location)
                        if annotationObj.get('transcripts'):
                            url_transcripts = annotationObj.get('transcripts').get('FASTA')
                            download_filea(url_transcripts, url_transcripts.split('/')[-1],
                                           'annotations/transcripts', download_location)

            print('Downloading Completed ...!!!')

    else:
        print('No Data found with provided parameters !!')
        sys.exit(0)


if __name__ == "__main__":
    neofourJ = NeoFourJ("bolt://45.88.80.141:30087", "neo4j", "DtolNeo4jAdminUser@123")
    parser = argparse.ArgumentParser(description='Welcome to the Downloader Utility !!')
    parser.add_argument("--phylogeny")
    parser.add_argument("--experiment_type")
    parser.add_argument("--data_status")
    parser.add_argument("--download_location")
    parser.add_argument("--download_option")
    args = parser.parse_args()
    config = vars(args)
    print(config["download_option"])
    warnings.filterwarnings(action='ignore')
    if config["phylogeny"] is None or config["phylogeny"] == '':
        print('Please provide phylogeny parameter it is required !!')
        sys.exit(0)
    elif config["download_option"] is None or config["download_option"] == '':
        print('Please provide download option parameter it is required !!')
        sys.exit(0)
    else:
        main(config["phylogeny"], config["data_status"], config["experiment_type"], config["download_option"],
             config["download_location"])
    # main('Dikarya', 'Mapped reads - Done', 'Chromium genome','assemblies' ,None)
    # main('Amphipyrinae',None, 'Hi-C - Arima v1', 'annotations', '/Users/raheela/Documents')
    neofourJ.close()



