import asyncio
from typing import List
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
import random

nltk.download('punkt')
nltk.download('wordnet')

class ContentParaphraser:
    def __init__(self):
        self.synonyms_cache = {}

    async def paraphrase_content(self, content: str) -> str:
        sentences = sent_tokenize(content)
        paraphrased_sentences = await asyncio.gather(*[self.paraphrase_sentence(sentence) for sentence in sentences])
        return ' '.join(paraphrased_sentences)

    async def paraphrase_sentence(self, sentence: str) -> str:
        words = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)
        
        paraphrased_words = []
        for word, pos in pos_tags:
            if pos.startswith('NN') or pos.startswith('VB') or pos.startswith('JJ') or pos.startswith('RB'):
                synonym = await self.get_synonym(word)
                paraphrased_words.append(synonym if synonym else word)
            else:
                paraphrased_words.append(word)
        
        return ' '.join(paraphrased_words)

    async def get_synonym(self, word: str) -> str:
        if word in self.synonyms_cache:
            return random.choice(self.synonyms_cache[word])

        synonyms = []
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                if lemma.name() != word:
                    synonyms.append(lemma.name())

        if synonyms:
            self.synonyms_cache[word] = synonyms
            return random.choice(synonyms)
        return word
