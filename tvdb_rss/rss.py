import datetime
import multiprocessing.dummy
from .setup_logger import getLogger

from feedgen.feed import FeedGenerator

logger = getLogger(__file__)

class RSSGenerator:
    def __init__(self, client, config):
        self.client = client
        self.config = config

    def get_episodes_info(self, date=None, max_days_back=14):
        if date is None:
            date = datetime.datetime.today()

        shows_list = self.config.get_shows_list()

        episodes_in_date_order = []
        for days_back in range(max_days_back):
            date_after_days_back = date - datetime.timedelta(days=days_back)
            logger.debug(f"Looking for episodes released on: {date_after_days_back}")
            for show_info in shows_list:
                logger.debug(f"  Looking for show: {show_info.show_name}")
                episodes_in_date_order.extend(self.client.get_episodes_by_first_air_date(show_info, date_after_days_back))

        return episodes_in_date_order

    def generate_rss_string(self, date=None, max_days_back=14):
        episodes_in_data_order = self.get_episodes_info(date, max_days_back)
        fg = FeedGenerator()
        fg.id('')
        fg.link(href='https://github.com/csm10495/tvdb_rss')
        fg.title('tvdb_rss')
        fg.author(name='Charles Machalow')
        fg.language('en')
        fg.description('Generated tvdb_rss RSS')

        for episode_info in reversed(episodes_in_data_order):
            fe = fg.add_entry()
            fe.id(episode_info.info_link)
            fe.link(href=episode_info.info_link)
            fe.title(episode_info.to_show_episode_string())
            fe.summary(episode_info.episode_description)
            fe.pubDate(episode_info.first_aired.replace(tzinfo=datetime.timezone.utc))

            image_html = f'<img src="{episode_info.get_available_image()}" title="{episode_info.episode_description}"/>'
            fe.description(image_html)

        return fg.rss_str(pretty=True).decode()
