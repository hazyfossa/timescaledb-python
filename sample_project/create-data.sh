#! /bin/bash
# Loop 50 times
for i in {1..50}; do
    # Generate a random temperature between 5 and 104 with one decimal place
    temp=$(echo "scale=1; 313 + ($RANDOM % 9900) / 100" | bc)
    curl -X POST http://localhost:8000/metrics/ -H "Content-Type: application/json" -d "{\"temp\": $temp}"
    echo ""
    # Print progress
    # echo "Sent data point $i/50"
done
