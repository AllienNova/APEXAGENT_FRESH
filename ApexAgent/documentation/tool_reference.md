# Aideon AI Lite Tool Reference

This document provides a comprehensive reference for all tools integrated into the Aideon AI Lite platform. These tools empower Aideon to perform a vast array of tasks across numerous domains, enhancing productivity and capability.

## Tool System Overview

The Aideon AI Lite tool system is managed by the `ToolManager`, which dynamically loads and provides access to tools organized by domain. Each tool is defined with a unique ID, a descriptive name, a clear description of its function, input/output schemas for data validation, and an execution method. Tools are designed to be robust, with built-in error handling and validation.

## Tool Domains

Aideon AI Lite features specialized tool providers for the following domains:

1.  **Software Development:** Tools for coding, debugging, testing, and documentation.
2.  **Data Science:** Tools for data analysis, visualization, machine learning, and preprocessing.
3.  **Business & Finance:** Tools for financial calculations, market analysis, reporting, and planning.
4.  **Healthcare:** Tools for medical research, symptom analysis, and health record management.
5.  **Legal:** Tools for legal research, document analysis, and compliance checks.
6.  **Creative & Design:** Tools for image generation, text styling, color palette creation, and design analysis.
7.  **Content & Communication:** Tools for writing, editing, translation, summarization, and communication management.
8.  **Engineering:** Tools for simulations, calculations, CAD interactions, and material analysis across various engineering fields.
9.  **Education & Research:** Tools for literature search, citation generation, concept explanation, and quiz creation.
10. **Marketing & Sales:** Tools for SEO analysis, lead generation, market research, and CRM interaction.
11. **Project Management:** Tools for task tracking, scheduling, resource allocation, and reporting.
12. **Science Research:** Tools for scientific data analysis, simulation execution, literature review, and experiment design.
13. **Agriculture & Environmental:** Tools for crop monitoring, soil analysis, weather forecasting, and environmental impact assessment.
14. **Architecture & Construction:** Tools for design analysis, material estimation, building code lookup, and project scheduling.
15. **Energy & Utilities:** Tools for energy consumption analysis, renewable energy assessment, grid monitoring, and rate optimization.

Below is a detailed reference for the tools available in each domain.

---

## 1. Software Development Tools

Provided by `SoftwareDevelopmentTools.js`, these tools assist with various aspects of the software development lifecycle.

### `code_generate`

*   **Name:** Generate Code
*   **Description:** Generates code snippets or complete functions based on natural language requirements, target language, and optional context.
*   **Category:** coding
*   **Input Schema:**
    *   `requirements` (string, required): Detailed description of the desired code functionality.
    *   `language` (string, required): Target programming language (e.g., 'javascript', 'python', 'java').
    *   `context` (string, optional): Existing code or context to integrate with.
    *   `style_guide` (string, optional): Preferred coding style or conventions.
*   **Output Schema:**
    *   `generated_code` (string): The generated code snippet or function.
    *   `explanation` (string): An explanation of the generated code.
    *   `dependencies` (array): List of potential libraries or dependencies used.
*   **Usage Example:**
    ```json
    {
      "requirements": "Create a Python function that takes a list of numbers and returns the sum of squares.",
      "language": "python"
    }
    ```
*   **Operations:** `llm_inference`

### `code_debug`

*   **Name:** Debug Code
*   **Description:** Analyzes provided code and error messages to identify bugs and suggest fixes.
*   **Category:** debugging
*   **Input Schema:**
    *   `code` (string, required): The code snippet containing the suspected bug.
    *   `language` (string, required): The programming language of the code.
    *   `error_message` (string, optional): The error message or stack trace observed.
    *   `desired_behavior` (string, optional): Description of the expected correct behavior.
*   **Output Schema:**
    *   `identified_issue` (string): Description of the identified bug or issue.
    *   `suggested_fix` (string): The proposed code modification to fix the bug.
    *   `explanation` (string): Rationale behind the suggested fix.
*   **Usage Example:**
    ```json
    {
      "code": "function sum(a, b) { return a - b; }",
      "language": "javascript",
      "desired_behavior": "The function should return the sum of a and b."
    }
    ```
*   **Operations:** `llm_inference`

### `code_review`

