import re
import random
import logging

logger = logging.getLogger(__name__)

class PlagiarismAvoidance:
    @staticmethod
    def rephrase_content(content):
        # This is a simple example. In a real-world scenario, you'd want to use
        # more sophisticated NLP techniques or an AI model for rephrasing.
        sentences = re.split(r'(?<=[.!?])\s+', content)
        rephrased_sentences = []
        
        for sentence in sentences:
            if random.random() < 0.5:
                rephrased_sentences.append(PlagiarismAvoidance._rephrase_sentence(sentence))
            else:
                rephrased_sentences.append(sentence)
        
        return ' '.join(rephrased_sentences)

    @staticmethod
    def _rephrase_sentence(sentence):
        # This is a very basic rephrasing. In practice, you'd want to use more advanced techniques.
        words = sentence.split()
        if len(words) > 3:
            i = random.randint(0, len(words) - 3)
            words[i], words[i+1] = words[i+1], words[i]
        return ' '.join(words)

class CitationManager:
    def __init__(self):
        self.citations = []

    def add_citation(self, source, author, year):
        self.citations.append({
            'source': source,
            'author': author,
            'year': year
        })

    def generate_bibliography(self):
        bibliography = "References:\n\n"
        for citation in self.citations:
            bibliography += f"{citation['author']} ({citation['year']}). {citation['source']}\n"
        return bibliography

    def cite_in_text(self, index):
        citation = self.citations[index]
        return f"({citation['author']}, {citation['year']})"
