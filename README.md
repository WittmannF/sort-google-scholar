# Sort Google Scholar by the Number of Citations

sortgs is a Python tool for ranking Google Scholar publications by the number of citations. It is useful for finding relevant papers in a specific field. The data acquired from Google Scholar includes Title, Citations, Links, Rank, and a new column with the number of citations per year. In the background, it first try to fetch results using python requests. If it fails, it will use selenium to fetch the results. 

## Try on Google Colab: [<img src="https://colab.research.google.com/assets/colab-badge.svg" align="center">](https://colab.research.google.com/github/WittmannF/sort-google-scholar/blob/master/Test_sortgs_py_on_Colab.ipynb)
  - No install requirements! Limitations: Can't handle robot checking, so use it carefully.

## Installation

You can now install `sortgs` directly using `pip`:

```bash
pip install sortgs
```

This will install the latest version of `sortgs` and its dependencies.

## Usage

Once installed, you can run `sortgs` directly from the command line:

```bash
sortgs "your keyword"
```

Replace `"your keyword"` with any keyword you'd like to search for. A CSV file with the name `your_keyword.csv` will be created in your current directory.

## Misc
If this project was helpful to you in any way, feel free to buy me a cup of coffee :)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=QAQ4YJFQVXLMA&source=url)

For a feedback, send me an email: fernando [dot] wittmann [at] gmail [dot] com

### Command Line Arguments

```bash
usage: sortgs [-h] [--sortby SORTBY] [--nresults NRESULTS] [--csvpath CSVPATH]
              [--notsavecsv] [--plotresults] [--startyear STARTYEAR]
              [--endyear ENDYEAR] [--debug] kw

positional arguments:
  kw                    Keyword to be searched. Use double quote followed by
                        simple quote for an exact keyword. 
                        Example: sortgs "'exact keyword'"

optional arguments:
  -h, --help            show this help message and exit
  --sortby SORTBY       Column to be sorted by. Default is "Citations". To sort
                        by citations per year, use --sortby "cit/year"
  --nresults NRESULTS   Number of articles to search on Google Scholar. Default
                        is 100. (careful with robot checking if value is high)
  --csvpath CSVPATH     Path to save the exported csv file. Default is the 
                        current folder
  --notsavecsv          By default, results are exported to a csv file. Select
                        this option to just print results but not store them
  --plotresults         Use this flag to plot results with the original rank on
                        the x-axis and the number of citations on the y-axis.
                        Default is False
  --startyear STARTYEAR
                        Start year when searching. Default is None
  --endyear ENDYEAR     End year when searching. Default is current year
  --debug               Debug mode. Used for unit testing. It will get pages
                        stored on web archive
```

### Examples

1. **Default Search**:
   ```bash
   sortgs "machine learning"
   ```
   This command searches for the top 100 results related to "machine learning" and saves them as a CSV file.

2. **Sort by Citations per Year**:
   ```bash
   sortgs "machine learning" --sortby "cit/year"
   ```
   Search for "machine learning" and sort by the number of citations per year.

3. **Specify Date Range**:
   ```bash
   sortgs "machine learning" --startyear 2005 --endyear 2015
   ```
   Search for papers from 2005 to 2015.

4. **Search for an Exact Keyword**:
   ```bash
   sortgs "'machine learning'"
   ```

5. **Save Results in a Specific Path**:
   ```bash
   sortgs 'neural networks' --csvpath './examples/'
   ```
   This will save the results under a subfolder called 'examples'.

6. **Multiple Keywords**:
   ```bash
   sortgs '"deep learning" OR "neural networks" OR "machine learning"' --sortby "cit/year"
   ```

### Output Example

While running, `sortgs` will provide updates in the terminal:

```
❯ sortgs "'machine learning'"
Running with the following parameters:
Keyword: 'machine learning', Number of results: 100, Save database: True, Path: /Users/wittmann/sort-google-scholar, Sort by: Citations, Plot results: False, Start year: None, End year: 2023, Debug: False
Loading next 10 results
Loading next 20 results
...
```

## Step-by-Step Installation
1. Install Python 3 and its dependencies from **Requirements** (suggestion: use Ananconda https://www.anaconda.com/distribution/)
2. In the terminal (or cmd if using Windows), run `pip install sortgs`
3. Use the command `sortgs "your keyword"` (replace "your keyword" to any keyword that you'd like to search)
4. A CSV file with the name `your_keyword.csv` should be created. 

If those steps are too complicated for you, send me an email with a list of keyworks that you'd like them ranked to: fernando [dot] wittmann [at] gmail [dot] com

## Requirements
If you install anaconda, all of those requirements (except selenium) are going to be met:
- Python 2.7 or Python 3
- Install from the requirements file: `pip install -r requirements.txt`

Highly suggested, if having problems with robot checking:
- ChromeDriver: http://chromedriver.chromium.org/
    - After downloading chromedriver, rename it to `chromedriver` and add it in a folder accessible by the PATH (Example: your python directory. Mine is at `/Users/.../anaconda/bin/`)

## Running Project Using Docker

This guide will walk you through the process of installing Docker, pulling the `fernandowittmann/sort-google-scholar` Docker image, and running the project.

### Step 1: Install Docker

#### Windows or Mac

1. **Download Docker Desktop**: Go to the [Docker Desktop website](https://www.docker.com/products/docker-desktop) and download the appropriate installer for your operating system.
2. **Install Docker Desktop**: Run the installer and follow the on-screen instructions.
3. **Verify Installation**: Open a terminal (or command prompt on Windows) and run `docker --version` to verify that Docker has been installed successfully.

#### Linux

1. **Update Package Index**: Run `sudo apt-get update` to update your package index.
2. **Install Docker**: Run `sudo apt-get install docker-ce docker-ce-cli containerd.io` to install Docker.
3. **Start Docker**: Run `sudo systemctl start docker` to start the Docker daemon.
4. **Verify Installation**: Run `docker --version` to ensure Docker is installed correctly.

### Step 2: Pull the Docker Image

1. **Pull Image**: Run the following command to pull the `fernandowittmann/sort-google-scholar` image from Docker Hub:

   ```bash
   docker pull fernandowittmann/sort-google-scholar
   ```

### Step 3: Run the Project

1. **Create a Results Directory**: Create a directory on your host machine where you want the results to be saved. For example, `mkdir ~/results`.
2. **Run the Docker Container**: Use the following command to run the container. This command mounts your results directory to the `/results` directory in the container and starts the sorting process for Google Scholar results based on your specified parameters.

   ```bash
   docker run -v "$PWD/results:/results" -it fernandowittmann/sort-google-scholar ./sortgs.py --kw "machine learning" --sortby "cit/year" --csvpath /results
   ```

   Replace `$PWD/results` with the absolute path to your results directory if you are not in the parent directory of `results`.


## Contributing
In order to make contributions, all of the tests must be passed. In order to test the code, we will be using the DEBUG mode which is going to use a URL from web archive. Please make sure to save the URL you want to test on web archive in case it is different from the one I already saved. By default it only works in debug mode when using the keywords 'machine learning'. There are 6 tests and all of them are testing different aspects that should match when using SortGS. In order to run the test cases, just run:
```
$python -m unittest
```

## LICENSE
- MIT
