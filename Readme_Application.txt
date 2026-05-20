Local Business Review Search and Sentiment Insight Tool

This file is the reproducibility guide for the submitted coursework.

1. Prerequisites
- Python 3.9 or newer
- Git
- Git LFS

2. Important note before starting
Do not use GitHub's "Download ZIP" button for this project if you need the dataset.
The dataset CSV files are stored through Git LFS, so the supported workflow is to clone the repository with Git, run Git LFS, and then use the built-in fetch command below.

3. Clone the repository
git clone https://github.com/abhisheksrivastava99/information-retrieval-project.git
cd information-retrieval-project

4. Install Python dependencies
python -m pip install -r requirements.txt

5. Enable Git LFS on the machine
git lfs install

6. Download the dataset files
python app.py fetch-data

What this command does:
- clones the public GitHub repository branch that stores the dataset in Git LFS
- downloads the real CSV files through Git LFS
- copies them into the local data folder

Expected downloaded files:
- data/businesses_CA(Sheet1).csv
- data/reviews_CA(Sheet1).csv

If the dataset already exists locally and you want to refresh it, run:
python app.py fetch-data --force

7. Build the search index
python app.py build-index

The build command automatically looks for dataset files in this order:
1. data/
2. the project root folder

Optional explicit file paths:
python app.py build-index --business-file "data/businesses_CA(Sheet1).csv" --review-file "data/reviews_CA(Sheet1).csv"

Sample build output:
Index built successfully in: /path/to/project/.cache/business_review_tool
Businesses indexed: 5203
Reviews indexed: 348856
Matrix shape: (348856, 40000)

8. Run the application
Search examples:
python app.py search --query "best seafood with outdoor seating"
python app.py search --query "friendly staff" --city "Goleta" --top-k 10
python app.py search --query "brunch" --category "Restaurants" --min-stars 4

Business summary example:
python app.py business-summary --business "Helena Avenue Bakery"

Category analysis example:
python app.py category-analysis --category "Restaurants"

9. Cache behavior
The application writes generated artifacts to:
.cache/business_review_tool/

This cache includes:
- cleaned business data
- cleaned review data
- TF-IDF vectorizer
- sparse review matrix
- metadata file

If the cache is missing, rebuild it with:
python app.py build-index

10. Reproducibility notes
- The dataset CSV files are not included in the final coursework submission archive.
- The project is reproducible by following this exact order:
  1. clone with Git
  2. run git lfs install
  3. run python app.py fetch-data
  4. run python app.py build-index
  5. run the query commands
- The fetch command uses the public GitHub repository and the Git LFS dataset branch, so no extra credentials are required.

11. Submission note
Do not include the dataset files, cache folder, or installed libraries in the final coursework submission archive.
