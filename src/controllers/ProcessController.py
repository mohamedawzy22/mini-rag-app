from .BaseController import BaseController
from .ProjectController import ProjectController

import os
import logging
from statistics import mean, median
from typing import List

from langchain_community.document_loaders import (
    TextLoader,
    PyMuPDFLoader,
)

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models import ProcessingEnum


logger = logging.getLogger("uvicorn.error")


class ProcessController(BaseController):

    def __init__(self, project_id: str):

        super().__init__()

        self.project_id = project_id

        self.project_path = ProjectController().get_project_path(
            project_id=project_id
        )

    # =========================================================
    # FILE HANDLING
    # =========================================================

    def get_file_extension(self, file_id: str) -> str:

        return os.path.splitext(file_id)[-1].lower()

    def get_file_loader(self, file_id: str):

        file_ext = self.get_file_extension(
            file_id=file_id
        )

        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if not os.path.exists(file_path):

            logger.error(
                "File not found | file_id=%s | path=%s",
                file_id,
                file_path,
            )

            return None

        if file_ext == ProcessingEnum.TXT.value:

            return TextLoader(
                file_path,
                encoding="utf-8",
            )

        if file_ext == ProcessingEnum.PDF.value:

            return PyMuPDFLoader(file_path)

        logger.error(
            "Unsupported file extension | file_id=%s | extension=%s",
            file_id,
            file_ext,
        )

        return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(
            file_id=file_id
        )

        if loader is None:
            return None

        try:

            documents = loader.load()

            logger.info(
                "Document loaded | file_id=%s | documents=%d",
                file_id,
                len(documents),
            )

            return documents

        except Exception:

            logger.exception(
                "Failed to load document | file_id=%s",
                file_id,
            )

            return None

    # =========================================================
    # CHUNKING
    # =========================================================

    def process_file_content(
        self,
        file_content: List[Document],
        file_id: str,
        chunk_size: int = 500,
        overlap_size: int = 50,
    ) -> List[Document]:

        logger.info(
            "Starting document chunking | "
            "file_id=%s | documents=%d | chunk_size=%d | overlap=%d",
            file_id,
            len(file_content),
            chunk_size,
            overlap_size,
        )

        # -----------------------------------------------------
        # Validate configuration
        # -----------------------------------------------------

        self._validate_chunk_config(
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        # -----------------------------------------------------
        # Create splitter
        # -----------------------------------------------------

        splitter = self._create_splitter(
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        # -----------------------------------------------------
        # Split documents
        # -----------------------------------------------------

        try:

            chunks = splitter.split_documents(
                file_content
            )

        except Exception:

            logger.exception(
                "Chunking failed | file_id=%s",
                file_id,
            )

            raise

        # -----------------------------------------------------
        # Add useful metadata
        # -----------------------------------------------------

        chunks = self._enrich_chunk_metadata(
            chunks=chunks,
            file_id=file_id,
        )

        # -----------------------------------------------------
        # Log statistics
        # -----------------------------------------------------

        self._log_chunk_statistics(
            chunks=chunks,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        return chunks

    # =========================================================
    # CHUNKER CONFIGURATION
    # =========================================================

    @staticmethod
    def _create_splitter(
        chunk_size: int,
        overlap_size: int,
    ) -> RecursiveCharacterTextSplitter:

        """
        Hierarchical chunking strategy.

        Priority:

        1. Paragraph
        2. New line
        3. Sentence
        4. Phrase
        5. Word
        6. Character
        """

        return RecursiveCharacterTextSplitter(

            chunk_size=chunk_size,

            chunk_overlap=overlap_size,

            length_function=len,

            keep_separator=True,

            strip_whitespace=True,

            separators=[
                # -----------------------------
                # Paragraph
                # -----------------------------
                "\n\n",

                # -----------------------------
                # New line
                # -----------------------------
                "\n",

                # -----------------------------
                # Arabic sentence endings
                # -----------------------------
                "؟ ",
                "! ",
                "؛ ",

                # -----------------------------
                # English sentence endings
                # -----------------------------
                ". ",

                # -----------------------------
                # Arabic punctuation
                # -----------------------------
                "؟",
                "؛",

                # -----------------------------
                # English punctuation
                # -----------------------------
                "!",
                ".",

                # -----------------------------
                # Commas
                # -----------------------------
                "، ",
                ", ",

                # -----------------------------
                # Word boundary
                # -----------------------------
                " ",

                # -----------------------------
                # Last resort
                # -----------------------------
                "",
            ],
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_chunk_config(
        chunk_size: int,
        overlap_size: int,
    ):

        if chunk_size <= 0:

            raise ValueError(
                "chunk_size must be greater than zero"
            )

        if overlap_size < 0:

            raise ValueError(
                "overlap_size cannot be negative"
            )

        if overlap_size >= chunk_size:

            raise ValueError(
                "overlap_size must be smaller than chunk_size"
            )

    # =========================================================
    # METADATA
    # =========================================================

    @staticmethod
    def _enrich_chunk_metadata(
        chunks: List[Document],
        file_id: str,
    ) -> List[Document]:

        for index, chunk in enumerate(chunks):

            chunk.metadata = {
                **chunk.metadata,

                "file_id": file_id,

                "chunk_index": index,

                "chunk_size": len(
                    chunk.page_content
                ),
            }

        return chunks

    # =========================================================
    # LOGGING / OBSERVABILITY
    # =========================================================

    @staticmethod
    def _log_chunk_statistics(
        chunks: List[Document],
        file_id: str,
        chunk_size: int,
        overlap_size: int,
    ):

        if not chunks:

            logger.warning(
                "Chunking produced no chunks | file_id=%s",
                file_id,
            )

            return

        lengths = [
            len(chunk.page_content)
            for chunk in chunks
        ]

        oversized_chunks = [
            length
            for length in lengths
            if length > chunk_size
        ]

        logger.info(
            "Chunking completed | "
            "file_id=%s | "
            "chunks=%d | "
            "min=%d | "
            "max=%d | "
            "avg=%.2f | "
            "median=%.2f | "
            "configured_size=%d | "
            "overlap=%d",
            file_id,
            len(chunks),
            min(lengths),
            max(lengths),
            mean(lengths),
            median(lengths),
            chunk_size,
            overlap_size,
        )

        if oversized_chunks:

            logger.warning(
                "Oversized chunks detected | "
                "file_id=%s | "
                "count=%d | "
                "max_size=%d",
                file_id,
                len(oversized_chunks),
                max(oversized_chunks),
            )

        # -----------------------------------------------------
        # Debug-level detailed inspection
        # -----------------------------------------------------

        logger.debug(
            "Chunk size distribution | "
            "file_id=%s | first_10=%s",
            file_id,
            lengths[:10],
        )

        for index, chunk in enumerate(chunks[:3]):

            preview = (
                chunk.page_content
                .replace("\n", " ")
                [:250]
            )

            logger.debug(
                "Chunk preview | "
                "file_id=%s | "
                "index=%d | "
                "size=%d | "
                "preview=%s",
                file_id,
                index,
                len(chunk.page_content),
                preview,
            )