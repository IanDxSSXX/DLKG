import hashlib
from const import BASE_URL

def generate_paper_id(title, authors, year):
  combined_string = title + "".join(authors) + str(year)
  result = hashlib.sha256(combined_string.encode()).hexdigest()
  return result

def generate_author_id(name, profile_link):
  combined_string = name + profile_link if profile_link else name
  result = hashlib.sha256(combined_string.encode()).hexdigest()
  return result


def author_url(name):
  return f"{BASE_URL}/citations?user={name}"

def author_url(name):
  return f"{BASE_URL}/citations?user={name}"