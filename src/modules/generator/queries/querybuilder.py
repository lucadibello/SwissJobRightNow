import urllib.parse as parser

class QueryBuilder:
  __LOCAL_BASE_QUERY_STRING = "https://www.local.ch/it/q"
  
  @classmethod
  def build_page_query_link (cls, region: str, jobKind: str, onlyCompanies: bool = True) -> str:
    # Build URL
    baseString = cls.__LOCAL_BASE_QUERY_STRING + "/" + parser.quote(region) + "/" + parser.quote(jobKind)
 
    if onlyCompanies:
      # Add filter for companies
      baseString += "?filter[entry_type]=business"
    
    # Return query string
    return baseString