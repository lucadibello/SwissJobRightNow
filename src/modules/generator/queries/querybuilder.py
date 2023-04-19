import urllib.parse as parser

class QueryBuilder:
  __LOCAL_BASE_QUERY_STRING = "https://www.local.ch/it/s"
  
  @classmethod
  def build_page_query_link (cls, area: str, jobKind: str, isAreaARegion: bool, isAreaACanton: bool) -> str:
    # Build area string
    if (isAreaARegion):
      area += " (Regione)"
    elif (isAreaACanton):
      area += " (Canton)"

    # Build URL
    baseString = cls.__LOCAL_BASE_QUERY_STRING + "/" + parser.quote(area) + "/" + parser.quote(jobKind)
    baseString += "?&search=s&page="
    
    # Return query string
    return baseString