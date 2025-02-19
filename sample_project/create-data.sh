#! /bin/bash
# Loop N times
iterations=${1:-50}
for ((i=1; i<=$iterations; i++)); do
    # Generate a random temperature between 5 and 104 with two decimal places
    whole_part=$((RANDOM % 100))
    decimal_part=$((RANDOM % 100))
    temp=$(echo "scale=2; 1 + $whole_part + $decimal_part/100" | bc)
    curl -X POST http://localhost:8000/metrics/ -H "Content-Type: application/json" -d "{\"temp\": $temp}"
    echo ""
done
