# downloader-utility

Download data using python script.

There are two ways to run the tool :

# 1. Run the python script by providing parameters:
   Requirment:
   
      Python installed:
      Run requirnment.txt using command pip install -r requirnment.txt
    
  Run script using command:
    
    python  app/downloader-utility.py --phylogeny "Dikarya"   --data_status “Mapped reads - Done”  --experiment_type “Chromium genome”  --download_location "/Users/raheela/Documents" --download_option "assemblies"


python  app/downloader-utility.py ---phylogeny "Dikarya"   --data_status “Mapped reads - Done”  --experiment_type “Chromium genome”  --download_location "/Users/raheela/Documents" --download_option "assemblies"

* `--phylogeny` (Required) The name of the Taxnomy for the download (`eg : Dikarya`)
* `--data_status` (Optional) The filter of data status for the download (`eg : Biosamples - Submitted,Mapped Reads - Submitted,Assemblies - Submitted,Raw Data - Submitted,Annotation Complete - Done,Genome Notes - Submitted`)
* `--experiment_type` (Optional) The filter of experiment type (`eg : PacBio - HiFi,Hi-C - Arima v2,Hi-C - Arima v1`)
* `--download_location` (Optional) The location for the download
* `--download_option` (Required) The type of data(`annotations,assemblies`) that you want to download.


# 2. Build Docker Image: 
 Requirment:
  
    docker is installed and running
  Create docker buid using command:
  
    docker build -t downloader-utility:latest .
    
  Run docker image by providing parameters:
  
    docker run downloader-utility:latest  --phylogeny Amphipyrinae  --experiment_type "Hi-C - Arima v1" --download_option annotations
Note: 

Using docker image data is downloaded into the container and you need to copy data from outside the container.
