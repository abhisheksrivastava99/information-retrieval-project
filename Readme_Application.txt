Local Business Review Search and Sentiment Insight Tool

1. Python version
Use Python 3.9 or newer.

2. Install command
pip install pandas scikit-learn joblib scipy openpyxl

3. Dataset files
Place the dataset files in the project folder. The tool auto-detects files that begin with:
- businesses
- reviews

Supported formats:
- CSV
- XLSX

Current sample files in this project:
- businesses_CA(Sheet1).csv
- reviews_CA(Sheet1).csv

4. Build the index
python app.py build-index

Optional explicit file paths:
python app.py build-index --business-file "businesses_CA(Sheet1).csv" --review-file "reviews_CA(Sheet1).csv"

Sample input:
python app.py build-index

Sample output:
Index built successfully in: /path/to/project/.cache/business_review_tool
Businesses indexed: 5203
Reviews indexed: 348856
Matrix shape: (348856, 40000)

5. Search command
python app.py search --query "best seafood with outdoor seating"
python app.py search --query "friendly staff" --city "Goleta" --top-k 10
python app.py search --query "brunch" --category "Restaurants" --min-stars 4

Output fields:
- business name and city
- business stars and review count
- relevance score
- categories
- matching review count
- one representative review snippet
- top praise terms
- top complaint terms

Sample input:
python app.py search --query "best seafood with outdoor seating" --top-k 3

Sample output:
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

6. Business summary command
python app.py business-summary --business "Helena Avenue Bakery"

Output fields:
- business stars and review count
- number of indexed reviews
- average review stars
- common praise terms
- common complaint terms
- positive and negative review snippets

Sample input:
python app.py business-summary --business "Helena Avenue Bakery"

Sample output:
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

7. Category analysis command
python app.py category-analysis --category "Restaurants"

Output fields:
- category name
- number of matching businesses
- total reviews
- average business stars
- top cities
- top praise and complaint terms

Sample input:
python app.py category-analysis --category "Restaurants"

Sample output:
Category: Restaurants
Business count: 1161
Total reviews: 211748
Average business stars: 3.76
Top cities: Santa Barbara (767), Goleta (220), Carpinteria (81), Isla Vista (55), Montecito (27)
Top praise: food, place, service, delicious
Top complaints: food, place, service, order

8. Cache behavior
The tool writes generated artifacts into:
.cache/business_review_tool/

This folder includes:
- cleaned business and review data
- TF-IDF vectorizer
- sparse review matrix
- metadata describing the built index

If the cache is missing, run:
python app.py build-index

9. Submission note
Do not include the dataset files, cached index files, or downloaded libraries in the final coursework submission archive.