*   **Name:** Review Code
*   **Description:** Reviews code for quality, adherence to best practices, potential issues, and style consistency.
*   **Category:** quality_assurance
*   **Input Schema:**
    *   `code` (string, required): The code snippet to be reviewed.
    *   `language` (string, required): The programming language of the code.
    *   `review_focus` (array, optional): Specific areas to focus on (e.g., ['performance', 'security', 'readability']).
    *   `style_guide` (string, optional): Specific style guide to check against (e.g., 'PEP 8', 'Google Java Style').
*   **Output Schema:**
    *   `review_summary` (string): Overall assessment of the code quality.
    *   `issues_found` (array): List of identified issues with severity, description, and suggested improvement.
    *   `quality_score` (number): A numerical score (0-100) representing overall quality.
*   **Usage Example:**
    ```json
    {
      "code": "for i in range(len(my_list)): print(my_list[i])",
      "language": "python",
      "review_focus": ["readability", "pythonic_style"]
    }
    ```
*   **Operations:** `llm_inference`

### `code_refactor`

*   **Name:** Refactor Code
*   **Description:** Refactors existing code to improve its structure, readability, performance, or maintainability without changing its external behavior.
*   **Category:** code_improvement
*   **Input Schema:**
    *   `code` (string, required): The code snippet to be refactored.
    *   `language` (string, required): The programming language of the code.
    *   `refactoring_goal` (string, required): The objective of the refactoring (e.g., 'improve performance', 'increase readability', 'reduce complexity').
    *   `constraints` (string, optional): Any constraints or specific patterns to follow/avoid.
*   **Output Schema:**
    *   `refactored_code` (string): The refactored code.
    *   `explanation` (string): Description of the changes made and the rationale.
    *   `potential_impact` (string): Notes on potential impacts (e.g., performance improvements, API changes).
*   **Usage Example:**
    ```json
    {
      "code": "if x > 10:\n  y = 5\nelse:\n  y = 2",
      "language": "python",
      "refactoring_goal": "Use a ternary operator for conciseness."
    }
    ```
*   **Operations:** `llm_inference`

### `code_document`

*   **Name:** Document Code
*   **Description:** Generates documentation (e.g., docstrings, comments, README sections) for provided code.
*   **Category:** documentation
*   **Input Schema:**
    *   `code` (string, required): The code snippet to document.
    *   `language` (string, required): The programming language of the code.
    *   `documentation_type` (string, required): Type of documentation needed (e.g., 'docstring', 'inline_comments', 'readme_usage').
    *   `format` (string, optional): Specific documentation format (e.g., 'google', 'numpy', 'jsdoc').
*   **Output Schema:**
    *   `documentation` (string): The generated documentation content.
    *   `placement_suggestion` (string): Suggestion on where to place the documentation (e.g., 'above function definition', 'within README.md').
*   **Usage Example:**
    ```json
    {
      "code": "def calculate_area(length, width): return length * width",
      "language": "python",
      "documentation_type": "docstring",
      "format": "google"
    }
    ```
*   **Operations:** `llm_inference`

### `code_test`

*   **Name:** Generate Test Cases
*   **Description:** Creates test cases (e.g., unit tests, integration tests) for a given code snippet or function.
*   **Category:** testing
*   **Input Schema:**
    *   `code` (string, required): The code snippet or function to test.
    *   `language` (string, required): The programming language of the code.
    *   `test_framework` (string, required): The testing framework to use (e.g., 'pytest', 'jest', 'junit').
    *   `test_type` (string, optional): Type of tests needed (e.g., 'unit', 'edge_cases', 'integration'). Defaults to 'unit'.
*   **Output Schema:**
    *   `test_code` (string): The generated test code.
    *   `setup_instructions` (string): Instructions on how to set up and run the tests.
    *   `coverage_notes` (string): Notes on the aspects covered by the generated tests.
*   **Usage Example:**
    ```json
    {
      "code": "function factorial(n) { if (n === 0) return 1; return n * factorial(n-1); }",
      "language": "javascript",
      "test_framework": "jest",
      "test_type": "edge_cases"
    }
    ```
*   **Operations:** `llm_inference`

---

## 2. Data Science Tools

Provided by `DataScienceTools.js`, these tools support various tasks in the data science workflow, from analysis and visualization to machine learning.

### `data_analyze`

