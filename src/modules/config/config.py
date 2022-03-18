import json

class Config:

  def __init__(self, config_file_path: str):
    self.configFile = json.load(open(config_file_path, "r"))

  def getConfig(self) -> dict:
    return self.configFile  