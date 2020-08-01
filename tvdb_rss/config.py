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

            # remove duplicates and sort
            self.data['shows'] = [dict(t) for t in {tuple(d.items()) for d in self.data['shows']}]
            self.data['shows'] = list(sorted(self.data['shows'], key=lambda x:x['show_name']))

            logger.debug(f"Loaded config data from: {self.config_path}")
        else:
            logger.debug(f"Config file didn't exist: {self.config_path}. Using empty config.")
            self.data = {}
            self.data['shows'] = []

    def get_shows_list(self):
        raw_shows = self.data.get('shows', [])
        return [to_dataclass(ShowInfo, d) for d in raw_shows]

    def add_show(self, show_info):
        self.data['shows'].append(dataclasses.asdict(show_info))

    def remove_show(self, show_info_or_name):
        if isinstance(show_info_or_name, ShowInfo):
            show_name = show_info_or_name.show_name
        else:
            show_name = show_info_or_name

        for show in self.data['shows']:
            if show['show_name'] == show_name:
                self.data['shows'].remove(show)
                logger.debug(f"Removed show: {show_name}")
                return

        raise KeyError(f"Show was not found in config: {show_name}")

    def save_changes(self):
        self.config_path.write_text(json.dumps(self.data))