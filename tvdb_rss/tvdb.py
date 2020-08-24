import datetime
import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .data_classes import EpisodeInfo, ShowInfo
from .setup_logger import getLogger
logger = getLogger(__file__)

API_ROOT = 'https://api.thetvdb.com'

class TVDBClient:
    def __init__(self, username, user_key, api_key):
        self.username = username
        self.user_key = user_key
        self.api_key = api_key

        # private
        self._session = self.__get_new_session()
        self._token = None
        self._token_death_time = 0

    @classmethod
    def __get_new_session(cls):
        ''' gets a session that will auto-retry 500/504s '''
        session = requests.Session()
        RETRY_COUNT = 25
        retry = Retry(
            total=RETRY_COUNT,
            read=RETRY_COUNT,
            connect=RETRY_COUNT,
            status=RETRY_COUNT,
            redirect=RETRY_COUNT,
            backoff_factor=.00001,
            status_forcelist=(500, 502, 504),
            method_whitelist=False, # retry on any method matching above status codes
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _authenticate(self):
        logger.debug("Attempting authentication")
        result = self._request('post', f'{API_ROOT}/login', json={
            'apikey': str(self.api_key),
            'userkey': str(self.user_key),
            'username': str(self.username),
        }, renew_auth_if_needed=False)

        self._token = result.json()['token']
        self._session.headers.update({
            'Authorization' : f'Bearer {self._token}'
        })

        # renew every 23 hours
        self._token_death_time = time.time() + (60 * 60 * 23)

    def _renew_authentication_if_needed(self):
        if self._token is None:
            self._authenticate()

        if time.time() > self._token_death_time:
            logger.debug("Renewing token")
            result = self._request('get', f'{API_ROOT}/refresh_token', renew_auth_if_needed=False)

            # renew every 23 hours
            self._token_death_time = time.time() + (60 * 60 * 23)

    def _request(self, method, url, json=None, renew_auth_if_needed=True, *args, **kwargs):
        if renew_auth_if_needed:
            self._renew_authentication_if_needed()

        logger.debug(f"Performing a {method.upper()} to {url}")

        result = self._session.request(method, url, json=json, *args, **kwargs)
        result.raise_for_status()
        return result

    def _get_data_with_paging(self, url, *args, **kwargs):
        # will update these in the loop
        page = 1
        last_page = 1

        params = kwargs.get('params', {})

        data = []

        while page <= last_page:
            params['page'] = page
            logger.debug(f"Requesting page: {page}")

            result = self._request('get', url, params=params)
            result.raise_for_status()
            last_page = result.json()['links']['last']

            data.extend(result.json()['data'])
            page += 1

        return data

    def _db_episode_to_episode_info(self, show_info, raw):
        e = EpisodeInfo(
            show_info=show_info,
            episode_season=raw['airedSeason'],
            episode_number=raw['airedEpisodeNumber'],
            first_aired=datetime.datetime.fromisoformat(raw['firstAired']),
            episode_title=raw['episodeName'],
            episode_description=raw['overview'],
            info_link=f'https://thetvdb.com/series/{show_info.show_name}/episodes/{raw["id"]}',
            image_link=f'https://artworks.thetvdb.com/banners/{raw["filename"]}' if raw['filename'] else '',
        )
        return e

    def _db_series_to_show_info(self, db_show_info):
        return ShowInfo(
            show_name=db_show_info['seriesName'],
            show_id=str(db_show_info['id']),
            info_link=f'https://www.thetvdb.com/series/{db_show_info["slug"]}',
            image_link=f'https://artworks.thetvdb.com{db_show_info["poster"]}',
        )

    def get_shows_info(self, show_name):
        result = self._request('get', f'{API_ROOT}/search/series', params={
            'name' : show_name
        })

        db_show_info = result.json()['data']
        return [self._db_series_to_show_info(a) for a in db_show_info]

    def get_show_info(self, show_name):
        return self.get_shows_info(show_name)[0]

    def get_all_episodes(self, show_name):
        show_info = self.get_show_info(show_name)
        raw_episode_data = self._get_data_with_paging(f'{API_ROOT}/series/{show_info.show_id}/episodes')
        episodes = []
        for raw in raw_episode_data:
            episodes.append(self._db_episode_to_episode_info(show_info, raw))

        return episodes

    def get_episodes_by_first_air_date(self, show_info, date):
        try:
            raw_list = self._request('get', f'https://api.thetvdb.com/series/{show_info.show_id}/episodes/query', params={
                'firstAired': date.strftime('%Y-%m-%d')}).json()['data']
        except Exception as ex:
            # 404 means nothing on that day
            if '404' in str(ex):
                return []
            raise

        return [(self._db_episode_to_episode_info(show_info, r)) for r in raw_list]

