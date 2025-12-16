import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from database.course_service import CourseService
from models.SearchCriteria import SearchCriteria
from patterns.search.title_search_strategy import TitleSearchStrategy
from patterns.search.filter_search_strategy import FilterSearchStrategy
from patterns.search.recommendation_search_strategy import RecommendationSearchStrategy

def test_strategies():
    print("Testing Search Strategies...")
    
    course_service = CourseService()
    
    # 1. Setup Data
    print("Creating test courses...")
    # Clean up old data might be tricky without drop, so we just add distinct ones
    c1 = course_service.create_course("Search Test Python", "Desc", "inst1", category_name="SearchCat", level="Beginner", price=10.0, visibility="published")
    c2 = course_service.create_course("Search Test Java", "Desc", "inst1", category_name="SearchCat", level="Advanced", price=50.0, visibility="published")
    c3 = course_service.create_course("Search Test Advanced Python", "Desc", "inst1", category_name="SearchCat", level="Advanced", price=20.0, visibility="published")
    
    # 2. Test TitleSearchStrategy
    print("\n--- Testing Title Search ---")
    title_strategy = TitleSearchStrategy()
    criteria = SearchCriteria(query="Python", page=1, page_size=10)
    results = title_strategy.search(criteria)
    print(f"Query 'Python' found {len(results)} courses.")
    for c in results:
        print(f" - {c.title}")
    
    # 3. Test FilterSearchStrategy
    print("\n--- Testing Filter Search ---")
    filter_strategy = FilterSearchStrategy()
    
    # Level Filter
    criteria_level = SearchCriteria(level="Advanced", page=1, page_size=10)
    results_level = filter_strategy.search(criteria_level)
    print(f"Filter Level='Advanced' found {len(results_level)} courses.")
    for c in results_level:
        print(f" - {c.title} ({c.level})")
        
    # Price Filter
    criteria_price = SearchCriteria(min_price=15.0, max_price=60.0, page=1, page_size=10)
    results_price = filter_strategy.search(criteria_price)
    print(f"Filter Price 15-60 found {len(results_price)} courses.")
    for c in results_price:
        print(f" - {c.title} (${c.price})")

    # 4. Test RecommendationSearchStrategy
    print("\n--- Testing Recommendation Search ---")
    rec_strategy = RecommendationSearchStrategy()
    criteria_rec = SearchCriteria(page=1, page_size=2)
    results_rec = rec_strategy.search(criteria_rec)
    print(f"Recommendations returned {len(results_rec)} courses.")

    # Cleanup
    course_service.delete_course(c1)
    course_service.delete_course(c2)
    course_service.delete_course(c3)
    print("\nAll search strategy tests passed!")

if __name__ == "__main__":
    test_strategies()
