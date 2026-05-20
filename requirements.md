# Section 3.5 Requirements

## 1. Purpose

This document defines the requirements for the Section 3.5 application. The application should be a **simple command-line NLP / Information Retrieval tool** built only from the newly sampled dataset for the selected single metropolitan area.

Based on the attached files, the sampled area appears to be the **Santa Barbara metropolitan area in California**, with businesses concentrated in Santa Barbara, Goleta, Carpinteria, Isla Vista, Montecito, and nearby localities.

## 2. Dataset Analysis

### 2.1 Files Provided

- `businesses_CA (1).xlsx`
- `reviews_CA (1).xlsx`

### 2.2 Reviews Dataset Findings

The reviews workbook was readable and contains one sheet with the following structure:

- Rows: `348,856`
- Columns:
  - `review_id`
  - `user_id`
  - `business_id`
  - `stars`
  - `useful`
  - `funny`
  - `cool`
  - `text`
  - `date`

Observed characteristics:

- Unique businesses reviewed: `5,203`
- Unique users: `155,949`
- Review date range: `2005-03-01` to `2022-01-19`
- Review text is suitable for NLP because it contains long free-text opinions
- Star labels are available and can act as a simple supervision / polarity signal

Star distribution:

- `1 star`: `42,849`
- `2 stars`: `23,353`
- `3 stars`: `28,904`
- `4 stars`: `63,544`
- `5 stars`: `190,206`

This dataset is strongly suitable for:

- keyword-based retrieval
- ranking businesses by relevance
- review search
- opinion mining / sentiment summarization
- category-level text mining

### 2.3 Businesses Dataset Findings

The businesses workbook is partially recoverable but appears to be **truncated / corrupted** as an `.xlsx` archive. However, enough content was recovered to identify the schema and sample records.

Recovered structure:

- Expected rows from sheet metadata: `5,204` including header
- Approximate business records: `5,203`
- Columns:
  - `business_id`
  - `name`
  - `address`
  - `city`
  - `state`
  - `postal_code`
  - `latitude`
  - `longitude`
  - `stars`
  - `review_count`
  - `is_open`
  - `attributes`
  - `categories`
  - `hours`

Recovered business-location evidence shows the sample is centered on:

- `Santa Barbara`
- `Goleta`
- `Carpinteria`
- `Isla Vista`
- `Montecito`
- `Summerland`

Common business categories include:

- `Restaurants`
- `Shopping`
- `Food`
- `Home Services`
- `Health & Medical`
- `Beauty & Spas`
- `Local Services`
- `Active Life`
- `Automotive`
- `Nightlife`

Important data risk:

- Before final implementation, the businesses file should ideally be **re-downloaded, repaired, or re-exported** to avoid parsing failures during marking.
- The recovered schema is still sufficient to define the application requirements.

## 3. Recommended Application Scope

## 3.1 Recommended Project

The strongest fit for this dataset and assignment is a:

**CLI-based Local Business Review Search and Opinion Mining Tool**

This should combine:

- **Information Retrieval**: search reviews and businesses using a user query
- **NLP**: preprocess review text and produce sentiment-oriented summaries or keyword insights

This scope is appropriate because it is:

- simple enough for coursework
- clearly based on the provided sampled dataset
- easy to demonstrate from the command line
- aligned with both IR and NLP learning outcomes

## 3.2 Core Use Case

A user enters a natural-language query such as:

- `best seafood with outdoor seating`
- `slow service but great food`
- `family friendly brunch in goleta`
- `tattoo shops with friendly staff`

The system returns:

- the most relevant businesses
- representative matching review snippets
- average rating / review count
- optional sentiment summary or top positive / negative terms

## 4. Functional Requirements

The application should satisfy the following requirements.

### 4.1 Data Loading

- The system must load data only from the sampled businesses and reviews datasets for the chosen metropolitan area.
- The system must join business metadata with reviews using `business_id`.
- The system must operate locally without a relational database such as MySQL.

### 4.2 Text Preprocessing

- The system must preprocess review text before indexing or analysis.
- Preprocessing should include:
  - lowercasing
  - tokenization
  - punctuation removal
  - stop-word removal
- Optional preprocessing:
  - stemming or lemmatization
  - bigram extraction
  - normalization of category text

### 4.3 Search / Retrieval

