from tools.db_tool import db_insert, db_select, db_list, db_top, db_delete

def test_db():
    print("Testing DB Tool...")
    # Clean up first
    db_delete("Test Candidate")
    
    # Insert
    res = db_insert("Test Candidate", 85, "Python, SQL", "No AWS", "Recommend", "http://test.com")
    print(res)
    
    # Select
    record = db_select("Test Candidate")
    print(f"Selected: {record}")
    
    # List
    all_cands = db_list()
    print(f"All candidates: {all_cands}")
    
    # Top
    top_cands = db_top(1)
    print(f"Top candidates: {top_cands}")
    
    # Delete
    del_res = db_delete("Test Candidate")
    print(del_res)
    
    # Verify deletion
    record_after = db_select("Test Candidate")
    print(f"Selected after delete: {record_after}")

if __name__ == "__main__":
    test_db()
