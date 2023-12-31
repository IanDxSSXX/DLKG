import requests
from bs4 import BeautifulSoup, NavigableString
import re
from utils import *
from const import *

all_authors = {}
all_papers = {}

def parse_paper_element(paper_element):
  paper = {
    "year": None,
    "pdf": None,
    "authors": [],
    "citedBy": []
  }
  content_element = paper_element.select_one(".gs_ri")

  # ---- pdf
  pdf_element = paper_element.select_one(".gs_ggs.gs_fl")
  if pdf_element:
    paper["pdf"] = pdf_element.select_one("a")["href"]

  # ---- info
  paper["title"] = content_element.select_one("a").text
  paper["link"] = content_element.select_one("a")["href"]

  # ---- authors
  authors_element = content_element.select_one(".gs_a")
  for author_element in authors_element.children:
    profile_link = None
    if isinstance(author_element, NavigableString): 
        year_match = re.search(r'(\b[12]\d{3}\b)', author_element)
        if year_match:
          year = year_match.group(0)
          paper["year"] = year

        author_str = author_element.split("-")[0].strip()
        if author_str in ["", ","]:
          continue
        name = author_str
    elif author_element.name == "a": 
        name = author_element.text
        user_id = get_path_param(author_element["href"], "user")
        if user_id:
          profile_link = author_url(user_id)

    author_id = generate_author_id(name, profile_link)
    all_authors[author_id] = { "name": name, "profileLink": profile_link, "authorId": author_id }
    paper["authors"].append(author_id)

  # ---- id
  paper["paperId"] = generate_paper_id(paper["title"], paper["authors"], paper["year"])

  # ---- cited by
  cite_elements = content_element.select_one(".gs_fl.gs_flb")
  cite_by_elements = list(filter(
    lambda x: x.text.startswith("Cited by"), 
    list(cite_elements.children)
  ))
  if len(cite_by_elements) > 0:
    cite_by_element = cite_by_elements[0]
    if (cite_by_element):
      citation_id = get_path_param(cite_by_element["href"], "cites")
      if citation_id:
        citation_url = paper_cite_url(citation_id)
        paper["citedBy"] = search_papers(citation_url)


  all_papers[paper["paperId"]] = paper
  print(paper["title"], paper["link"])
  return paper["paperId"]

def search_papers(url):
  if len(all_papers) >= TOTAL_PAPER_NUM:
    return
  response = requests.get(url, headers=HEADERS)
  paper_ids = []
  next_page_element = False
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    for result in soup.select(".gs_r.gs_or.gs_scl"):
      paper_ids.append(parse_paper_element(result))
      break
    next_page_element = soup.select_one('.gs_ico_nav_next')
  else:
    print(f"Failed to retrieve {url}.")
    print(response.text)
  
  if next_page_element:
    paper_ids.extend(search_papers(next_page_url(url)))
  
  return paper_ids

def main():
  search_papers(paper_url("resnet deep learning"))

if __name__ == "__main__":
  main()
  write_papers(all_papers)
