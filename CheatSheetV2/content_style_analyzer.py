import asyncio
from typing import Dict, List
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import cmudict
import re

nltk.download('cmudict')

class ContentStyleAnalyzer:
    def __init__(self):
        self.pronouncing_dict = cmudict.dict()

    async def analyze_style(self, content: str) -> Dict[str, float]:
        sentences = sent_tokenize(content)
        words = word_tokenize(content.lower())

        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        lexical_diversity = len(set(words)) / len(words)
        readability_score = await self.calculate_flesch_kincaid_grade(content)

        return {
            "avg_sentence_length": avg_sentence_length,
            "avg_word_length": avg_word_length,
            "lexical_diversity": lexical_diversity,
            "readability_score": readability_score
        }

    async def adjust_style(self, content: str, target_style: Dict[str, float]) -> str:
        current_style = await self.analyze_style(content)
        
        if current_style["avg_sentence_length"] > target_style["avg_sentence_length"]:
            content = await self.shorten_sentences(content)
        elif current_style["avg_sentence_length"] < target_style["avg_sentence_length"]:
            content = await self.lengthen_sentences(content)

        if current_style["lexical_diversity"] < target_style["lexical_diversity"]:
            content = await self.increase_vocabulary_diversity(content)

        if current_style["readability_score"] > target_style["readability_score"]:
            content = await self.simplify_vocabulary(content)
        elif current_style["readability_score"] < target_style["readability_score"]:
            content = await self.sophisticate_vocabulary(content)

        return content

    async def calculate_flesch_kincaid_grade(self, text: str) -> float:
        sentences = sent_tokenize(text)
        words = word_tokenize(text.lower())
        syllables = sum(self.count_syllables(word) for word in words)

        return 0.39 * (len(words) / len(sentences)) + 11.8 * (syllables / len(words)) - 15.59

    def count_syllables(self, word: str) -> int:
        if word in self.pronouncing_dict:
            return len([ph for ph in self.pronouncing_dict[word][0] if ph[-1].isdigit()])
        return len(re.findall(r'[aeiou]', word, re.IGNORECASE)) + 1

    async def shorten_sentences(self, content: str) -> str:
        sentences = sent_tokenize(content)
        shortened_sentences = [self.shorten_sentence(sentence) for sentence in sentences]
        return ' '.join(shortened_sentences)

    def shorten_sentence(self, sentence: str) -> str:
        words = word_tokenize(sentence)
        if len(words) > 20:
            return ' '.join(words[:20]) + '.'
        return sentence

    async def lengthen_sentences(self, content: str) -> str:
        sentences = sent_tokenize(content)
        lengthened_sentences = [await self.lengthen_sentence(sentence) for sentence in sentences]
        return ' '.join(lengthened_sentences)

    async def lengthen_sentence(self, sentence: str) -> str:
        words = word_tokenize(sentence)
        if len(words) < 10:
            additional_words = await self.generate_additional_words(5)
            return f"{sentence[:-1]}, {' '.join(additional_words)}."
        return sentence

    async def generate_additional_words(self, num_words: int) -> List[str]:
        # This is a placeholder. In a real implementation, you might use an AI model to generate contextually relevant words.
        return ["additionally", "furthermore", "moreover", "specifically", "consequently"][:num_words]

    async def increase_vocabulary_diversity(self, content: str) -> str:
        words = word_tokenize(content.lower())
        word_freq = nltk.FreqDist(words)
        common_words = word_freq.most_common(10)

        for word, _ in common_words:
            synonym = await self.get_synonym(word)
            if synonym:
                content = content.replace(word, synonym, 1)

        return content

    async def get_synonym(self, word: str) -> str:
        synsets = nltk.corpus.wordnet.synsets(word)
        if synsets:
            lemmas = [lemma.name() for synset in synsets for lemma in synset.lemmas() if lemma.name() != word]
            return random.choice(lemmas) if lemmas else word
        return word

    async def simplify_vocabulary(self, content: str) -> str:
        words = word_tokenize(content)
        simplified_words = [await self.simplify_word(word) for word in words]
        return ' '.join(simplified_words)

    async def simplify_word(self, word: str) -> str:
        if len(word) > 8:
            synsets = nltk.corpus.wordnet.synsets(word)
            if synsets:
                simpler_words = [lemma.name() for synset in synsets for lemma in synset.lemmas() if len(lemma.name()) < len(word)]
                return random.choice(simpler_words) if simpler_words else word
        return word

    async def sophisticate_vocabulary(self, content: str) -> str:
        words = word_tokenize(content)
        sophisticated_words = [await self.sophisticate_word(word) for word in words]
        return ' '.join(sophisticated_words)

    async def sophisticate_word(self, word: str) -> str:
        if len(word) < 6:
            synsets = nltk.corpus.wordnet.synsets(word)
            if synsets:
                more_complex_words = [lemma.name() for synset in synsets for lemma in synset.lemmas() if len(lemma.name()) > len(word)]
                return random.choice(more_complex_words) if more_complex_words else word
        return word
