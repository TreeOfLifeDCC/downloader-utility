import argparse
import requests
import os
import sys
import pathlib
import warnings
import multiprocessing


def download_filea(url, filename, directory, download_location):
    abs_path = create_directory(url, filename, directory, download_location)
    with requests.get(url, stream=True) as r, open(abs_path, "wb") as f:
        print('Download Started !! ' + url)
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)


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


def downloader(download_list, processes):
    # download data with multiprocessing
    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(cpus if cpus < processes else processes)
    for url, filename, directory, download_location in download_list:
        pool.apply_async(download_filea, args=(url, filename, directory, download_location))
    pool.close()
    pool.join()
    print("Download complete")


def main(species_list, taxonomy_filter, data_status, experiment_type, download_option, download_location, processes):
    if (download_location == '' or download_location is None) or os.path.exists(download_location) == False:
        print('using default download location')
        download_location = pathlib.Path(__file__).parent.resolve()
    if species_list is not None and species_list != '':

        data_portal = requests.get(
            "https://portal.darwintreeoflife.org/statuses_update/downloader_utility_data_with_species"
            "/?species_list=" + species_list).json()
    else:
        if data_status and not experiment_type:
            data_portal = requests.get(
                "https://portal.darwintreeoflife.org/statuses_update/downloader_utility_data/?taxonomy_filter="
                + taxonomy_filter + "&data_status=" + data_status + "&experiment_type=").json()
        elif not data_status and experiment_type:
            data_portal = requests.get(
                "https://portal.darwintreeoflife.org/statuses_update/downloader_utility_data/?taxonomy_filter="
                + taxonomy_filter + "&experiment_type=" + experiment_type + "&data_status=").json()
        elif not data_status and not experiment_type:
            data_portal = requests.get(
                "https://portal.darwintreeoflife.org/statuses_update/downloader_utility_data/?taxonomy_filter="
                + taxonomy_filter+ "&experiment_type=" + "&data_status=").json()
        else:
            data_portal = requests.get(
                "https://portal.darwintreeoflife.org/statuses_update/downloader_utility_data/?taxonomy_filter="
                + taxonomy_filter + "&data_status=" + data_status + "&experiment_type=" + experiment_type).json()

    if len(data_portal) > 0:
        download_list = []
        if download_option == 'assemblies':
            for organism in data_portal:
                if organism.get('_source').get("assemblies"):
                    for assemblies in organism.get('_source').get("assemblies"):
                        url = "https://www.ebi.ac.uk/ena/browser/api/fasta/" + assemblies.get("accession") + "?download" \
                                                                                                             "=true" \
                                                                                                             "&gzip" \
                                                                                                             "=true "
                        if assemblies.get("version"):
                            download_list.append(
                                [url, assemblies.get("accession") + '.' + assemblies.get("version") + '.fasta.gz',
                                 'assemblies', download_location])
                        else:
                            download_list.append(
                                [url, assemblies.get("accession") + '.fasta.gz', 'assemblies', download_location])
        elif download_option == 'annotations':
            for organism in data_portal:
                if organism.get('_source').get("annotation"):
                    for annotationObj in organism.get('_source').get("annotation"):
                        if annotationObj.get('annotation'):
                            urlGFT = annotationObj.get('annotation').get('GTF')
                            urlGFF3 = annotationObj.get('annotation').get('GFF3')
                            download_list.append([urlGFT, urlGFT.split('/')[-1], 'annotations/GFT', download_location])
                            download_list.append(
                                [urlGFF3, urlGFF3.split('/')[-1], 'annotations/GFF3', download_location])
                        if annotationObj.get('proteins'):
                            url_proteins = annotationObj.get('proteins').get('FASTA')
                            download_list.append(
                                [url_proteins, url_proteins.split('/')[-1], 'annotations/proteins', download_location])
                        if annotationObj.get('softmasked_genome'):
                            url_softmasked_genome = annotationObj.get('softmasked_genome').get('FASTA')
                            download_list.append(
                                [url_softmasked_genome, url_softmasked_genome.split('/')[-1], 'annotations'
                                                                                              '/softmaskedGenome',
                                 download_location])
                        if annotationObj.get('transcripts'):
                            url_transcripts = annotationObj.get('transcripts').get('FASTA')
                            download_list.append(
                                [url_transcripts, url_transcripts.split('/')[-1],
                                 'annotations/transcripts', download_location])
        elif download_option == 'experiments':
            for organism in data_portal:
                if organism.get('_source').get("experiment"):
                    for experiment in organism.get('_source').get("experiment"):
                        if experiment.get('sra-ftp'):
                            url_sra_ftp = experiment.get('sra-ftp')
                            download_list.append(
                                ['http://' + url_sra_ftp, url_sra_ftp.split('/')[-1],
                                 'experiments/sraFtp', download_location])
                        if experiment.get('submitted_ftp'):
                            url_submitted_ftp = experiment.get('submitted_ftp')
                            download_list.append(
                                ['http://' + url_submitted_ftp, url_submitted_ftp.split('/')[-1],
                                 'experiments/submittedFtp', download_location])
                        if experiment.get('fastq_ftp'):
                            fastq_ftplist = experiment.get('fastq_ftp').split(';')
                            if fastq_ftplist:
                                for fastq in fastq_ftplist:
                                    url_fastq_ftp = fastq
                                    download_list.append(
                                        ['http://' + url_fastq_ftp, url_fastq_ftp.split('/')[-1],
                                         'experiments/fastqFtp', download_location])
        if len(download_list):
            print(f"Downloading {len(download_list)}  files...\n")
            downloader(download_list, processes)
        print('Downloading Completed ...!!!')

    else:
        print('No Data found with provided parameters !!')
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Welcome to the Downloader Utility !!')
    parser.add_argument("--species_list")
    parser.add_argument("--phylogeny")
    parser.add_argument("--experiment_type")
    parser.add_argument("--data_status")
    parser.add_argument("--download_location")
    parser.add_argument("--download_option")
    parser.add_argument("--processes", default=8)
    args = parser.parse_args()
    config = vars(args)
    warnings.filterwarnings(action='ignore')
    if (config["phylogeny"] is None or config["phylogeny"] == '') and (config["species_list"] is None or config[
        "species_list"] == ''):
        print('Please provide phylogeny or species_list parameter it is required !!')
        sys.exit(0)
    elif config["download_option"] is None or config["download_option"] == '':
        print('Please provide download option parameter it is required !!')
        sys.exit(0)
    else:
        main(config["species_list"], config["phylogeny"], config["data_status"], config["experiment_type"],
             config["download_option"],
             config["download_location"], int(config['processes']))
