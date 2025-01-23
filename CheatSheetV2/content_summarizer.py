import asyncio
from typing import List
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from heapq import nlargest

nltk.download('punkt')
nltk.download('stopwords')

class ContentSummarizer:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))

    async def summarize_content(self, content: str, num_sentences: int = 3) -> str:
        sentences = sent_tokenize(content)
        words = word_tokenize(content.lower())
        word_frequencies = self._calculate_word_frequencies(words)
        sentence_scores = self._calculate_sentence_scores(sentences, word_frequencies)
        summary_sentences = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
        return summary

    def _calculate_word_frequencies(self, words: List[str]) -> FreqDist:
        return FreqDist(word for word in words if word not in self.stopwords and word.isalnum())

    def _calculate_sentence_scores(self, sentences: List[str], word_frequencies: FreqDist) -> dict:
        max_frequency = max(word_frequencies.values())
        sentence_scores = {}

        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies.keys():
                    if len(sentence.split()) < 30:
                        if sentence not in sentence_scores:
                            sentence_scores[sentence] = 0
                        sentence_scores[sentence] += word_frequencies[word] / max_frequency

        return sentence_scores
