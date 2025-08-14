/**
 * VectorSimilarity.js
 * Utility functions for vector similarity calculations in Aideon AI Lite
 * Supports multiple similarity metrics for embedding comparisons
 */

class VectorSimilarity {
  /**
   * Calculate similarity between two vectors
   * @param {Array<number>} vector1 - First vector
   * @param {Array<number>} vector2 - Second vector
   * @param {string} metric - Similarity metric ('cosine', 'euclidean', 'dot', 'manhattan')
   * @returns {number} Similarity score
   */
  static calculateSimilarity(vector1, vector2, metric = 'cosine') {
    // Validate inputs
    if (!Array.isArray(vector1) || !Array.isArray(vector2)) {
      throw new Error('Vectors must be arrays');
    }
    
    if (vector1.length !== vector2.length) {
      throw new Error('Vectors must have the same dimension');
    }
    
    if (vector1.length === 0) {
      throw new Error('Vectors cannot be empty');
    }
    
    switch (metric.toLowerCase()) {
      case 'cosine':
        return this.cosineSimilarity(vector1, vector2);
      case 'euclidean':
        return this.euclideanSimilarity(vector1, vector2);
      case 'dot':
        return this.dotProduct(vector1, vector2);
      case 'manhattan':
        return this.manhattanSimilarity(vector1, vector2);
      default:
        throw new Error(`Unsupported similarity metric: ${metric}`);
    }
  }
  
  /**
   * Calculate cosine similarity between two vectors
   * @param {Array<number>} vector1 - First vector
   * @param {Array<number>} vector2 - Second vector
   * @returns {number} Cosine similarity (0 to 1)
   */
  static cosineSimilarity(vector1, vector2) {
    const dotProduct = this.dotProduct(vector1, vector2);
    const magnitude1 = this.magnitude(vector1);
    const magnitude2 = this.magnitude(vector2);
    
    if (magnitude1 === 0 || magnitude2 === 0) {
      return 0;
    }
    
    return dotProduct / (magnitude1 * magnitude2);
  }
  
  /**
   * Calculate Euclidean similarity between two vectors
   * @param {Array<number>} vector1 - First vector
   * @param {Array<number>} vector2 - Second vector
   * @returns {number} Euclidean similarity (0 to 1)
   */
  static euclideanSimilarity(vector1, vector2) {
    const distance = this.euclideanDistance(vector1, vector2);
    // Convert distance to similarity (closer to 0 = more similar)
    return 1 / (1 + distance);
  }
  
  /**
   * Calculate Manhattan similarity between two vectors
   * @param {Array<number>} vector1 - First vector
   * @param {Array<number>} vector2 - Second vector
   * @returns {number} Manhattan similarity (0 to 1)
   */
  static manhattanSimilarity(vector1, vector2) {
    const distance = this.manhattanDistance(vector1, vector2);
    // Convert distance to similarity (closer to 0 = more similar)
    return 1 / (1 + distance);
  }
  
  /**
   * Calculate dot product of two vectors
   * @param {Array<number>} vector1 - First vector
   * @param {Array<number>} vector2 - Second vector
   * @returns {number} Dot product
   */
  static dotProduct(vector1, vector2) {
    let sum = 0;
    for (let i = 0; i < vector1.length; i++) {
      sum += vector1[i] * vector2[i];
    }
    return sum;
  }
  
  /**
   * Calculate Euclidean distance between two vectors
   * @param {Array<number>} vector1 - First vector
   * @param {Array<number>} vector2 - Second vector
   * @returns {number} Euclidean distance
   */
  static euclideanDistance(vector1, vector2) {
    let sum = 0;
    for (let i = 0; i < vector1.length; i++) {
      const diff = vector1[i] - vector2[i];
      sum += diff * diff;
    }
    return Math.sqrt(sum);
  }
  
