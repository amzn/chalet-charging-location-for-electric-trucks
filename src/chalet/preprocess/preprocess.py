"""Preprocessing module."""

import logging
from abc import ABC, ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class PreprocessData(ABC, metaclass=ABCMeta):
    """Generic preprocess class."""

    @abstractmethod
    def preprocess(self, data: dict):
        """Preprocess data for running algorithm."""
