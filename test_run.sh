#!/bin/bash
# test_optimizer.sh

echo "🧪 Testing SQL Query Optimizer"
echo "==============================="

# Create example directory if it doesn't exist
mkdir -p example_queries

# Array of test files
queries=(
    "simple_select.sql"
    "basic_join.sql"
    "aggregation_query.sql"
    "subquery_example.sql"
    "multiple_joins.sql"
    "window_functions.sql"
    "cte_example.sql"
    "unoptimized_query.sql"
    "complex_analytics.sql"
    "update_query.sql"
    "insert_select.sql"
    "monthly_report.sql"
    "cross_tab_analysis.sql"
)

# Test each query for both databases
for query in "${queries[@]}"; do
    echo ""
    echo "🔍 Testing: $query"
    echo "-------------------"
    
    # Oracle optimization
    echo "⚡ Oracle optimization..."
    python src/main.py optimize "example_queries/$query" --database oracle
    
    # SQLite optimization
    echo "⚡ SQLite optimization..."
    python src/main.py optimize "example_queries/$query" --database sqlite
    
    echo "✅ Completed: $query"
done

echo ""
echo "🎉 All tests completed!"
echo "📁 Check the example_queries/ directory for output JSON files"
