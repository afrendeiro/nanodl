import jax
import jax.numpy as jnp
from jax import random, ops
from typing import Optional

class KMeans:
    """
    KMeans clustering algorithm using JAX for efficient computation.
    """
    def __init__(self, k, epochs=1):
        """
        Initialize the KMeans object.

        Args:
            k (int): Number of clusters.
            epochs (int): Number of training epochs. Default is 1.
        """
        self.k = k
        self.epochs = epochs

    def fit(self, data):
        """
        Fit the KMeans model to the given data.

        Args:
            data (list or array): Input data for clustering.

        Returns:
            tuple: A tuple containing the data and assigned cluster labels.
        """
        data = jnp.array(data)
        centroids = jnp.array([random.choice(data) for _ in range(self.k)])
        labels = jnp.zeros(data.shape[0], dtype=jnp.int32)

        for _ in range(self.epochs):
            labels = self.train_step(data, centroids)
            centroids = self.set_centroids(data, labels)

        return data, labels

    @staticmethod
    @jax.jit
    def train_step(data, centroids):
        """
        Perform a single training step of the KMeans algorithm.

        Args:
            data (array): Input data.
            centroids (array): Current cluster centroids.

        Returns:
            array: Cluster labels for each data point.
        """
        distances = jnp.linalg.norm(data[:, None, :] - centroids, axis=2)
        labels = jnp.argmin(distances, axis=1)
        return labels

    @staticmethod
    def set_centroids(data, labels):
        """
        Update cluster centroids based on data and labels.

        Args:
            data (array): Input data.
            labels (array): Cluster labels for each data point.

        Returns:
            array: Updated cluster centroids.
        """
        centroids = jnp.zeros((labels.max() + 1, data.shape[1]))
        counts = jnp.bincount(labels)

        for label in range(centroids.shape[0]):
            if counts[label] == 0:
                continue
            cluster_data = data[labels == label]
            mean = jnp.mean(cluster_data, axis=0)
            centroids = centroids.at[label].set(mean)

        return centroids
    

class GaussianMixtureModel:
    """
    Gaussian Mixture Model using the Expectation-Maximization algorithm in JAX.

    Attributes:
        n_components (int): Number of Gaussian components.
        n_features (int): Number of features in the data.
        max_iter (int): Maximum number of iterations for EM algorithm.
        tol (float): Convergence tolerance.
        weights (jnp.ndarray): Component weights.
        means (jnp.ndarray): Component means.
        covariances (jnp.ndarray): Component covariances.

    Example Usage:
        # Create an instance of the GaussianMixtureModel class
        gmm = GaussianMixtureModel(n_components=3, n_features=2)

        # Generate synthetic data (e.g., using jax.random.multivariate_normal)
        key = jax.random.PRNGKey(0)
        data = jax.random.multivariate_normal(key, mean=jnp.array([0, 0]), cov=jnp.eye(2), shape=(100,))

        # Fit the model on the dataset
        gmm.fit(data)

        # The model is now trained with the means, covariances, and weights of each component
    """

    def __init__(self, 
                 n_components: int, 
                 n_features: int, 
                 max_iter: int = 100, 
                 tol: float = 1e-4):
        """
        Initialize a Gaussian Mixture Model.

        Args:
            n_components (int): Number of Gaussian components.
            n_features (int): Number of features in the data.
            max_iter (int): Maximum number of iterations for EM algorithm.
            tol (float): Convergence tolerance.
        """
        self.n_components = n_components
        self.n_features = n_features
        self.max_iter = max_iter
        self.tol = tol

        key = random.PRNGKey(0)
        self.weights = jnp.ones(n_components) / n_components
        self.means = random.normal(key, (n_components, n_features))
        self.covariances = jnp.array([jnp.eye(n_features) for _ in range(n_components)])

    def fit(self, X: jnp.ndarray) -> None:
        """
        Fit the Gaussian Mixture Model to the data using Expectation-Maximization.

        Args:
            X (jnp.ndarray): Input data with shape (n_samples, n_features).
        """
        for _ in range(self.max_iter):
            prev_log_likelihood = self.log_likelihood(X)

            # Expectation step
            responsibilities = self.expectation(X)

            # Maximization step
            self.weights = responsibilities.sum(axis=0) / X.shape[0]
            self.means = jnp.dot(responsibilities.T, X) / responsibilities.sum(axis=0)[:, jnp.newaxis]
            for k in range(self.n_components):
                diff = X - self.means[k]
                self.covariances = ops.index_update(
                    self.covariances, ops.index[k], 
                    jnp.dot(responsibilities[:, k] * diff.T, diff) / responsibilities[:, k].sum()
                )

            current_log_likelihood = self.log_likelihood(X)

            if jnp.abs(current_log_likelihood - prev_log_likelihood) < self.tol:
                break

    def expectation(self, 
                    X: jnp.ndarray) -> jnp.ndarray:
        """
        Perform the Expectation step of the EM algorithm.

        Args:
            X (jnp.ndarray): Input data with shape (n_samples, n_features).

        Returns:
            jnp.ndarray: Responsibilities of data points for each component.
        """
        responsibilities = jnp.zeros((X.shape[0], self.n_components))
        for k in range(self.n_components):
            responsibilities = ops.index_add(
                responsibilities, ops.index[:, k], 
                self.weights[k] * self.pdf(X, self.means[k], self.covariances[k])
            )
        responsibilities /= responsibilities.sum(axis=1, keepdims=True)
        return responsibilities

    def pdf(self, 
            X: jnp.ndarray, 
            mean: jnp.ndarray, 
            cov: jnp.ndarray) -> jnp.ndarray:
        """
        Compute the probability density function of data points for a Gaussian component.

        Args:
            X (jnp.ndarray): Input data with shape (n_samples, n_features).
            mean (jnp.ndarray): Mean of the Gaussian component.
            cov (jnp.ndarray): Covariance of the Gaussian component.

        Returns:
            jnp.ndarray: PDF values for each data point.
        """
        d = X.shape[1]
        norm_factor = jnp.sqrt((2 * jnp.pi)**d * jnp.linalg.det(cov))
        exponent = -0.5 * jnp.sum(jnp.dot((X - mean), jnp.linalg.inv(cov)) * (X - mean), axis=1)
        return jnp.exp(exponent) / norm_factor

    def log_likelihood(self, 
                       X: jnp.ndarray) -> float:
        """
        Compute the log-likelihood of the data given the model parameters.

        Args:
            X (jnp.ndarray): Input data with shape (n_samples, n_features).

        Returns:
            float: Log-likelihood of the data.
        """
        likelihoods = jnp.zeros((X.shape[0], self.n_components))
        for k in range(self.n_components):
            likelihoods = ops.index_add(
                likelihoods, ops.index[:, k], 
                self.weights[k] * self.pdf(X, self.means[k], self.covariances[k])
            )
        return jnp.sum(jnp.log(jnp.sum(likelihoods, axis=1)))