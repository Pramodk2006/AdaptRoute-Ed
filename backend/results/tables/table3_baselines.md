# Table 3: Baseline Comparison
| Configuration | Average Quality | Avg Latency (ms) | Average Reward | Lightweight Model Rate (%) |
|---|---|---|---|---|
| B1_Smallest | 0.847 | 3110.5 | 0.351 | 100.0% |
| B2_Strongest | 0.872 | 11279.5 | 0.333 | 0.0% |
| B3_ComplexityOnly | 0.857 | 5004.8 | 0.349 | 75.0% |
| B4_OriginalHeuristic | 0.847 | 3110.5 | 0.351 | 100.0% |
| B5_CapabilityHeuristic | 0.872 | 11279.5 | 0.333 | 0.0% |
| B6_CapabilityLinUCB | 0.872 | 11279.5 | 0.333 | 0.0% |
| FULL_AdaptRoute | 0.865 | 8256.8 | 0.342 | 38.9% |
| A2_NoCapabilityFilter | 0.859 | 7710.0 | 0.339 | 55.6% |
| A3_6DFeatures | 0.858 | 7275.6 | 0.344 | 50.0% |
| A4_StaticReward | 0.872 | 11279.5 | 0.917 | 0.0% |
| A5_NoEscalation | 0.872 | 11279.5 | 0.333 | 0.0% |
| A7_LinUCBNoFilterNoEscalation | 0.847 | 3110.5 | 0.351 | 100.0% |
| A8_NoTaskDependentReward | 0.872 | 11279.5 | 0.852 | 0.0% |
