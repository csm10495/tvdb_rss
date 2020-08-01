import datetime

from dataclasses import dataclass

@dataclass
class ShowInfo:
    show_name: str
    show_id: str = ''
    info_link: str = ''
    image_link: str = ''

@dataclass
class EpisodeInfo:
    show_info: ShowInfo
    episode_season: int
    episode_number: int
    first_aired: datetime.datetime
    episode_title: str = ''
    episode_description: str = ''
    info_link: str = ''
    image_link: str = ''

    def to_show_episode_string(self):
        return f'{self.show_info.show_name} - S{self.episode_season:02}E{self.episode_number:02} - {self.episode_title}'

    def get_available_image(self):
        return self.image_link or self.show_info.image_link

def to_dataclass(dc, _dict):
    return dc(**_dict)