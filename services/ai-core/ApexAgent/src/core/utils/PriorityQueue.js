/**
 * PriorityQueue.js
 * 
 * A priority queue implementation for Aideon AI Lite.
 * Provides efficient task prioritization and scheduling capabilities.
 * 
 * @author Aideon AI Team
 * @version 1.0.0
 */

class PriorityQueue {
  /**
   * Create a new priority queue
   * @param {Function} comparator - Function to compare elements (a, b) => number
   *                               Should return negative if a has higher priority than b,
   *                               positive if b has higher priority than a,
   *                               or 0 if they have equal priority
   */
  constructor(comparator = (a, b) => a.priority - b.priority) {
    this.comparator = comparator;
    this.heap = [];
    this.size = 0;
  }

  /**
   * Get the number of elements in the queue
   * @returns {number} Number of elements
   */
  length() {
    return this.size;
  }

  /**
   * Check if the queue is empty
   * @returns {boolean} Whether the queue is empty
   */
  isEmpty() {
    return this.size === 0;
  }

  /**
   * Add an element to the queue
   * @param {*} element - Element to add
   */
  enqueue(element) {
    this.heap.push(element);
    this.size++;
    this._siftUp(this.size - 1);
    return this.size;
  }

  /**
   * Remove and return the highest priority element
   * @returns {*} Highest priority element
   */
  dequeue() {
    if (this.isEmpty()) {
      return null;
    }

    const top = this.heap[0];
    const bottom = this.heap.pop();
    this.size--;

    if (this.size > 0) {
      this.heap[0] = bottom;
      this._siftDown(0);
    }

    return top;
  }

  /**
   * Get the highest priority element without removing it
   * @returns {*} Highest priority element
   */
  peek() {
    return this.isEmpty() ? null : this.heap[0];
  }

  /**
   * Remove a specific element from the queue
   * @param {*} element - Element to remove
   * @param {Function} equalityFn - Function to check equality (a, b) => boolean
   * @returns {boolean} Whether the element was found and removed
   */
  remove(element, equalityFn = (a, b) => a === b) {
    for (let i = 0; i < this.size; i++) {
      if (equalityFn(this.heap[i], element)) {
        // Replace with the last element
        const last = this.heap.pop();
        this.size--;

        // If we removed the last element, we're done
        if (i === this.size) {
          return true;
        }

        // Otherwise, replace the removed element with the last one and restore heap property
        this.heap[i] = last;
        
        // Determine whether to sift up or down
        const parentIndex = this._parent(i);
        if (parentIndex >= 0 && this.comparator(this.heap[i], this.heap[parentIndex]) < 0) {
          this._siftUp(i);
        } else {
          this._siftDown(i);
        }
        
        return true;
      }
    }
    
    return false;
  }

  /**
   * Update the priority of an element
   * @param {*} element - Element to update
   * @param {*} newPriority - New priority value
   * @param {Function} equalityFn - Function to check equality (a, b) => boolean
   * @returns {boolean} Whether the element was found and updated
   */
  updatePriority(element, newPriority, equalityFn = (a, b) => a === b) {
    for (let i = 0; i < this.size; i++) {
      if (equalityFn(this.heap[i], element)) {
        const oldPriority = this.heap[i].priority;
        this.heap[i].priority = newPriority;
        
        // Determine whether to sift up or down
        if (newPriority < oldPriority) {
          this._siftUp(i);
        } else if (newPriority > oldPriority) {
          this._siftDown(i);
        }
        
        return true;
      }
    }
    
    return false;
  }

  /**
   * Get all elements in the queue as an array
   * @returns {Array} Array of all elements
   */
  toArray() {
    return [...this.heap];
  }

  /**
   * Clear the queue
   */
  clear() {
    this.heap = [];
    this.size = 0;
  }

  /**
   * Find an element in the queue
   * @param {Function} predicate - Function to test elements (element) => boolean
   * @returns {*} Found element or null if not found
   */
  find(predicate) {
    for (let i = 0; i < this.size; i++) {
      if (predicate(this.heap[i])) {
        return this.heap[i];
      }
    }
    
    return null;
  }

  /**
   * Filter the queue to get elements matching a predicate
   * @param {Function} predicate - Function to test elements (element) => boolean
   * @returns {Array} Array of matching elements
   */
  filter(predicate) {
    const result = [];
    
    for (let i = 0; i < this.size; i++) {
      if (predicate(this.heap[i])) {
        result.push(this.heap[i]);
      }
    }
    
    return result;
  }

  /**
   * Get the index of the parent node
   * @param {number} index - Child index
   * @returns {number} Parent index
   * @private
   */
  _parent(index) {
    return Math.floor((index - 1) / 2);
  }

  /**
   * Get the index of the left child
   * @param {number} index - Parent index
   * @returns {number} Left child index
   * @private
   */
  _leftChild(index) {
    return 2 * index + 1;
  }

  /**
   * Get the index of the right child
   * @param {number} index - Parent index
   * @returns {number} Right child index
   * @private
   */
  _rightChild(index) {
    return 2 * index + 2;
  }

  /**
   * Sift an element up to restore heap property
   * @param {number} index - Element index
   * @private
   */
  _siftUp(index) {
    let currentIndex = index;
    let parentIndex = this._parent(currentIndex);
    
    while (
      currentIndex > 0 &&
      this.comparator(this.heap[currentIndex], this.heap[parentIndex]) < 0
    ) {
      // Swap elements
      [this.heap[currentIndex], this.heap[parentIndex]] = 
        [this.heap[parentIndex], this.heap[currentIndex]];
      
      // Move up
      currentIndex = parentIndex;
      parentIndex = this._parent(currentIndex);
    }
  }

  /**
   * Sift an element down to restore heap property
   * @param {number} index - Element index
   * @private
   */
  _siftDown(index) {
    let currentIndex = index;
    let minIndex = currentIndex;
    
    while (true) {
      const leftChildIndex = this._leftChild(currentIndex);
      const rightChildIndex = this._rightChild(currentIndex);
      
      // Check if left child has higher priority
      if (
        leftChildIndex < this.size &&
        this.comparator(this.heap[leftChildIndex], this.heap[minIndex]) < 0
      ) {
        minIndex = leftChildIndex;
      }
      
      // Check if right child has higher priority
      if (
        rightChildIndex < this.size &&
        this.comparator(this.heap[rightChildIndex], this.heap[minIndex]) < 0
      ) {
        minIndex = rightChildIndex;
      }
      
      // If current element has highest priority, we're done
      if (minIndex === currentIndex) {
        break;
      }
      
      // Swap with the higher priority child
      [this.heap[currentIndex], this.heap[minIndex]] = 
        [this.heap[minIndex], this.heap[currentIndex]];
      
      // Move down
      currentIndex = minIndex;
    }
  }
}

module.exports = PriorityQueue;
