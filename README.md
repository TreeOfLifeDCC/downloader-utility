# downloader-utility

Download data using python script.

There are two ways to run the tool :

# 1. Run the python script by providing parameters:
   Requirement:
   
      Python installed:
      Install required libraries using command pip install -r requirement.txt
    
  Run script using command:
    
    python  app/downloader-utility.py --phylogeny "Chordata" --project_name "DToL"  --data_status "Mapped Reads - Done"  
    --experiment_type "Chromium genome"  --download_location "/Users/raheela/Documents" --download_option "assemblies" 
    --species_list "Apamea sordens,Bufo bufo"


python  app/downloader-utility.py --project_name "DToL" ---phylogeny 
"Chordata"   --data_status "Mapped Reads - Done"  --experiment_type "Chromium genome"  --download_location 
"/Users/raheela/Documents" --download_option "assemblies" --species_list "Apamea sordens,Bufo bufo"

* `--project_name` (Required): The name of the project (e.g., DToL, ERGA, 25 
   genomes, Canadian BioGenome Project (CBP)).
* `--phylogeny` (Optional/Required): The name of the taxonomy for the download 
  (e.g., Chordata). Either --phylogeny or --species_list must be provided.
* `--data_status` (Optional): The filter for data status (e.g., Biosamples - 
  Done, Raw Data - Done, Assemblies - Done, Annotation Complete - Done, Genome Notes - Done).
* `--experiment_type` (Optional): The filter for experiment type (e.g., 
  PacBio HiFi, Hi-C - Arima v2, Hi-C - Arima v1).
* `--download_location` (Optional): The location to save the downloaded files.
* `--download_option` (Required): The type of data to download (annotations, 
  assemblies, experiments).
* `--species_list` (Optional/Required): The list of species to download. 
  Either --phylogeny or --species_list must be provided.

Note: The `--phylogeny` and `--species_list` parameters are conditional; you need to provide one of them.

# 2. Build Docker Image: 
 Requirement:
  
    docker is installed and running
  Create docker build using command:
  
    docker build -t downloader-utility:latest .
    
  Run docker image by providing parameters:
  
    docker run --rm -v "$PWD/download_location:/code/app/download_option" downloader-utility:latest  --clade Chordata  
    --experiment_type "Chromium genome" --download_option annotations --species_list "Apamea sordens,Bufo bufo" 
    --project_name "DToL"

Note: When using the Docker image, data is downloaded into the specified 
`download_location (e.g., /Users/downloads)` and the `download_option` should 
be one of `(annotations, assemblies, experiments)`.