*   **Name:** Analyze Data
*   **Description:** Performs statistical analysis on a dataset to extract insights, identify trends, and summarize key characteristics.
*   **Category:** data_analysis
*   **Input Schema:**
    *   `data_source` (object, required): Information about the data source.
        *   `type` (string, required): 'file' or 'dataframe_id'.
        *   `path` (string, optional): Path to the data file (CSV, JSON, Excel) if type is 'file'.
        *   `id` (string, optional): Identifier for an existing dataframe in memory if type is 'dataframe_id'.
    *   `analysis_type` (string, required): Type of analysis (e.g., 'summary_statistics', 'correlation_analysis', 'trend_analysis', 'anomaly_detection').
    *   `columns` (array, optional): Specific columns to focus the analysis on.
    *   `parameters` (object, optional): Additional parameters specific to the analysis type (e.g., time window for trend analysis).
*   **Output Schema:**
    *   `analysis_summary` (string): Text summary of the key findings.
    *   `results` (object): Detailed results of the analysis (e.g., correlation matrix, statistical measures, identified anomalies).
    *   `visualizations` (array): Suggestions for relevant visualizations based on the analysis.
*   **Usage Example:**
    ```json
    {
      "data_source": { "type": "file", "path": "/home/ubuntu/data/sales_data.csv" },
      "analysis_type": "summary_statistics"
    }
    ```
*   **Operations:** `local_file_access`, `local_process_execution` (requires Python environment with pandas, numpy, scipy)

### `data_visualize`

*   **Name:** Visualize Data
*   **Description:** Generates various types of plots and charts from data to help understand patterns and relationships visually.
*   **Category:** data_visualization
*   **Input Schema:**
    *   `data_source` (object, required): Information about the data source (similar to `data_analyze`).
    *   `plot_type` (string, required): Type of plot (e.g., 'histogram', 'scatter_plot', 'line_chart', 'bar_chart', 'heatmap', 'box_plot').
    *   `x_column` (string, required): Column for the x-axis.
    *   `y_column` (string, optional): Column for the y-axis (required for most plots).
    *   `color_column` (string, optional): Column to use for coloring points or bars.
    *   `facet_column` (string, optional): Column to create separate plots for each category.
    *   `title` (string, optional): Title for the plot.
    *   `output_path` (string, required): Path to save the generated plot image (e.g., '/home/ubuntu/plots/sales_trend.png').
*   **Output Schema:**
    *   `plot_file_path` (string): Absolute path to the saved plot image.
    *   `plot_description` (string): A brief description of what the plot shows.
*   **Usage Example:**
    ```json
    {
      "data_source": { "type": "file", "path": "/home/ubuntu/data/iris.csv" },
      "plot_type": "scatter_plot",
      "x_column": "sepal_length",
      "y_column": "sepal_width",
      "color_column": "species",
      "title": "Iris Sepal Dimensions by Species",
      "output_path": "/home/ubuntu/plots/iris_scatter.png"
    }
    ```
*   **Operations:** `local_file_access`, `local_process_execution` (requires Python environment with pandas, matplotlib, seaborn)

### `data_preprocess`

*   **Name:** Preprocess Data
*   **Description:** Cleans, transforms, and prepares raw data for analysis or machine learning model training.
*   **Category:** data_preparation
*   **Input Schema:**
    *   `data_source` (object, required): Information about the input data source.
    *   `operations` (array, required): List of preprocessing steps to perform.
        *   Each item is an object: `{ "operation": "operation_name", "parameters": { ... } }`
        *   Examples: `handle_missing_values`, `scale_numeric_features`, `encode_categorical_features`, `remove_duplicates`, `feature_engineering`.
    *   `output_destination` (object, required): Where to save the preprocessed data.
        *   `type` (string, required): 'file' or 'dataframe_id'.
        *   `path` (string, optional): Path for the output file.
        *   `id` (string, optional): ID for the new dataframe in memory.
*   **Output Schema:**
    *   `output_location` (string): Path or ID of the preprocessed data.
    *   `summary_of_changes` (string): Description of the preprocessing steps applied and their impact.
    *   `new_data_shape` (object): Shape (rows, columns) of the processed data.
*   **Usage Example:**
    ```json
    {
      "data_source": { "type": "file", "path": "/home/ubuntu/data/raw_data.csv" },
      "operations": [
        { "operation": "handle_missing_values", "parameters": { "strategy": "mean", "columns": ["age"] } },
        { "operation": "encode_categorical_features", "parameters": { "method": "one_hot", "columns": ["category"] } }
      ],
      "output_destination": { "type": "file", "path": "/home/ubuntu/data/processed_data.csv" }
    }
    ```
*   **Operations:** `local_file_access`, `local_process_execution` (requires Python environment with pandas, scikit-learn)

### `ml_train`

