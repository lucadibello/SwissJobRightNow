import urllib.parse as parser

class QueryBuilder:
  __LOCAL_BASE_QUERY_STRING = "https://www.local.ch/it/q"
  
  @classmethod
  def build_page_query_link (cls, area: str, jobKind: str, isAreaARegion: bool, isAreaACanton: bool, onlyCompanies: bool = True) -> str:
    # Build area string
    if (isAreaARegion):
      area += " (Regione)"
    elif (isAreaACanton):
      area += " (Canton)"

    # Build URL
    baseString = cls.__LOCAL_BASE_QUERY_STRING + "/" + parser.quote(area) + "/" + parser.quote(jobKind)
 
    if onlyCompanies:
      # Add filter for companies + page flag
      baseString += "?filter[entry_type]=business&page="
    else:
      baseString += "?page="
    
    # Return query string
    return baseString