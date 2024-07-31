import argparse
from typing import Optional, List, Tuple
import requests
import os
import sys
import pathlib
import warnings
import multiprocessing

ena_url_download_fastq_file = 'https://www.ebi.ac.uk/ena/browser/api/fasta'
portal_url_to_get_data = 'https://portal.erga-biodiversity.eu/api'


def download_file(url, filename, directory, download_location):
    """Download file using url in the specified location
   :param url:
   :param filename:
   :param directory:
   :param download_location:
   """
    abs_path = create_directory(filename, directory, download_location)
    with requests.get(url, stream=True) as r, open(abs_path, "wb") as f:
        print('Download Started !! ' + url)
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)


def create_directory(filename, directory, parent_dir):
    """Download file using url in the specified location

     Keyword arguments:
     filename -- The name of the File
     directory -- Directory name which you want to create
     parent_dir --  The parent directory where you want to create
    """
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


def downloader(download_list, processes, download_location):
    """Download data using multiprocessing.
     :param download_list:,
     :param processes,
     :param download_location
    """
    cpus = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(cpus if cpus < processes else processes)
    for url, filename, directory, download_location in download_list:
        pool.apply_async(download_file,
                         args=(url, filename, directory, download_location))
    pool.close()
    pool.join()
    print("Download complete")


def convert_project_name(project_name: str) -> str:
    """Convert project name to a standardized format.
     project_name -- Name of the project"""
    return 'dtol' if project_name == 'DToL' else project_name


def download_data(project_name: str, species_list: Optional[str],
                  taxonomy_filter: str, data_status: Optional[str],
                  experiment_type: Optional[str], download_option: str,
                  download_location: str, processes: int) -> None:
    """Fetch data from the portal and initiate downloads."""
    if not download_location or not os.path.exists(download_location):
        print('Using default download location')
        download_location = pathlib.Path(__file__).parent.resolve()

    url = f"{portal_url_to_get_data} " \
          f"/downloader_utility_data_with_species/?" \
          f"species_list={species_list}&project_name={project_name}" \
        if species_list else \
        f"{portal_url_to_get_data}/downloader_utility_data" \
        f"/?taxonomy_filter={taxonomy_filter}" \
        f"&data_status={data_status or ''}&experiment_type=" \
        f"{experiment_type or ''}&project_name={project_name}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data_portal = response.json()
    except requests.RequestException as e:
        print(f'Failed to fetch data: {e}')
        sys.exit(1)

    download_list = generate_download_list(data_portal, download_option,
                                           download_location)
    if download_list:
        print(f"Downloading {len(download_list)} files...\n")
        downloader(download_list, processes, download_location)
        print('All downloads completed.')
    else:
        print('No files to download.')


def generate_download_list(data_portal: List[dict], download_option: str,
                           download_location: str) -> \
        List[Tuple[str, str, str, str]]:
    """Generate a list of files to be downloaded based on the download
    option. """
    download_list = []
    if download_option == 'assemblies':
        for organism in data_portal:
            assemblies = organism.get('_source', {}).get("assemblies", [])
            for assembly in assemblies:
                accession = assembly.get("accession")
                version = assembly.get("version", '')
                filename = f"{accession}.{version}.fasta.gz" if version else \
                    f"{accession}.fasta.gz "
                url = f"{ena_url_download_fastq_file}/{accession}?download" \
                      f"=true&gzip=true "
                download_list.append(
                    (url, filename, 'assemblies', download_location))

    elif download_option == 'annotations':
        for organism in data_portal:
            annotation = organism.get('_source', {}).get("annotation", [])
            for annotation_obj in annotation:
                for key in ['GTF', 'GFF3', 'FASTA']:
                    url = annotation_obj.get('annotation', {}).get(key)
                    if url:
                        sub_dir = f'annotations/{key}'
                        filename = url.split('/')[-1]
                        download_list.append(
                            (url, filename, sub_dir, download_location))
                for key in ['proteins', 'softmasked_genome', 'transcripts']:
                    url = annotation_obj.get(key, {}).get('FASTA')
                    if url:
                        sub_dir = f'annotations/{key}'
                        filename = url.split('/')[-1]
                        download_list.append(
                            (url, filename, sub_dir, download_location))

    elif download_option == 'experiments':
        for organism in data_portal:
            experiments = organism.get('_source', {}).get("experiment", [])
            for experiment in experiments:
                for key in ['sra-ftp', 'submitted_ftp']:
                    url = experiment.get(key)
                    if url:
                        sub_dir = f'experiments/{key}'
                        filename = url.split('/')[-1]
                        download_list.append((f'http://{url}', filename,
                                              sub_dir, download_location))
                fastq_ftp = experiment.get('fastq_ftp', '').split(';')
                for url in fastq_ftp:
                    if url:
                        sub_dir = 'experiments/fastqFtp'
                        filename = url.split('/')[-1]
                        download_list.append((f'http://{url}', filename,
                                              sub_dir, download_location))

    return download_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Welcome to the Downloader Utility !!')
    parser.add_argument("--species_list")
    parser.add_argument("--clade")
    parser.add_argument("--experiment_type")
    parser.add_argument("--data_status")
    parser.add_argument("--download_location")
    parser.add_argument("--download_option")
    parser.add_argument("--project_name")
    parser.add_argument("--processes", default=8)
    args = parser.parse_args()
    config = vars(args)
    warnings.filterwarnings(action='ignore')
    if (config["clade"] is None or config["clade"] == '') and (
            config["species_list"] is None or
            config["species_list"] == ''):
        print('Please provide clade or species_list parameter it is required '
              '!!')
        sys.exit(0)
    elif config["download_option"] is None or config["download_option"] == '':
        print('Please provide download option parameter it is required !!')
        sys.exit(0)
    elif config["project_name"] is None or config["project_name"] == '':
        print('Please provide project name it is required !!')
        sys.exit(0)
    else:
        download_data(config["project_name"], config["species_list"],
                      config["clade"], config["data_status"],
                      config["experiment_type"],
                      config["download_option"],
                      config["download_location"], int(config['processes']))
