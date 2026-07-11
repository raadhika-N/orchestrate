# Evaluation Report

Generated: 2026-07-10 23:30:07
Total claims evaluated: 20

---

## Overall Accuracy

**Primary metric (claim_status): 65.0%**

| Field | Accuracy | Correct | Total |
|---|---|---|---|
| claim_status | 65.0% | 13 | 20 |
| issue_type | 55.0% | 11 | 20 |
| object_part | 80.0% | 16 | 20 |
| severity | 50.0% | 10 | 20 |
| evidence_standard_met | 75.0% | 15 | 20 |
| valid_image | 75.0% | 15 | 20 |

---

## Mismatch Analysis

### claim_status — 7 mismatches

| Row | User ID | Expected | Predicted |
|---|---|---|---|
| 0 | user_001 | supported | contradicted |
| 1 | user_002 | supported | contradicted |
| 4 | user_005 | contradicted | supported |
| 13 | user_020 | contradicted | supported |
| 17 | user_032 | not_enough_information | supported |
| 18 | user_033 | contradicted | not_enough_information |
| 19 | user_034 | contradicted | supported |

### issue_type — 9 mismatches

| Row | User ID | Expected | Predicted |
|---|---|---|---|
| 2 | user_004 | crack | glass_shatter |
| 3 | user_007 | broken_part | crack |
| 4 | user_005 | scratch | dent |
| 7 | user_008 | broken_part | unknown |
| 8 | user_009 | crack | glass_shatter |
| 12 | user_018 | crack | glass_shatter |
| 13 | user_020 | none | scratch |
| 17 | user_032 | unknown | missing_part |
| 19 | user_034 | none | torn_packaging |

### object_part — 4 mismatches

| Row | User ID | Expected | Predicted |
|---|---|---|---|
| 5 | user_006 | headlight | unknown |
| 7 | user_008 | front_bumper | unknown |
| 15 | user_030 | seal | package_side |
| 16 | user_031 | package_side | box |

### severity — 10 mismatches

| Row | User ID | Expected | Predicted |
|---|---|---|---|
| 0 | user_001 | medium | high |
| 2 | user_004 | medium | high |
| 7 | user_008 | high | unknown |
| 8 | user_009 | medium | high |
| 12 | user_018 | medium | high |
| 13 | user_020 | none | low |
| 14 | user_015 | medium | low |
| 17 | user_032 | unknown | medium |
| 18 | user_033 | low | unknown |
| 19 | user_034 | none | medium |

### evidence_standard_met — 5 mismatches

| Row | User ID | Expected | Predicted |
|---|---|---|---|
| 0 | user_001 | true | false |
| 1 | user_002 | true | false |
| 7 | user_008 | true | false |
| 17 | user_032 | false | true |
| 18 | user_033 | true | false |

### valid_image — 5 mismatches

| Row | User ID | Expected | Predicted |
|---|---|---|---|
| 0 | user_001 | true | false |
| 1 | user_002 | true | false |
| 5 | user_006 | true | false |
| 17 | user_032 | false | true |
| 18 | user_033 | true | false |

---

## Operational Analysis

- Model calls made: approximately 20 (minus cache hits)
- Caching: enabled — reruns cost zero additional API calls
- Rate limiting: 1 second delay between calls
- Safe fallback: failed calls return not_enough_information
- Retry strategy: 3 attempts with exponential backoff

## Cost Estimate

- Groq Llama 4 Scout: free tier
- Estimated tokens: ~46,000
- Cost: $0.00 (free tier)
