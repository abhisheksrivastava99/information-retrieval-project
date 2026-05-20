# Local Business Review Search and Sentiment Insight Tool

This project is a command-line NLP / Information Retrieval application built for the Santa Barbara metropolitan business and review dataset.

It supports:

- `build-index`: preprocess the dataset and build the TF-IDF search index
- `search`: find relevant businesses for a natural-language query
- `business-summary`: summarize review praise and complaints for one business
- `category-analysis`: analyze one business category

## 1. Requirements

- Python `3.9` or newer
- Git
- Git LFS

Install dependencies with:

```bash
pip install -r requirements.txt
```

If needed, you can also install manually:

```bash
pip install pandas scikit-learn joblib scipy openpyxl
```

## 2. Dataset Setup

Do not rely on GitHub's `Download ZIP` flow if you need the dataset. The supported workflow is:

```bash
git lfs install
python app.py fetch-data
```

This downloads the Git LFS-backed dataset files into `data/`:

- `data/businesses_CA(Sheet1).csv`
- `data/reviews_CA(Sheet1).csv`

The tool automatically looks for dataset files in this order:

1. `data/`
2. the project root

Supported formats:

- `.csv`
- `.xlsx`

## 3. Build the Index

Run this first after fetching the dataset:

```bash
python app.py build-index
```

You can also provide explicit file paths:

```bash
python app.py build-index --business-file "data/businesses_CA(Sheet1).csv" --review-file "data/reviews_CA(Sheet1).csv"
```

This command:

- loads the business and review datasets
- cleans and joins the data
- builds a TF-IDF review index
- stores cache artifacts in `.cache/business_review_tool/`

### Sample input

```bash
python app.py build-index
```

### Sample output

```text
Index built successfully in: /path/to/project/.cache/business_review_tool
Businesses indexed: 5203
Reviews indexed: 348856
Matrix shape: (348856, 40000)
```

## 4. Search for Businesses

Basic search:

```bash
python app.py search --query "best seafood with outdoor seating"
```

Search with filters:

```bash
python app.py search --query "friendly staff" --city "Goleta" --top-k 10
python app.py search --query "brunch" --category "Restaurants" --min-stars 4
```

### Search output includes

- business name
- city
- business stars
- review count
- relevance score
- categories
- matching review count
- one representative review snippet
- top praise terms
- top complaint terms

### Sample input

```bash
python app.py search --query "best seafood with outdoor seating" --top-k 3
```

### Sample output

```text
1. Brophy Bros - Santa Barbara (Santa Barbara)
   Stars: 4.0 | Reviews: 2940 | Relevance: 0.4910
   Categories: Cocktail Bars, Fish & Chips, Nightlife, Seafood, Restaurants, Bars
   Matching review count: 53
   Snippet: Best seafood joint in the area, their clams are my favorite!
   Top praise: chowder, place, clam, clam chowder
   Top complaints: None found

2. Santa Barbara FisHouse (Santa Barbara)
   Stars: 3.5 | Reviews: 1140 | Relevance: 0.4770
   Categories: Tapas/Small Plates, Desserts, Restaurants, Breakfast & Brunch, Food, Seafood
   Matching review count: 10
   Snippet: Simply the best seafood I've ever had in my life. Period. Love the outdoor seating, fast service and great attitude. A+
   Top praise: food, place, service, clam
   Top complaints: None found

3. Santa Barbara Shellfish Company (Santa Barbara)
   Stars: 4.0 | Reviews: 2404 | Relevance: 0.4527
   Categories: Live/Raw Food, Restaurants, Seafood, Beer Bar, Beer, Wine & Spirits, Bars, Food, Nightlife
   Matching review count: 39
   Snippet: Best seafood around. Super fresh. Divey feel without a lot of indoor space, but huge beautiful outdoor seating area...
   Top praise: place, fresh, super, crab
   Top complaints: None found
```

## 5. Business Summary

Use this command to summarize one business:

```bash
python app.py business-summary --business "Helena Avenue Bakery"
```

### Business summary output includes

- business name and city
- business star rating
- business review count
- indexed review count
- average review stars
- top praise terms
- top complaint terms
- positive review snippets
- negative review snippets

### Sample input

```bash
python app.py business-summary --business "Helena Avenue Bakery"
```

### Sample output

```text
Helena Avenue Bakery (Santa Barbara)
Business stars: 4.0 | Business review count: 389
Categories: Food, Restaurants, Salad, Coffee & Tea, Breakfast & Brunch, Sandwiches, Bakeries
Indexed review count: 401 | Average review stars: 4.22
Top praise: breakfast, sandwich, delicious, place
Top complaints: bakery, order, food, coffee
Positive snippets:
- What a great addition to the Funk Zone! Grab a bite, grab some tastings, life is good...
- This place is a great casual breakfast spot. You order at the counter and they bring your meal to the patio tables...
Negative snippets:
- The food was good but the service was terrible. The female staff was downright rude...
- Went for breakfast on a weekday. 10 minute line to order. Ordered breakfast and coffee...
```

## 6. Category Analysis

Use this command to analyze a business category:

```bash
python app.py category-analysis --category "Restaurants"
```

### Category analysis output includes

- category name
- number of matching businesses
- total reviews
- average business stars
- top cities
- top praise terms
- top complaint terms

### Sample input

```bash
python app.py category-analysis --category "Restaurants"
```

### Sample output

```text
Category: Restaurants
Business count: 1161
Total reviews: 211748
Average business stars: 3.76
Top cities: Santa Barbara (767), Goleta (220), Carpinteria (81), Isla Vista (55), Montecito (27)
Top praise: food, place, service, delicious
Top complaints: food, place, service, order
```

## 7. Cache Folder

The application creates cached files in:

```bash
.cache/business_review_tool/
```

This folder stores:

- cleaned business data
- cleaned review data
- TF-IDF vectorizer
- sparse review matrix
- metadata file

If the cache does not exist yet, run:

```bash
python app.py build-index
```

## 8. Example Workflow

```bash
python app.py fetch-data
python app.py build-index
python app.py search --query "best seafood with outdoor seating" --top-k 5
python app.py business-summary --business "Helena Avenue Bakery"
python app.py category-analysis --category "Restaurants"
```

## 9. Notes

- The application is fully command-line based.
- No relational database is required.
- The cached files can be deleted and rebuilt at any time.
- Do not include the dataset files, cache folder, or installed libraries in the final coursework submission archive.
- Use `git lfs install` and `python app.py fetch-data` to reproduce the dataset locally.
