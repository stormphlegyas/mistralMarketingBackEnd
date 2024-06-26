# -*- coding: utf-8 -*-

import logging
import numpy as np
import os
import polars as pl

import scipy.spatial.distance as distance

from dotenv import load_dotenv
from mistralai.client import MistralClient
from sklearn.metrics.pairwise import euclidean_distances

from typing import Tuple

logging.basicConfig(level=logging.INFO)

load_dotenv()

class SimilaritySearch:
    def __init__(self, model:str, index_name:str=None):
        """
        Initializes an SimilaritySearch object to manage associations between embedding models and index names.

        Parameters
        ----------
        model : str
            Name or identifier of the embedding model being used.

        index_name : str, optional
            Name of the index associated with the embedding model.

        Notes
        -----
        The `Embeddings` class serves as a handler for managing and associating embedding models 
        with their respective index names. It is primarily utilized to handle embeddings 
        retrieval or utilization within the specified index for various operations.
        """
        self.model = model
        self.index_name = index_name
        self.vectorstore = None
        self.api_key = os.environ.get("MISTRAL_API_KEY")
        self.client = MistralClient(
            api_key=self.api_key
        )
    
    def encode(self, data: str) -> np.ndarray:
        """
        Encodes a list of sentences into their corresponding embeddings using a specified SentenceTransformer model.

        Parameters
        ----------
        data : str
            String to be encoded.

        Returns
        -------
        embeddings : np.ndarray
            Embeddings of the sentences.

        Notes
        -----
        This method utilizes the SentenceTransformer model specified during object initialization to generate embeddings
        for the provided list of sentences. It encodes the sentences into numerical representations, returning the embeddings
        as a NumPy array.

        Raises
        ------
        Exception
            If there's an issue with the SentenceTransformer model or the encoding process.
        """
        try:
            embeddings_batch_response = self.client.embeddings(
                model=self.model,
                input=data,
            )

            logging.info("Embeddings have been successfully generated...")

            return embeddings_batch_response.data[0].embedding

        except Exception as e:
            logging.error(f"Error occurred during encoding: {e}")


    @staticmethod
    def cosine(embeddings:list[np.ndarray], target:np.ndarray):
        """
        Calculates the index of the array within `embeddings` containing the matrix with the highest similarity score to `target`.

        Parameters
        ----------
        embeddings : list[np.ndarray]
            List of arrays, each containing matrices.

        target : np.ndarray
            The matrix for comparison.

        Returns
        -------
        max_array_index : int
            Index of the array within `embeddings` containing the matrix with the highest similarity score to `target`.
        """
        # Input validation
        if not isinstance(embeddings, list) or not all(isinstance(arr, np.ndarray) for arr in embeddings):
            raise ValueError("embeddings should be a list of numpy arrays.")
        
        if not isinstance(target, np.ndarray):
            raise ValueError("target should be a numpy array.")

        if not embeddings or any(not arr.size for arr in embeddings):
            raise ValueError("The input embeddings list cannot be empty or contain empty arrays.")

        max_similarity = -1
        max_array_index = -1

        try:
            for idx, array_of_matrices in enumerate(embeddings):
                for matrix in array_of_matrices:
                    similarity_score = 1 - distance.cosine(target.flatten(), matrix.flatten())
                    if similarity_score > max_similarity:
                        max_similarity = similarity_score
                        max_array_index = idx

        except ValueError as e:
            raise ValueError(f"An error occurred during computation: {e}")

        return max_array_index

    
    def calculate_distances(
        self,
        sentences:list, 
        embeddings:list, 
        reference_embedding
    ):
        """
        Calculate Euclidean distances between each embedding in 'embeddings' and 'reference_embedding'
        and print the distances along with their corresponding sentences.

        Parameters
        ----------
        sentences : list of str
            List of sentences corresponding to the embeddings.

        embeddings : list of arrays
            List of embeddings.

        reference_embedding : array
            The reference embedding to calculate distances from.

        Returns
        -------
        None
            Prints each sentence along with its corresponding distance to the reference_embedding.

        Notes
        -----
        This function calculates the Euclidean distances between each embedding in 'embeddings' and the
        'reference_embedding'. It prints each sentence along with its corresponding distance.
        """
        # Initialize empty lists to store sentences and distances
        sentences_list = []
        distances_list = []
        
        for t, e in zip(sentences, embeddings):
            distance = euclidean_distances([e], [reference_embedding])[0][0]
            sentences_list.append(t)
            distances_list.append(distance)

        data = {
            "sentence": sentences_list, 
            "distance": distances_lis
        }

        df = pl.DataFrame(data)


    def index(self, embeddings:np.ndarray, save:bool=False) -> any:
        """
        Creates an index for the embeddings using the FAISS library, trains the index, and saves it to a file.
        
        Returns
        -------
        embeddings : np.ndarray
            Embeddings of the sentences.

        save : bool, optional
            Bool indicating if the index will be saved. Default is False.

        Notes
        -----
        This method employs the FAISS library to create and train an index using the embeddings previously generated. 
        It constructs an index with a specified configuration, trains it with the embeddings data, and saves the 
        resulting index to a file named after the specified index name.

        Raises
        ------
        Exception
            If there's an issue with creating or training the FAISS index or while saving it to the file.
        """
        dimension = embeddings.shape[1]

        # Create and configure the FAISS index
        if not self.vectorstore:
            self.vectorstore = faiss.index_factory(dimension, "IVF82_HNSW56,Flat")

        try:
            self.vectorstore.add(embeddings)

            if save:
                faiss.write_index(self.vectorstore, self.index_name + ".index")
                logging.info("Vectorstore has been successfully saved...")

            return self.vectorstore

        except Exception as e:
            logging.error(f"Error occurred during index creation and saving: {e}")

            raise Exception("Index creation or saving failed. Check the FAISS index configuration or embeddings data.")


    def load_vectorstore(self) -> any:
        """
        Loads a FAISS index from a file.

        Returns
        -------
        index or None
            FAISS index if the file exists, else None.

        Notes
        -----
        This method attempts to load a pre-existing FAISS index from a file. It checks for the presence of a file 
        corresponding to the specified index name. If the file exists, it reads the index from the file and returns 
        it; otherwise, it returns None.

        Raises
        ------
        Exception
            If there's an issue while loading the FAISS index from the file.
        """
        if os.path.exists(self.index_name + ".index"):
            try:
                # Load the FAISS index from the file
                self.vectorstore = faiss.read_index(self.index_name + ".index")

                return self.vectorstore

            except Exception as e:
                logging.error(f"Error occurred while loading the FAISS index: {e}")

                raise Exception("Failed to load the FAISS index from the file.")
        else:
            return None


    def search(self, target: np.ndarray, k:int=5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Searches for the nearest neighbors in the index for a given prompt.

        Parameters
        ----------
        target : np.ndarray
            Target to be searched for.

        k : int, optional
            Number of nearest neighbors to be returned. Defaults to 5.
        
        Returns
        -------
        neighbours : np.ndarray
            Indices of the nearest neighbors.
        
        distances : np.ndarray
            Distances to the nearest neighbors.

        Notes
        -----
        This method performs a search within the indexed embeddings to find the k nearest neighbors to the provided target.
        It encodes the target into embeddings using the specified model, then searches the index using the FAISS library.
        The resulting arrays contain the indices of the nearest neighbors and their respective distances.

        Raises
        ------
        Exception
            If there's an issue with encoding the target, performing the search, or retrieving the nearest neighbors.
        """
        try:
            # Encode the target into embeddings
            v = np.array([self.encode(
                data=target, 
                model=self.model
            )])

            # Configure the number of probes for the search
            self.vectorstore.nprobe = 512

            # Perform the search in the indexed embeddings
            distances, neighbours = self.vectorstore.search(
                v, 
                k=k
            )

            return neighbours[0], distances

        except Exception as e:
            logging.error(f"Error occurred during search: {e}")

            raise Exception("Search for nearest neighbors failed. Check the target data or index.")