- The system must accept a text query from the command line.
- The system must rank businesses or reviews by relevance.
- The retrieval method should be one of:
  - TF-IDF + cosine similarity
  - BM25
  - a simple inverted index with scoring
- The system should support optional filters such as:
  - city
  - category
  - minimum stars
  - open / closed status
  - review date range

### 4.4 NLP / Mining Output

The system should provide at least one NLP-based analysis feature beyond plain search, such as:

- sentiment label estimation from review stars
- extraction of top positive and negative keywords
- category-wise frequent terms
- summary statistics for a business based on its reviews
- most common complaint / praise terms

### 4.5 Results Display

The command-line output should be human-readable and concise.

For each result, the system should display some combination of:

- business name
- city
- category
- business star rating
- review count
- relevance score
- short review snippet
- sentiment-oriented keywords or summary

### 4.6 Command-Line Interface

The application must be run entirely from the command line.

Example command shapes:

```bash
python app.py --query "best seafood with outdoor seating"
python app.py --query "friendly staff" --city "Goleta" --top-k 10
python app.py --business "Helena Avenue Bakery"
python app.py --category "Restaurants" --analyze-keywords
```

## 5. Non-Functional Requirements

- The application must not be web-based.
- The application must not be a mobile app.
- The application must not rely on MySQL or another relational DBMS.
- The code should be simple enough for demonstration and explanation in the report.
- The application should return results within a reasonable time on the sampled dataset.
- The implementation should be reproducible from a clean setup using instructions in `Readme.txt`.

## 6. Suggested Technical Design

## 6.1 Recommended Language and Libraries

Recommended stack:

- `Python`
- `pandas` for loading and joining data
- `scikit-learn` for TF-IDF and cosine similarity
- `nltk` or `spaCy` for tokenization / stop-word removal / lemmatization
- `collections` / `re` / `json` for lightweight indexing and output formatting

These are suitable because they are common, free for educational use, and easy to cite in the report.

## 6.2 Recommended Internal Pipeline

1. Load businesses and reviews
2. Clean / repair missing values
3. Merge on `business_id`
4. Preprocess review text
5. Build searchable text representation
6. Accept CLI query and optional filters
7. Rank candidate businesses or reviews
8. Produce search results plus one NLP insight layer

## 6.3 Recommended Storage

Allowed simple storage options:

- in-memory data structures
- serialized `pickle` / `json` / `csv` intermediate files
- local inverted index files

Not allowed:

- MySQL
- PostgreSQL if used as a relational backend for this assignment

## 7. Minimum Viable Feature Set

To keep the project realistic, the minimum acceptable version should include:

- loading both datasets
- joining by `business_id`
- preprocessing review text
- keyword query search
- ranked output of top matching businesses or reviews
- at least one NLP insight feature
- clear CLI arguments

## 8. Recommended Extended Features

If time permits, the project can include:

- separate modes for `search`, `business-summary`, and `category-analysis`
- sentiment trend by year
- positive vs negative keyword comparison
- filtering by category and location
- exporting result summaries to `.txt` or `.csv`

## 9. Report Requirements Mapping

The final implementation and documentation should satisfy the assignment requirements as follows.

### 9.1 In the Report

The report should include:

- the application objective
- why this application fits the dataset
- overall system design
- the retrieval / NLP method used
- important code snippets only
- example inputs and outputs
- limitations
- citations for third-party libraries

The report should **not** include the full source code listing.

### 9.2 In `Readme.txt`

The `Readme.txt` must include:

- installation steps
- required Python version
- package installation command
- exact command lines to run the program
- description of input arguments
- explanation of sample output

### 9.3 In Final Submission

The final source folder must include:

- your own source code
- `Readme.txt`
- any small config files needed to run the system

The final source folder must exclude:

- the dataset files
- downloaded libraries
- virtual environments
- cache folders

## 10. Final Recommendation

The recommended Section 3.5 solution is:

**A command-line business review retrieval and sentiment insight system for the Santa Barbara metropolitan sample.**

This is the best fit because it directly uses:

- business metadata
- review text
- star ratings
- categories
- location filters

It is also straightforward to explain, implement, test, and demonstrate within the coursework constraints.

## 11. Implementation Note

Before coding the final system, the `businesses_CA (1).xlsx` file should be repaired or replaced with a valid copy if possible. The current file is partially truncated, although its column structure and metropolitan-area focus were still recoverable for requirements analysis.
