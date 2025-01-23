import asyncio
from typing import List, Tuple
import aiohttp
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re

nltk.download('punkt')
nltk.download('stopwords')

class ContentFactChecker:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    async def check_facts(self, content: str) -> List[Tuple[str, bool, str]]:
        sentences = sent_tokenize(content)
        fact_check_results = await asyncio.gather(*[self.check_sentence(sentence) for sentence in sentences])
        return [result for result in fact_check_results if result is not None]

    async def check_sentence(self, sentence: str) -> Tuple[str, bool, str]:
        keywords = self.extract_keywords(sentence)
        if not keywords:
            return None

        search_query = ' '.join(keywords)
        search_results = await self.search_web(search_query)

        if not search_results:
            return sentence, False, "No relevant information found"

        fact_verified, source = await self.verify_fact(sentence, search_results)
        return sentence, fact_verified, source

    def extract_keywords(self, sentence: str) -> List[str]:
        words = nltk.word_tokenize(sentence.lower())
        return [word for word in words if word.isalnum() and word not in self.stop_words]

    async def search_web(self, query: str) -> List[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.google.com/search?q={query}") as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        search_results = []
        for result in soup.find_all('div', class_='g'):
            link = result.find('a')
            if link and 'href' in link.attrs:
                search_results.append(link['href'])

        return search_results[:5]  # Limit to top 5 results

    async def verify_fact(self, sentence: str, search_results: List[str]) -> Tuple[bool, str]:
        for url in search_results:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            page_text = soup.get_text()

            if self.sentence_similarity(sentence, page_text) > 0.7:
                return True, url

        return False, "No reliable source found"

    def sentence_similarity(self, sentence1: str, sentence2: str) -> float:
        words1 = set(self.extract_keywords(sentence1))
        words2 = set(self.extract_keywords(sentence2))

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0

class FactCheckingResult:
    def __init__(self, sentence: str, is_verified: bool, source: str):
        self.sentence = sentence
        self.is_verified = is_verified
        self.source = source

    def __str__(self):
        status = "Verified" if self.is_verified else "Unverified"
        return f"{status}: {self.sentence}\nSource: {self.source}"
