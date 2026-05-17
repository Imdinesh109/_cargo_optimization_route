# Cargo Routing Optimization (CO-008) Synthetic Dataset

## Business Use Case

This synthetic dataset simulates a real-world airline and freight forwarding cargo routing optimization environment for Saudi Logistics Services (SAL).

The objective of this dataset is to support Machine Learning models that predict the most optimal air cargo route for shipments destined to Jeddah (`JED`).

The ML system evaluates multiple candidate routes for each shipment and assigns an `optimization_score` between `0.0` and `1.0`.

Higher scores indicate routes that are operationally superior based on:
- Lower transportation cost
- Faster transit time
- Higher route reliability
- Better capacity availability
- Lower weather disruption risk
- Fewer transshipments
- Better handling compatibility

---

# Dataset Files

| File Name | Description |
|---|---|
| cargo_routing_train.csv | Training dataset with 14,000 rows |
| cargo_routing_validation.csv | Validation dataset with 3,500 rows |
| cargo_routing_test.csv | Test dataset with 3,500 rows |
| feature_contribution_reference.txt | Optimization score feature logic |
| README.md | Dataset documentation |

---

# Dataset Statistics

| Split | Rows |
|---|---|
| Training | 14000 |
| Validation | 3500 |
| Test | 3500 |
| Total | 21000 |

Date Range:
- March 2025 to February 2026

Destination Airport:
- Always `JED` (King Abdulaziz International Airport, Jeddah)

---

# Feature Documentation

## 1. record_id
Unique route record identifier.

Example:
- RTE_000001

Type:
- Identifier

---

## 2. timestamp
Timestamp representing when the routing decision was generated.

Type:
- Datetime

Range:
- 2025-03-01 to 2026-02-28

---

## 3. shipment_id
Unique shipment identifier.

Multiple candidate routes share the same shipment ID.

Example:
- SHP_000210

Type:
- Identifier

---

## 4. candidate_route_id
Identifier representing a candidate route within a shipment.

Examples:
- CR_01
- CR_02
- CR_03

Type:
- Identifier

---

## 5. origin
Origin airport IATA code.

### Europe
- AMS → Amsterdam
- FRA → Frankfurt
- LHR → London Heathrow
- CDG → Paris Charles de Gaulle
- BRU → Brussels
- IST → Istanbul
- MAD → Madrid

### Middle East
- DXB → Dubai
- DOH → Doha
- AUH → Abu Dhabi
- RUH → Riyadh
- KWI → Kuwait

### Asia
- SIN → Singapore
- HKG → Hong Kong
- PVG → Shanghai Pudong
- ICN → Seoul Incheon
- NRT → Tokyo Narita
- DEL → Delhi
- BOM → Mumbai

### North America
- JFK → New York
- LAX → Los Angeles
- ORD → Chicago
- ATL → Atlanta
- MIA → Miami

### Africa
- ADD → Addis Ababa
- NBO → Nairobi
- CAI → Cairo
- JNB → Johannesburg

Type:
- Categorical

---

## 6. destination
Destination airport.

Always:
- JED

Type:
- Constant categorical

---

## 7. cargo_type

| Value | Meaning |
|---|---|
| General | Standard commercial cargo |
| Perishable | Temperature-sensitive goods |
| Valuable | High-value cargo |
| Dangerous | Hazardous materials |
| Heavy | Oversized or high-weight cargo |
| Pharmaceutical | Medical and healthcare shipments |

Type:
- Categorical

---

## 8. cargo_weight_kg
Shipment weight in kilograms.

Type:
- Numeric

Typical Range:
- 10 kg to 15,000 kg

---

## 9. cost_sar
Estimated transportation cost in Saudi Riyal (SAR).

Factors influencing cost:
- Cargo weight
- Distance
- Cargo type
- Priority
- Number of connections
- Special handling requirements

Type:
- Numeric

---

## 10. total_transit_time_hours
Total transit duration including:
- Flight time
- Ground handling
- Connection waiting time

Type:
- Numeric

Typical Range:
- 4 hours to 42 hours

---

## 11. capacity_available_kg
Available cargo space across the route.

Type:
- Numeric

Logic:
- Must usually exceed cargo weight for feasible routing

---

## 12. reliability_score
Operational reliability probability between `0.0` and `1.0`.

Higher values indicate:
- Better on-time performance
- Lower disruption risk
- Better operational consistency

Type:
- Numeric

---

## 13. num_connections
Number of transshipments.

| Value | Meaning |
|---|---|
| 0 | Direct route |
| 1 | Single connection |
| 2 | Double connection |

Operational Impact:
- More connections increase transit time
- More connections reduce reliability
- More connections reduce cost

---

## 14. priority

| Value | Meaning |
|---|---|
| Express | Fastest routing preference |
| Standard | Balanced routing |
| Economy | Lowest cost routing |

Type:
- Categorical

---

## 15. airline
Operating airline for the route.

Examples:
- Saudia Cargo
- Qatar Airways Cargo
- Emirates SkyCargo
- Turkish Cargo
- Lufthansa Cargo
- Etihad Cargo

Type:
- Categorical

---

## 16. distance_km
Approximate route distance from origin to Jeddah.

Type:
- Numeric

Typical Range:
- 850 km to 13,500 km

---

## 17. weather_risk_score
Weather disruption probability between `0.0` and `1.0`.

Higher values indicate:
- Greater operational risk
- Delay likelihood
- Reduced reliability

Type:
- Numeric

---

## 18. season

| Value | Meaning |
|---|---|
| Summer | June to August |
| Winter | December to February |
| Monsoon | September to November |
| Spring | March to May |

