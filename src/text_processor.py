"""
VoiceTracer Text Processing Engine

Handles text preprocessing, sentence/token extraction, and analysis preparation.
"""

import re
from typing import List, Tuple, Dict, Optional
import string
from collections import Counter


class TextProcessor:
    """Processes raw text for analysis."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Uses regex-based sentence splitting followed by rule-based refinement.
        Handles common abbreviations (Dr., Mr., etc.) and decimal numbers.
        """
        if not text:
            return []
        
        # Basic sentence splitting on .!?
        # But keep decimals intact
        sentences = re.split(r'(?<![0-9])\.(?![0-9])|[!?]+', text)
        
        # Filter empty and very short sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Remove sentences that are just numbers or punctuation
        sentences = [s for s in sentences if len(s.split()) >= 2]
        
        return sentences
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Simple word tokenization.
        Splits on whitespace and preserves punctuation.
        """
        return text.split()
    
    @staticmethod
    def get_word_tokens(text: str) -> List[str]:
        """
        Extract only word tokens (no punctuation).
        Lowercase and removes pure punctuation tokens.
        """
        tokens = TextProcessor.tokenize(text)
        words = []
        for token in tokens:
            # Remove punctuation from token
            word = token.strip(string.punctuation).lower()
            if word and not all(c in string.punctuation for c in word):
                words.append(word)
        return words
    
    @staticmethod
    def extract_clauses(sentence: str) -> List[str]:
        """
        Extract clauses from a sentence.
        Splits on coordinating and subordinating conjunctions.
        """
        # Common subordinators: because, which, that, when, where, if, since, although, etc.
        clause_markers = r'\b(because|which|that|when|where|if|since|although|unless|while|before|after|as|whereas|so that)\b'
        
        clauses = re.split(clause_markers, sentence, flags=re.IGNORECASE)
        # Keep non-empty, non-conjunction parts
        clauses = [c.strip() for c in clauses if c.strip() and not re.match(clause_markers, c, re.IGNORECASE)]
        
        return clauses if clauses else [sentence]
    
    @staticmethod
    def extract_n_grams(tokens: List[str], n: int) -> Dict[Tuple[str, ...], int]:
        """
        Extract n-grams (sequences of n tokens).
        
        Args:
            tokens: List of tokens
            n: Size of n-gram
        
        Returns:
            Dict mapping n-gram tuples to occurrence counts
        """
        n_grams = Counter()
        for i in range(len(tokens) - n + 1):
            n_gram = tuple(tokens[i:i+n])
            n_grams[n_gram] += 1
        return dict(n_grams)
    
    @staticmethod
    def get_passive_voice_ratio(text: str) -> float:
        """
        Estimate passive voice usage.
        Looks for 'to be' + past participle patterns.
        Returns ratio 0-1.
        """
        if not text:
            return 0.0
        
        # Passive voice patterns
        be_forms = r'\b(is|are|was|were|be|been|being)\s+\w+ed\b'
        matches = len(re.findall(be_forms, text, re.IGNORECASE))
        
        sentences = TextProcessor.extract_sentences(text)
        if not sentences:
            return 0.0
        
        return min(matches / len(sentences), 1.0)


class StatisticsCalculator:
    """Calculates statistical properties of text."""
    
    @staticmethod
    def calculate_sentence_lengths(sentences: List[str]) -> List[int]:
        """Calculate word count for each sentence."""
        return [len(TextProcessor.tokenize(s)) for s in sentences]
    
    @staticmethod
    def mean_sentence_length(sentences: List[str]) -> float:
        """Calculate mean sentence length."""
        if not sentences:
            return 0.0
        lengths = StatisticsCalculator.calculate_sentence_lengths(sentences)
        return sum(lengths) / len(lengths)
    
    @staticmethod
    def std_dev_sentence_length(sentences: List[str]) -> float:
        """Calculate standard deviation of sentence lengths."""
        if not sentences or len(sentences) < 2:
            return 0.0
        
        lengths = StatisticsCalculator.calculate_sentence_lengths(sentences)
        mean = sum(lengths) / len(lengths)
        
        variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
        return variance ** 0.5
    
    @staticmethod
    def type_token_ratio(words: List[str]) -> float:
        """
        Calculate Type-Token Ratio (unique words / total words).
        Returns value 0-1.
        """
        if not words:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        return unique_words / total_words if total_words > 0 else 0.0
    
    @staticmethod
    def mtld(words: List[str], threshold: float = 0.72) -> float:
        """
        Calculate MTLD (Mean Type-Token Ratio Dynamics).
        
        More robust to text length than TTR.
        MTLD segments the text and averages TTR across segments.
        
        Args:
            words: List of word tokens
            threshold: TTR threshold for segmentation (default 0.72)
        
        Returns:
            MTLD value (typically 70-150)
        """
        if not words or len(words) < 10:
            # For very short texts, use TTR
            return StatisticsCalculator.type_token_ratio(words) * 100
        
        # Forward pass
        segments = 0
        token_count = 0
        type_count = 0
        types = set()
        
        for word in words:
            token_count += 1
            types.add(word)
            type_count = len(types)
            
            ttr = type_count / token_count if token_count > 0 else 0
            
            if ttr <= threshold:
                segments += 1
                types = set()
                token_count = 0
                type_count = 0
        
        # Backward pass (to capture final segment)
        types = set()
        token_count = 0
        for word in reversed(words):
            token_count += 1
            types.add(word)
            type_count = len(types)
            
            ttr = type_count / token_count if token_count > 0 else 0
            
            if ttr <= threshold:
                segments += 1
                types = set()
                token_count = 0
                type_count = 0
        
        if segments == 0:
            segments = 1
        
        mtld_value = len(words) / segments
        return mtld_value
    
    @staticmethod
    def subordination_ratio(sentence: str) -> float:
        """
        Calculate subordination ratio for a sentence.
        
        Returns: subordinate clauses / total clauses (0-1)
        """
        # Extract all clauses
        clauses = TextProcessor.extract_clauses(sentence)
        if not clauses:
            return 0.0
        
        # Count subordinate clauses (heuristic: contains subordinators)
        subordinators = r'\b(because|which|that|when|where|if|since|although|unless|while|before|after|as|whereas|so that)\b'
        subordinate = sum(1 for c in clauses if re.search(subordinators, c, re.IGNORECASE))
        
        return subordinate / len(clauses) if clauses else 0.0
    
    @staticmethod
    def modifier_density(text: str) -> float:
        """
        Calculate modifier density.
        Returns: count of adjectives/adverbs / total words (0-1)
        """
        if not text:
            return 0.0
        
        # Simple heuristic: words ending in -ly (adverbs) and common adjectives
        words = TextProcessor.get_word_tokens(text)
        
        # Count adverbs (simple heuristic: ends in -ly)
        adverbs = sum(1 for w in words if w.endswith('ly'))
        
        # Count common adjective patterns (this is a simplification)
        # More sophisticated would need POS tagging
        total_words = len(words)
        
        modifier_count = adverbs
        return modifier_count / total_words if total_words > 0 else 0.0


class TextAnalysisPreprocessor:
    """Preprocesses text and extracts features for metric calculation."""
    
    def __init__(self, text: str):
        self.raw_text = text
        self.clean_text = TextProcessor.clean_text(text)
        self.sentences = TextProcessor.extract_sentences(self.clean_text)
        self.tokens = TextProcessor.tokenize(self.clean_text)
        self.words = TextProcessor.get_word_tokens(self.clean_text)
    
    def get_metadata(self) -> Dict:
        """Extract text metadata."""
        return {
            'word_count': len(self.words),
            'char_count': len(self.raw_text),
            'sentence_count': len(self.sentences),
            'token_count': len(self.tokens),
            'avg_sentence_length': (
                StatisticsCalculator.mean_sentence_length(self.sentences)
                if self.sentences else 0.0
            ),
        }
    
    def get_analysis_features(self) -> Dict:
        """Extract all features needed for metric calculation."""
        return {
            'sentences': self.sentences,
            'words': self.words,
            'tokens': self.tokens,
            'sentence_lengths': StatisticsCalculator.calculate_sentence_lengths(self.sentences),
            'bigrams': TextProcessor.extract_n_grams(self.words, 2),
            'trigrams': TextProcessor.extract_n_grams(self.words, 3),
            'passive_voice_ratio': TextProcessor.get_passive_voice_ratio(self.clean_text),
        }
