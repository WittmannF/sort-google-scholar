# Sort Google Scholar by the Number of Citations
[![PyPI Version](https://img.shields.io/pypi/v/sortgs.svg)](https://pypi.org/project/sortgs/)

sortgs is a Python tool for ranking Google Scholar publications by the number of citations. It is useful for finding relevant papers in a specific field. The data acquired from Google Scholar includes Title, Citations, Links, Rank, and a new column with the number of citations per year. In the background, it first try to fetch results using python requests. If it fails, it will use selenium to fetch the results. 

## 🚀 Run it on Google Colab
- **No-Code Version (new!)**:  [<img src="https://colab.research.google.com/assets/colab-badge.svg" align="center">](https://colab.research.google.com/github/WittmannF/sort-google-scholar/blob/master/examples/Sort_Google_Scholar_No_Code_Version.ipynb)  — *No coding required! Perfect for a quick start!* ⚡  
- **Code Version:** [<img src="https://colab.research.google.com/assets/colab-badge.svg" align="center">](https://colab.research.google.com/github/WittmannF/sort-google-scholar/blob/master/examples/run_sortgs_on_colab.ipynb)— *For developers who want full control of what's behind the scenes!* 💻

> 💡 **All you need** is a Google Account to get started.  
> ⚠️ **Note**: Google Scholar may block access after too many repetitive requests due to CAPTCHA checks, so proceed mindfully! See the [optional SearchApi provider](#optional-searchapi-provider) for automated retrieval and its current limitations.

## 📚 Colab No-Code Instructions
https://github.com/user-attachments/assets/25de7bad-2a5d-4bcf-b486-faa1d7a29eb3


## Installation

You can install `sortgs` directly using `pip`:

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

## Optional SearchApi provider

For automated workflows or searches affected by Google Scholar CAPTCHA checks,
SearchApi provides an optional retrieval path using your own API key, without
launching a browser. The default direct Google Scholar workflow remains available.
The Python Selenium dependency is still installed, but is not used by this provider.

**Current limitation (September 2026):** our live SearchApi checks returned papers
but omitted citation counts, including for well-known cited papers. Missing counts
are exported as `0` for compatibility; **this does not mean a paper has no citations**.
The CLI warns when an entire response lacks counts. Citation ranking is meaningful
only when the provider supplies them. The complete public “Phantom physics” example
is covered by offline tests that verify all ten citation counts, both ranking
options and every CSV field. This upstream limitation needs resolution
before treating SearchApi as a complete replacement for citation-based ranking.

Create a SearchApi account through our [affiliate link](https://www.searchapi.io/?via=wittmannf),
then obtain your API key from the account dashboard.

**Disclosure:** SearchApi sponsors this integration. The maintainer may also earn
a commission if you purchase a subscription through the affiliate link.

For the unreleased implementation, install from this checkout with `uv pip install -e .`
in your virtual environment. A previously published package/image may not support these options.

```bash
export SEARCH_API_KEY="YOUR_API_KEY"
sortgs "machine learning" --provider searchapi --nresults 100
```

`YOUR_API_KEY` is a placeholder. Configure the real value privately in your environment
or secret manager. sortgs does not load `.env` automatically; `.env.example` only
documents the variable. Never put a real key into a saved notebook or source file.
A missing key fails before any request. Merely setting a key never selects SearchApi,
and there is no automatic switch between providers.

The existing year/language filters, `--sortby`, CSV options and `--plotresults` apply.
`--debug` uses the Web Archive and cannot be combined with SearchApi. Both providers
require a positive `--nresults`. Unknown arguments trigger a warning; check spelling,
especially `--provider`, since ignored arguments do not select the provider.

SearchApi retrieves up to 20 results per page. With full pages, 10/20/50/100/101
results require 1/1/3/5/6 searches. The final page is truncated locally to the requested
count; the legacy direct path can exceed the requested count. Queries with short or
repeated pages may return fewer rows. By default, up to two additional pages are
allowed. To set a different ceiling explicitly:

```bash
sortgs "machine learning" --provider searchapi --nresults 100 --searchapi-max-pages 10
```

Warnings distinguish source exhaustion, repeated results and the page ceiling. A
limited one-time retry is made for connection-establishment timeouts and HTTP
502/503/504, subject to the server's retry guidance. Read timeouts and HTTP 429 are
not automatically retried. A failed later page does not write or overwrite a CSV;
earlier successful requests may already have used credits.

Our development searches were charged one credit each, including a successful
zero-result response. Requests and charges may vary with service terms; see
[SearchApi pricing](https://www.searchapi.io/pricing) and
[Scholar API documentation](https://www.searchapi.io/docs/google-scholar).
The runtime does not send affiliate identifiers or add analytics.

### Colab and Docker

In Colab, install a version containing the integration, add `SEARCH_API_KEY` in the
Secrets panel, grant the notebook access, and load it without printing it:

```python
import os
from google.colab import userdata

os.environ["SEARCH_API_KEY"] = userdata.get("SEARCH_API_KEY")
!sortgs "machine learning" --provider searchapi
```

This is a manual CLI setup; existing no-code notebooks do not expose a provider selector.

For Docker, use an image containing this integration and forward an already exported
host variable without putting its value in the command. `SORTGS_IMAGE` below should
identify that image; the published image is not assumed to include unreleased code:

```bash
docker run --rm -e SEARCH_API_KEY \
  -v "$PWD/sortgs-results:/app" "$SORTGS_IMAGE" \
  "machine learning" --provider searchapi
```

The repository Dockerfile installs the package from PyPI, so building it before a
package release does not test local source changes.

## Misc
For a feedback, send me an email: fernando [dot] wittmann [at] gmail [dot] com

### Command Line Arguments

```bash
usage: sortgs [-h] [--sortby SORTBY] [--nresults NRESULTS] [--csvpath CSVPATH]
              [--notsavecsv] [--plotresults] [--startyear STARTYEAR]
              [--endyear ENDYEAR] [--debug] [--provider {direct,searchapi}]
              [--searchapi-max-pages SEARCHAPI_MAX_PAGES] kw

positional arguments:
  kw                    Keyword to be searched. Use double quote followed by
                        simple quote for an exact keyword. 
                        Example: sortgs "'exact keyword'"

optional arguments:
  -h, --help            show this help message and exit
  --sortby SORTBY       Column to be sorted by. Default is "Citations". To sort
                        by citations per year, use --sortby "cit/year"
  --langfilter LANGFILTER [LANGFILTER ...]
                        Only languages listed are permitted to pass the filter. 
                        List of supported language codes: zh-CN, zh-TW, nl, en, fr,
                        de, it, ja, ko, pl, pt, es, tr
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
  --provider {direct,searchapi}
                        Retrieval provider (default: direct).
  --searchapi-max-pages SEARCHAPI_MAX_PAGES
                        Explicit page ceiling for SearchApi.
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

7. **Language Filter**:
   ```bash
   sortgs "machine learning" --langfilter pt es fr de
   ```
   This will only include articles in Portuguese, Spanish, French, and German.

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

## Conda Environment Setup

### Creating the Environment
```
conda env create -f conda_environment.yml
```

### Reset the environment
```
conda deactivate
conda remove --name sortgs --all
conda env create -f environment.yml
```

### Activate the environment
```
conda activate sortgs
```

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

1. **Run the Docker Container**: Use the following command to run the container:

   ```bash
   docker run -v "$PWD/sortgs-results:/app" fernandowittmann/sort-google-scholar "machine learning" 
   ```

   Replace `$PWD` with the absolute path to your results directory if you are not in the parent directory of `sortgs-results`.


## Contributing
We use `pytest` for our test suite. To run all tests, install pytest and run:
```bash
pip install pytest
pytest
```
or:
```bash
python -m pytest
```
Ensure all tests pass before submitting a PR; GitHub Actions will also execute the test suite on each push.

## About Robot Check
Google Scholar may block access after too many repetitive requests due to CAPTCHA checks. If this issue arrises, selenium will be used to attempt to fetch the results. You might be asked to solve a CAPTCHA manually. Ideally, you should use a VPN to avoid this issue. When using selenium, you might need to install chromedriver. You can download it from https://developer.chrome.com/docs/chromedriver/downloads and add it to your PATH.

## LICENSE
- MIT

## Updates
Main branch has been renamed from master. Update it locally by running:
```sh
git branch -m master main
git fetch origin
git branch -u origin/main main
git remote set-head origin -a
```
## 💖 Support the Project

If you find this project helpful and would like to support its development, consider making a donation. Your support is greatly appreciated!

[Donate via Wise](https://wise.com/pay/me/fernandow21)

