#Simple Webcrawler Container

The files in this repo implement a simple webcrawler and its associated test files.

The directory structure is shown below:

.                    
├── src/                     # Main Source file. (crawler.py)
├── test/                    # Automated tests (test_crawler.py)
├── utils/                   # Tools and utilities  (dummy.html, dummy.xml, requirements.txt) used by the test suite and Dockerfile
├
├── Dockerfile				 # File used to build and run src code
└── README.txt				 # Project overview inc installation and running instructions

This script is recommended to be run on Linux or Mac OS however the instructions for all 3 major operation systems are included in this README.


The usage is shown below:

usage: crawler.py [-h] [-u A_BASEURL]
                  [-ul A_UNWANTEDLINKS [A_UNWANTEDLINKS ...]]
                  [-ue A_UNWANTEDEXTENSIONS [A_UNWANTEDEXTENSIONS ...]]

Gather Options

optional arguments:
  -h, --help            show this help message and exit
  -u A_BASEURL, --url A_BASEURL
                        Base url of the site to be crawled
  -ul A_UNWANTEDLINKS [A_UNWANTEDLINKS ...], --unwanted_links A_UNWANTEDLINKS [A_UNWANTEDLINKS ...]
                        space separated list of which link 'rel' attributes to
                        ignore
  -ue A_UNWANTEDEXTENSIONS [A_UNWANTEDEXTENSIONS ...], --unwanted_extensions A_UNWANTEDEXTENSIONS [A_UNWANTEDEXTENSIONS ...]
                        space separated list of which extensions to ignore


Because the affectiveness of webcrawling is dependent on site recon/ trial and error, there are user configurable options to specify which extensions should be ignored in the event
of domain specific software to mitigate the use of bots, these parameters are already set as software defaults based on the observed behaviour of https://bbc.com.




RUNNING INSTRUCTIONS (crawler):

These instructions assume that the host machine has an up to date instance of Docker installed. These instructions have been tested against Docker Version 1.12.6 however any docker
version after version 1.0.1

IF DOCKER IS NOT INSTALLED ON THE HOST MACHINE:::  Please see section below under the heading 'Installation Instructions.'



BUILDING THE DOCKER IMAGE:

In order to run the crawler itself you will first need to use the docker file to build the docker image.

On an internet connected computer, point your terminal window (or command prompt) to the base directory of the downloaded files. This directory should hold a 'Dockerfile' and have various directories.


1: 
In a terminal window type:

docker build -t i_crawler:0.1 .

This should build a Docker image file based on the instructions in the Dockerfile.


![Building docker image](/resources/download_image.png)




RUNNING THE TEST SCRPIT


2.1:

Ensure you have completed step one (Building the docker image)


Once this has successfully finished, type:

docker run -it -v /tmp/results:/tmp/test-reports/ --name=c_crawler_test i_crawler:0.1 test_crawler.py


![Test output](/resources/test_output.png)


This will run a series of unit tests based on the functions within the crawler.Crawler class.
The outcome of the tests will be printed to STDOUT, this should only take a fraction of a second.
The script also generates a report showing the outcome of the tests in a .xml format. this can be found in the /tmp/results directory of the host machine.








RUNNING THE CRAWLER:


2.2:
Ensure you have completed step one (Building the docker image)


Once this has successfully finished, type:

docker run -it -v /tmp/results:/tmp/test-reports/ i_crawler:0.1 crawler.py


This will begin the crawl from the url specified. If no url is specified then crawler will begin from its default address: https://bbc.com.


![Crawl in progress indicator](/resources/progress_indication.png)



- The task specification stated that the final output should be to STDOUT. PLEASE BE PATIENT as in tests this has taken around mins at the default url. 
  A Crude progress indicator has been included for a better user experiance.
  
- Once the crawler is finished the visited sites and their static assets will be printed to STDOUT.






CLEANUP:

Once you are done testing the script:

Please remember to safely remove the docker container and its associated volumes by running:

docker rm -v c_crawler


and remove the docker image by typing:

docker rmi i_crawler:0.1








Installation instructions:


MAC

Prerequisites:
 - Mac hardware 2010 or newer
 - OSX 10.10.3 or newer (Yosemite)

Instructions:

To download, 'docker for mac':

- visit https://www.docker.com/products/overview
- Under Mac, select 'Download'
- Once downloaded install, double click on the .dmg file and in the window that opens, drag the image into applications folder
- Open a terminal window and verify the install by typing: docker version.



WINDOWS

Prerequisites:
	- Windows 10 64 bit

Before installing double check hardware virtualisation is turned on. To do this:
	- Go to control pannel > Programs and features > Turn windows features on or off
	- Make sure 'hyper v'  is ticked. If not tick and restart windows.
	- Go back to the settings in the control pannel and double check the hyper v is running 
	(If hyper v is still not running, and you feel comfortable to do so then  check hardware virtualisation is enabled in BIOS - NOT RECOMMENDED. instead proceed with mac or linux install)


To install 'Docker for Windows':
	- visit https://www.docker.com/products/overview
	- under Windows select 'Download'
	- Once downloaded: install by double clicking the icon and following the on-screen instructions
	- A successfully completed install is indicated by the presence of the Docker whale in the system tray




LINUX (Trialled on ubuntu)


To install Docker on Linux:

	- Open a terminal window and type:  wget -qO- https://get.docker.com | sh

This should download and install docker. It is also recommended to add any necessary users to the Docker user group. 

To do this type:
sudo user mod -aG docker (user)
 