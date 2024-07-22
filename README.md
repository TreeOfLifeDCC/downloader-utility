# downloader-utility

Download data using python script.

There are two ways to run the tool :

# 1. Run the python script by providing parameters:
   Requirement:
   
      Python installed:
      Install required libraries using command pip install -r requirements.txt
    
  Run script using command:
    
    python  app/downloader-utility.py --phylogeny "Chordata"   --data_status "Mapped Reads - Done"  --experiment_type "Chromium genome"  --download_location "/Users/raheela/Documents" --download_option "assemblies" --species_list "Apamea sordens,Bufo bufo"


python  app/downloader-utility.py ---phylogeny "Chordata"   --data_status "Mapped Reads - Done"  --experiment_type "Chromium genome"  --download_location "/Users/raheela/Documents" --download_option "assemblies" --species_list "Apamea sordens,Bufo bufo"

* `--clade` (Optional/Required) The name of the Taxnomy for the download (`eg : Dikarya`)
* `--data_status` (Optional) The filter of data status for the download (`eg : Biosamples - Done, Raw Data - Done, Assemblies - Done, Annotation Complete - Done, Genome Notes - Done`)
* `--experiment_type` (Optional) The filter of experiment type (`eg : PacBio - HiFi,Hi-C - Arima v2,Hi-C - Arima v1`)
* `--download_location` (Optional) The location for the download
* `--download_option` (Required) The type of data(`annotations,assemblies,experiments`) that you want to download.
* `--species_list` (Optional/Required) The List of species that you want to download.
* `--project_name` (Required) The name of Project(`DToL,ERGA,25 genomes,CBP`) that you want to download data.
`Note:` clade and species_list both parameters are not optional you need to must provide one of them.

# 2. Build Docker Image: 
 Requirement:
  
    docker is installed and running
  Create docker build using command:
  
    docker build -t downloader-utility:latest .
    
  Run docker image by providing parameters:
  
    docker run --rm -v "$PWD/download_location:/code/app/download_option" downloader-utility:latest  --clade Chordata  --experiment_type "Chromium genome" --download_option annotations --species_list "Apamea sordens,Bufo bufo" --project_name "DToL"
Note: 

Using docker image data is downloaded into download_location e.g /Users/downloads and download_option is (`annotations,assemblies,experiments`).
