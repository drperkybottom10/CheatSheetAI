import asyncio
from typing import List, Tuple
import aiohttp
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')

class PlagiarismChecker:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    async def check_plagiarism(self, content: str, threshold: float = 0.8) -> Tuple[bool, List[str]]:
        sentences = sent_tokenize(content)
        vectors = self.vectorizer.fit_transform(sentences)
        similarity_matrix = cosine_similarity(vectors)

        plagiarized_sentences = []
        for i in range(len(sentences)):
            for j in range(i + 1, len(sentences)):
                if similarity_matrix[i][j] > threshold:
                    plagiarized_sentences.append(sentences[i])
                    break

        is_plagiarized = len(plagiarized_sentences) > 0
        return is_plagiarized, plagiarized_sentences

    async def check_online_plagiarism(self, content: str, api_key: str) -> Tuple[bool, List[str]]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.copyleaks.com/v3/plagiarism/check",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={"text": content}
            ) as response:
                result = await response.json()

        is_plagiarized = result.get("plagiarismPercentage", 0) > 0
        plagiarized_sources = [source["url"] for source in result.get("results", [])]
        return is_plagiarized, plagiarized_sources