*   **Name:** Train Machine Learning Model
*   **Description:** Trains a machine learning model on a given dataset using specified algorithms and parameters.
*   **Category:** machine_learning
*   **Input Schema:**
    *   `data_source` (object, required): Information about the training data source (preprocessed data recommended).
    *   `target_column` (string, required): The column to predict.
    *   `feature_columns` (array, optional): List of columns to use as features (defaults to all others).
    *   `model_type` (string, required): Type of model (e.g., 'classification', 'regression', 'clustering').
    *   `algorithm` (string, required): Specific algorithm to use (e.g., 'logistic_regression', 'random_forest', 'kmeans', 'xgboost').
    *   `hyperparameters` (object, optional): Algorithm-specific hyperparameters.
    *   `evaluation_metric` (string, optional): Metric to optimize during training (e.g., 'accuracy', 'f1_score', 'rmse', 'silhouette_score').
    *   `output_model_path` (string, required): Path to save the trained model object.
*   **Output Schema:**
    *   `model_path` (string): Absolute path to the saved trained model file.
    *   `training_summary` (object): Summary including training time, final evaluation score on training/validation set.
    *   `feature_importance` (object, optional): Importance scores for features (if applicable).
*   **Usage Example:**
    ```json
    {
      "data_source": { "type": "file", "path": "/home/ubuntu/data/processed_data.csv" },
      "target_column": "is_fraud",
      "model_type": "classification",
      "algorithm": "random_forest",
      "hyperparameters": { "n_estimators": 100, "max_depth": 10 },
      "evaluation_metric": "f1_score",
      "output_model_path": "/home/ubuntu/models/fraud_detector.pkl"
    }
    ```
*   **Operations:** `local_file_access`, `local_process_execution` (requires Python environment with pandas, scikit-learn, potentially others like xgboost, tensorflow, pytorch)

### `ml_evaluate`

*   **Name:** Evaluate Machine Learning Model
*   **Description:** Evaluates the performance of a trained machine learning model on a separate test dataset.
*   **Category:** machine_learning
*   **Input Schema:**
    *   `model_path` (string, required): Path to the saved trained model file.
    *   `test_data_source` (object, required): Information about the test dataset source.
    *   `target_column` (string, required): The true target column in the test data.
    *   `metrics` (array, required): List of evaluation metrics to calculate (e.g., ['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc', 'rmse', 'mae']).
*   **Output Schema:**
    *   `evaluation_scores` (object): Dictionary of calculated metric scores.
    *   `confusion_matrix` (object, optional): Confusion matrix for classification models.
    *   `classification_report` (string, optional): Detailed classification report.
    *   `plot_paths` (object, optional): Paths to generated evaluation plots (e.g., ROC curve, precision-recall curve).
*   **Usage Example:**
    ```json
    {
      "model_path": "/home/ubuntu/models/fraud_detector.pkl",
      "test_data_source": { "type": "file", "path": "/home/ubuntu/data/test_data.csv" },
      "target_column": "is_fraud",
      "metrics": ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    }
    ```
*   **Operations:** `local_file_access`, `local_process_execution` (requires Python environment with pandas, scikit-learn, matplotlib)

### `ml_deploy`

*   **Name:** Deploy Machine Learning Model
*   **Description:** Deploys a trained machine learning model as an API endpoint or integrates it into a specified environment.
*   **Category:** machine_learning
*   **Input Schema:**
    *   `model_path` (string, required): Path to the saved trained model file.
    *   `deployment_target` (string, required): Where to deploy the model (e.g., 'local_api', 'cloud_function', 'docker_container').
    *   `api_config` (object, optional): Configuration for API deployment (e.g., endpoint name, port, authentication).
    *   `environment_config` (object, optional): Configuration for other deployment targets.
*   **Output Schema:**
    *   `deployment_status` (string): 'success' or 'failure'.
    *   `endpoint_url` (string, optional): URL of the deployed API endpoint.
    *   `deployment_id` (string, optional): Identifier for the deployment.
    *   `access_instructions` (string): How to access or use the deployed model.
*   **Usage Example:**
    ```json
    {
      "model_path": "/home/ubuntu/models/fraud_detector.pkl",
      "deployment_target": "local_api",
      "api_config": { "endpoint_name": "/predict_fraud", "port": 5000 }
    }
    ```
*   **Operations:** `local_file_access`, `local_process_execution`, `network_access` (potentially requires frameworks like Flask/FastAPI, Docker, cloud SDKs)

---

