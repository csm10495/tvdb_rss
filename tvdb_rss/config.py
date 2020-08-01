from .data_classes import to_dataclass, ShowInfo
from .setup_logger import getLogger

import dataclasses
import json
import pathlib

logger = getLogger(__file__)

'''
{
    'shows' : [
        { ShowInfo }
    ]
}
'''

class Config:
    ''' simple json wrapper '''
    def __init__(self, config_path):
        self.config_path = pathlib.Path(config_path)

        if self.config_path.exists():
            self.data = json.loads(self.config_path.read_text())
            logger.debug(f"Loaded config data from: {self.config_path}")
        else:
            logger.debug(f"Config file didn't exist: {self.config_path}. Using empty config.")
            self.data = {}

    def get_shows_list(self):
        raw_shows = self.data.get('shows', [])
        return [to_dataclass(ShowInfo, d) for d in raw_shows]

    def add_show(self, show_info):
        if 'shows' not in self.data:
            self.data['shows'] = []

        self.data['shows'].append(dataclasses.asdict(show_info))

    def save_changes(self):
        self.config_path.write_text(json.dumps(self.data))