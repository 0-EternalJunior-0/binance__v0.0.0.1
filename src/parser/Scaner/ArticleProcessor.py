class ArticleProcessor:
    """Клас для обробки статей."""
    @staticmethod
    async def filter_new_articles(results):
        """Фільтрує нові статті та додає мета-дані."""
        new_results = [
            {**article, "catalogId": catalogs.get('catalogId', "-Cacher.py"), "catalogName": catalogs.get('catalogName', "-Cacher.py")}
            for catalogs in results
            for article in catalogs.get('articles', [])
        ]
        return new_results