  /**
   * Calculate Manhattan distance between two vectors
   * @param {Array<number>} vector1 - First vector
   * @param {Array<number>} vector2 - Second vector
   * @returns {number} Manhattan distance
   */
  static manhattanDistance(vector1, vector2) {
    let sum = 0;
    for (let i = 0; i < vector1.length; i++) {
      sum += Math.abs(vector1[i] - vector2[i]);
    }
    return sum;
  }
  
  /**
   * Calculate magnitude (L2 norm) of a vector
   * @param {Array<number>} vector - Vector
   * @returns {number} Vector magnitude
   */
  static magnitude(vector) {
    let sum = 0;
    for (let i = 0; i < vector.length; i++) {
      sum += vector[i] * vector[i];
    }
    return Math.sqrt(sum);
  }
  
  /**
   * Normalize vector to unit length
   * @param {Array<number>} vector - Vector to normalize
   * @returns {Array<number>} Normalized vector
   */
  static normalize(vector) {
    const mag = this.magnitude(vector);
    if (mag === 0) {
      return vector.slice(); // Return copy of zero vector
    }
    return vector.map(val => val / mag);
  }
  
  /**
   * Find top K most similar vectors
   * @param {Array<number>} queryVector - Query vector
   * @param {Array<{id: string, vector: Array<number>}>} vectors - Vectors to search
   * @param {number} k - Number of top results to return
   * @param {string} metric - Similarity metric
   * @returns {Array<{id: string, score: number}>} Top K similar vectors
   */
  static findTopK(queryVector, vectors, k = 10, metric = 'cosine') {
    const similarities = vectors.map(item => ({
      id: item.id,
      score: this.calculateSimilarity(queryVector, item.vector, metric)
    }));
    
    // Sort by similarity score (descending)
    similarities.sort((a, b) => b.score - a.score);
    
    return similarities.slice(0, k);
  }
  
  /**
   * Calculate pairwise similarities between all vectors in a set
   * @param {Array<Array<number>>} vectors - Array of vectors
   * @param {string} metric - Similarity metric
   * @returns {Array<Array<number>>} Similarity matrix
   */
  static pairwiseSimilarities(vectors, metric = 'cosine') {
    const n = vectors.length;
    const similarities = Array(n).fill(null).map(() => Array(n).fill(0));
    
    for (let i = 0; i < n; i++) {
      for (let j = i; j < n; j++) {
        if (i === j) {
          similarities[i][j] = 1.0; // Self-similarity is 1
        } else {
          const sim = this.calculateSimilarity(vectors[i], vectors[j], metric);
          similarities[i][j] = sim;
          similarities[j][i] = sim; // Symmetric
        }
      }
    }
    
    return similarities;
  }
  
  /**
   * Calculate centroid of a set of vectors
   * @param {Array<Array<number>>} vectors - Array of vectors
   * @returns {Array<number>} Centroid vector
   */
  static centroid(vectors) {
    if (vectors.length === 0) {
      throw new Error('Cannot calculate centroid of empty vector set');
    }
    
    const dimension = vectors[0].length;
    const centroid = new Array(dimension).fill(0);
    
    for (const vector of vectors) {
      if (vector.length !== dimension) {
        throw new Error('All vectors must have the same dimension');
      }
      
      for (let i = 0; i < dimension; i++) {
        centroid[i] += vector[i];
      }
    }
    
    // Average
    for (let i = 0; i < dimension; i++) {
      centroid[i] /= vectors.length;
    }
    
    return centroid;
  }
  
  /**
   * Calculate variance of a set of vectors
   * @param {Array<Array<number>>} vectors - Array of vectors
   * @returns {number} Variance
   */
  static variance(vectors) {
    if (vectors.length === 0) {
      return 0;
    }
    
    const centroidVector = this.centroid(vectors);
    let totalVariance = 0;
    
    for (const vector of vectors) {
      const distance = this.euclideanDistance(vector, centroidVector);
      totalVariance += distance * distance;
    }
    
    return totalVariance / vectors.length;
  }
}

module.exports = VectorSimilarity;