Type:
- Categorical

---

## 19. load_factor
Cargo utilization ratio between `0.0` and `1.0`.

Higher values indicate:
- Flights closer to full capacity
- Reduced operational flexibility

Operational Impact:
- High load factor reduces available capacity
- High load factor may reduce optimization score

---

## 20. shc_code (Special Handling Code)

| Code | Meaning |
|---|---|
| GEN | General cargo |
| PER | Perishable cargo |
| ICE | Cargo requiring ice cooling |
| FRO | Frozen cargo |
| DGR | Dangerous goods |
| VAL | Valuable cargo |
| AVI | Live animals |
| ELI | Lithium ion batteries |
| ELM | Lithium metal batteries |
| CAO | Cargo aircraft only |
| HEA | Heavy cargo |

Type:
- Categorical

SHC codes are aligned with cargo type compatibility rules.

---

## 21. optimization_score (Target Variable)

Continuous target between `0.0` and `1.0`.

Higher values indicate more operationally optimal routes.

The score is generated using a weighted multi-factor optimization model.

---

# Optimization Score Generation Logic

The optimization score is generated using normalized weighted factors.

## Positive Contributors
- Lower transportation cost
- Lower transit time
- Higher reliability
- Higher excess capacity
- Lower weather risk
- Lower load factor
- Fewer transshipments

## Weighted Contribution Structure

| Feature Group | Approximate Weight |
|---|---|
| Cost efficiency | 24% |
| Transit time efficiency | 24% |
| Reliability | 22% |
| Weather risk | 10% |
| Connection penalty | 8% |
| Capacity adequacy | 7% |
| Load factor efficiency | 5% |

Additional bonuses:
- Express priority routes receive small boosts
- Pharmaceutical and perishable cargo receive stricter optimization emphasis
- Infeasible capacity conditions receive severe penalties

---

# Operational Relationships Enforced

## Distance vs Time
Longer routes generally:
- Increase transit time
- Increase operational cost

## Connection Logic
### Direct Routes
- Faster
- More reliable
- More expensive

### Multi-connection Routes
- Slower
- Less reliable
- Cheaper

## Weather Logic
Higher weather risk:
- Reduces reliability
- Reduces optimization score

## Capacity Logic
Higher load factor:
- Reduces effective available capacity

## SHC Compatibility
Special handling cargo:
- Increases cost
- Requires stricter operational feasibility

---

# Data Quality

The dataset is intentionally designed to:
- Contain no null values
- Contain no duplicate rows
- Preserve operational consistency
- Support ML training and explainability
- Simulate realistic airline cargo operations

---

# Intended ML Use Cases

This dataset can be used for:
- Regression models
- Route ranking systems
- Multi-objective optimization
- Explainable AI dashboards
- Operational simulation
- Commercial decision support

## 🧮 Mathematical Foundation of the Optimization Score

Unlike simple linear regression, this system utilizes an **XGBoost Regressor**, which calculates predictions using an ensemble of decision trees. However, the final optimization score can be broken down into a linear, explainable mathematical formula using Additive Feature Contributions (similar to SHAP values).

### 1. The Core XGBoost Equation
The final prediction for any given route is the sum of the outputs from all individual decision trees in the model:

$$\hat{y}_i = \sum_{k=1}^{K} f_k(x_i)$$

Where:
* **$\hat{y}_i$** = The final predicted Optimization Score for route $i$.
* **$K$** = The total number of decision trees in the model (e.g., 100).
* **$f_k$** = A specific decision tree evaluating the route's parameters.
* **$x_i$** = The vector of input features (Cost, Transit Time, Reliability, etc.).

### 2. The Explainable Feature Formula
For human interpretability and operational auditing, the system translates the tree ensemble into a linear additive formula. The score of any route is calculated as the **Base Score** plus the sum of the individual **Feature Impacts**:

$$Score = Base\_Score + \sum_{j=1}^{N} Impact(Feature_j)$$

Expanded out for the primary routing metrics, the formula is:

$$Score = 0.5000 + \Delta_{Cost} + \Delta_{Time} + \Delta_{Reliability} + \Delta_{Capacity} + \Delta_{Risk}$$

* **$Base\_Score$ (0.5000):** The global average score of all routes in the training dataset before any specific details are known.
* **$\Delta$ (Delta / Impact):** The mathematical penalty (negative value) or bonus (positive value) applied by the AI based on that specific feature's value.

### 3. Example Calculation Walkthrough
Consider a route with the following inputs:
* **Cost:** 15,000 SAR
* **Transit Time:** 15.0 Hours
* **Reliability:** 0.850

The AI evaluates these facts against the historical baseline and applies the math:

1. **Base Score:** `0.5000`
2. **Cost Impact:** 15,000 SAR is slightly expensive for this cargo weight $\rightarrow$ `- 0.0850`
3. **Time Impact:** 15 hours is a highly efficient transit time $\rightarrow$ `+ 0.1200`
4. **Reliability Impact:** 0.850 is a strong, safe carrier metric $\rightarrow$ `+ 0.0650`
5. **Other Impacts (Weather, Load, etc.):** $\rightarrow$ `- 0.0200`

**Final Score Calculation:**

$$Score = Base + (W_{rel} \times Rel) + (W_{cap} \times Cap) - (W_{cost} \times Cost_{penalty}) - (W_{time} \times Time_{penalty})$$

**Verdict:** `0.5800` (Proceed With Caution). The excellent transit time (+0.12) is being dragged down by the expensive cost (-0.085), pushing it out of the "Highly Recommended" (>0.70) tier.
