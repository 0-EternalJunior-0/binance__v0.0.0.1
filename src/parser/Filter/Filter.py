from src.parser.Cacher.Cacher import Cacher
from src.logger import logger


class Filter:
    def __init__(self):
        self.cacher = Cacher()
    async def filter_cacher(self, data):
        cacher = self.cacher.load_checkIdArticles()
        if data['id'] not in cacher:
            cacher.add(data['id'])
            self.cacher.save_checkIdArticles(cacher)
            await logger.info('new article')
            return data
        return None