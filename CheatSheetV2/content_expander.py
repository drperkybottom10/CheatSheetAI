import asyncio
from typing import List
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import wordnet
import random

nltk.download('punkt')
nltk.download('wordnet')

class ContentExpander:
    def __init__(self):
        self.expansion_templates = [
            "In other words, {}",
            "To put it differently, {}",
            "This means that {}",
            "Specifically, {}",
            "For instance, {}",
            "As an illustration, {}",
            "Furthermore, {}",
            "Additionally, {}",
            "Moreover, {}",
            "In addition to this, {}"
        ]

    async def expand_content(self, content: str, expansion_factor: float = 1.5) -> str:
        sentences = sent_tokenize(content)
        expanded_sentences = []

        for sentence in sentences:
            expanded_sentences.append(sentence)
            if random.random() < expansion_factor - 1:
                expanded_sentence = await self.expand_sentence(sentence)
                expanded_sentences.append(expanded_sentence)

        return ' '.join(expanded_sentences)

    async def expand_sentence(self, sentence: str) -> str:
        words = word_tokenize(sentence)
        pos_tags = nltk.pos_tag(words)
        
        key_words = [word for word, pos in pos_tags if pos.startswith('NN') or pos.startswith('VB') or pos.startswith('JJ')]
        
        if key_words:
            chosen_word = random.choice(key_words)
            definition = await self.get_word_definition(chosen_word)
            if definition:
                expansion = random.choice(self.expansion_templates).format(definition)
                return f"{sentence} {expansion}"
        
        return sentence

    async def get_word_definition(self, word: str) -> str:
        synsets = wordnet.synsets(word)
        if synsets:
            return synsets[0].definition()
        return ""
