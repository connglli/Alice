"""Base class for memory providers."""
import abc
from config import AbstractSingleton
import sentence_transformers


FLAX_EMBED_MODEL = sentence_transformers.SentenceTransformer("flax-sentence-embeddings/all_datasets_v4_MiniLM-L6")
FLAX_EMBED_DIM = 384


def get_flax_embedding(text):
    text = text.replace("\n", " ")
    return FLAX_EMBED_MODEL.encode(text, show_progress_bar=False)


class MemoryProviderSingleton(AbstractSingleton):
    @abc.abstractmethod
    def add(self, data):
        pass

    @abc.abstractmethod
    def get(self, data):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def get_relevant(self, data, num_relevant=5):
        pass

    @abc.abstractmethod
    def get_stats(self):
        pass
