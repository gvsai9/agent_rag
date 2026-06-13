# ingestion/pmc_fetcher.py

import requests #We import the requests library, which is used to make HTTP requests to the PMC API. We will use this library to send GET requests to the API endpoints and retrieve the search results, metadata, and XML content of papers.
from models.paper import PaperMetadata #We import the PaperMetadata dataclass from the models.paper module. This dataclass is used to represent the metadata of a paper, including its PMCID, title, publication year, and authors. We will use this dataclass to create objects that hold the metadata of papers retrieved from the PMC database.
from pathlib import Path #We import the Path class from the pathlib module, which provides an object-oriented interface for working with file system paths. We will use this class to create directories and save XML files of papers in a structured way.


# This API is used for esearch
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

#This API is used for esummary
SUMMARY_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
)

#This API is used for efetch to download the full XML of a paper given its PMCID.
FETCH_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
)

#This function is used to search for papers in PMC using a query and return a list of PMCIDs.
def search_pmc(query: str, limit: int = 10) -> list[str]:

    #parameters for the API request
    params = {
        "db": "pmc", #search in the PMC database
        "term": query, #the search query
        "retmax": limit, #the maximum number of results to return
        "retmode": "json" #return the results in JSON format
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    #The PMIDs are located in the "idlist" field of the "esearchresult" field in the response JSON. We return this list of PMCIDs.
    return data.get("esearchresult", {}).get("idlist", [])



#This function is used to get the metadata of papers given a list of PMIDs. It returns a list of PaperMetadata objects.
def get_metadata(pmc_ids: list[str]) -> list[PaperMetadata]:


    #parameters for the API request to get the metadata of the papers. We specify the database as "pmc", the list of PMIDs as a comma-separated string, and the return mode as JSON.
    params = {
        "db": "pmc",
        "id": ",".join(pmc_ids),
        "retmode": "json"
    }

    response = requests.get(
        SUMMARY_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    papers = []

    result = data["result"]

    for uid in result["uids"]:

        paper = result[uid]

        ids_in_a_paper = paper.get("articleids", [])
        pmcid = None

        #The PMCID is located in the "articleids" field of each paper in the response JSON. We iterate through the list of article IDs and look for the one with the "idtype" of "pmcid". If we find it, we extract the value of the PMCID and break out of the loop. If we don't find a PMCID, we skip this paper and move on to the next one.
        for id_info in ids_in_a_paper:
            if id_info.get("idtype") == "pmcid":
                pmcid = id_info.get("value")
                break
        if not pmcid:
            continue

        title = paper.get("title", "")

        pubdate = paper.get("pubdate", "")

        year = None

        #The publication date is usually in the format "YYYY MM DD" or "YYYY". We try to extract the year from the publication date. If the publication date is not in a valid format, we ignore it and set the year to None.
        if pubdate:
            try:
                year = int(pubdate[:4])
            except ValueError:
                pass
        authors = paper.get("authors", [])
        author_names = [author.get("name", "") for author in authors]


        #We create a PaperMetadata object for each paper and append it to the list of papers. We use the PMCID, title, year, and author names to create the PaperMetadata object.
        papers.append(
            PaperMetadata(
                pmcid=pmcid,
                title=title,
                year=year,
                authors=author_names
            )
        )

    return papers



#This function is used to download the full XML of a paper given its PMCID. It returns the XML content as a string.
def download_xml(pmcid: str) -> str:

    #parameters for the API request to download the full XML of a paper. We specify the database as "pmc", the PMCID of the paper, and the return mode as XML.
    params = {
        "db": "pmc",
        "id": pmcid,
        "retmode": "xml"
    }

    response = requests.get(
        FETCH_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()


    #The XML content of the paper is located in the response text. 
    # We return this XML content as a string. If the XML content is empty, we raise a RuntimeError.    
    xml_content = response.text


    # We check if the XML content contains the "<article" tag, which indicates that the XML is not empty and contains the full article. 
    # If the "<article" tag is not found in the XML content, we raise a RuntimeError indicating that an empty XML was returned for the given PMCID. This is a simple way to check if the API returned a valid XML for the paper.
    if "<article" not in xml_content:
        raise RuntimeError(
            f"Empty XML returned for {pmcid}"
        )

    return xml_content

#This function is used to save the XML content of a paper to a file. It takes the PMCID of the paper and the XML content as input, and it returns the path to the saved XML file. The XML files are saved in a "data/raw" directory, with the filename format "{pmcid}.xml". If the "data/raw" directory does not exist, it is created.

def save_xml(
    pmcid: str,
    xml_content: str
) -> Path:

    raw_dir = Path("data/raw")

    raw_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = raw_dir / f"{pmcid}.xml"

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(xml_content)

    return file_path

if __name__ == "__main__":
    id_list = search_pmc("diabetes", limit=5)
    metadata = get_metadata(id_list)
    PMCIDs = [paper.pmcid for paper in metadata]
    XML_content = download_xml(PMCIDs[0])
    path = save_xml(PMCIDs[0], XML_content)
    print(path)
    
        