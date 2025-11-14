# Web Pixel Detection Keywords - Quick Reference Guide

## For Implementation in Notification System

---

## High-Confidence Detection Keywords

These keywords/phrases should trigger immediate notification with HIGH confidence:

### Single Keyword Matches
```
pixel validation
pixel firing
pixel not firing
pixels not firing
conversion pixel
tracking pixel
web pixel
website pixel
universal tag
universal tags
pixel implementation
pixel troubleshooting
pixel setup
confirmation page pixel
revenue pixel
user sync pixel
piggyback pixel
```

### Context-Dependent Matches
When "pixel" appears WITH any of these context words:
```
pixel + confirmation
pixel + conversion
pixel + firing
pixel + tracking
pixel + website
pixel + validation
pixel + troubleshooting
pixel + implementation
pixel + code
pixel + piggyback
pixel + appending
```

---

## Medium-Confidence Detection Patterns

These combinations suggest pixel-related content but need additional validation:

### Pattern 1: Tracking + Action
```
(tracking OR tag OR tags)
AND
(implement OR implementation OR install OR setup OR deploy OR add OR append OR create)
```

Examples:
- "implement tracking code"
- "setup tracking tag"
- "add tracking to website"

### Pattern 2: Web + Code
```
(javascript OR js OR web code OR website)
AND
(code OR snippet OR implementation OR integration OR embed)
```

Examples:
- "javascript code implementation"
- "website integration code"
- "web snippet embed"

### Pattern 3: Conversion + Tracking
```
conversion
AND
(tracking OR code OR tag OR validation OR data)
```

Examples:
- "conversion tracking code"
- "conversion data validation"
- "conversion tag setup"

---

## Exclusion Patterns (Avoid False Positives)

These patterns should EXCLUDE a ticket from pixel detection:

### High-Confidence Exclusions
```
"acr data"
"acr report"
"acr monitoring"
"o&o monitoring"
"delivery report only"
"grant access"
"access request"
"permission request"
"request access"
"monitoring alert"
"snowflake access"
"udw access"
```

### Context-Based Exclusions
Exclude if these appear WITHOUT pixel keywords:
```
"warehouse creation"
"database access"
"role assignment"
"keycloak"
"authentication"
```

---

## Common Phrase Library

### Problem Descriptions
```
"pixel is not firing"
"pixel not working"
"not seeing pixels"
"0 conversions"
"no conversions"
"conversion data not showing"
"pixel showing zero"
"discrepancy between"
"not tracking correctly"
"validation request"
```

### Implementation Requests
```
"need to implement"
"set up pixel"
"install tracking"
"append pixel"
"add pixel to"
"piggyback into"
"integrate pixel"
"deploy tracking code"
```

### Validation/Testing
```
"validate pixel"
"verify tag"
"check if firing"
"test pixel"
"troubleshoot pixel"
"debug tracking"
```

### Technical Terms
```
"universal tag"
"conversion group"
"u-variable"
"custom variable"
"confirmation page"
"purchase page"
"thank you page"
"revenue tracking"
"user sync"
"macro"
```

---

## Priority-Based Rules

### Rule 1: ALWAYS Notify (High Priority)
If ticket contains:
- "pixel" + (validation OR firing OR "not firing" OR troubleshooting)
- "universal tag" + any action keyword
- Priority = High/Critical AND contains "pixel"

### Rule 2: NOTIFY (Standard Priority)
If ticket contains:
- "pixel" in any context (except exclusions)
- "conversion" + "tracking" + implementation keywords
- "tracking pixel" or "conversion pixel"

### Rule 3: DIGEST/REVIEW (Low Priority)
If ticket contains:
- Medium-confidence patterns only
- Priority = Low
- Generic tracking keywords without specifics

### Rule 4: SKIP
If ticket contains:
- Any exclusion pattern
- No pixel-related keywords
- Generic support requests

---

## Detection Confidence Scoring

### High Confidence (90-100%)
- Contains "pixel" in summary
- Contains any high-confidence phrase
- Multiple pixel-related keywords
- **Action:** Immediate notification

### Medium Confidence (60-89%)
- Contains combination patterns
- Context-dependent matches
- Single generic tracking keyword
- **Action:** Standard notification or daily digest

### Low Confidence (30-59%)
- Weak pattern matches
- Distant keyword relationships
- Generic terms only
- **Action:** Log for review, no notification

### No Confidence (0-29%)
- No relevant keywords
- Contains exclusion patterns
- **Action:** Ignore

---

## Real-World Examples with Scoring

### Example 1: "Ministry of Supply Pixel Validation Request"
- **Score:** HIGH (95%)
- **Matched:** "pixel", "validation"
- **Action:** Immediate notification
- **Reasoning:** Direct pixel reference + action keyword

### Example 2: "Pixels not firing in DSP"
- **Score:** HIGH (100%)
- **Matched:** "pixels", "not firing"
- **Action:** Immediate notification
- **Reasoning:** Classic pixel problem description

### Example 3: "Need verification on universal tags"
- **Score:** HIGH (90%)
- **Matched:** "universal tags", "verification"
- **Action:** Immediate notification
- **Reasoning:** Samsung-specific tracking term

### Example 4: "Implement tracking code for website"
- **Score:** MEDIUM (75%)
- **Matched:** tracking + implement + website
- **Action:** Standard notification
- **Reasoning:** Combination pattern, likely pixel-related

### Example 5: "Planning Module Usage Report"
- **Score:** LOW (40%)
- **Matched:** Generic "implementation" and "tracking"
- **Action:** Review/Skip
- **Reasoning:** Not pixel-specific, generic terms

### Example 6: "Grant UDW access for user"
- **Score:** EXCLUDED (0%)
- **Matched:** Exclusion pattern "grant access"
- **Action:** Skip
- **Reasoning:** Access request, not pixel-related

---

## JQL Queries for Different Confidence Levels

### High Confidence Query
```jql
project = PS
AND resolution = Unresolved
AND (
    summary ~ "pixel"
    OR summary ~ "universal tag"
    OR summary ~ "conversion pixel"
    OR summary ~ "tracking pixel"
    OR description ~ "pixel validation"
    OR description ~ "pixel firing"
    OR description ~ "pixel not firing"
)
AND NOT (
    summary ~ "ACR"
    OR summary ~ "access"
    OR summary ~ "monitoring"
)
ORDER BY created DESC
```

### Medium Confidence Query
```jql
project = PS
AND resolution = Unresolved
AND (
    (summary ~ "tracking" AND summary ~ "implement")
    OR (summary ~ "conversion" AND summary ~ "tracking")
    OR (summary ~ "javascript" AND summary ~ "code")
    OR (summary ~ "website" AND summary ~ "integration")
)
AND NOT (
    summary ~ "ACR"
    OR summary ~ "access request"
    OR summary ~ "delivery report"
)
ORDER BY created DESC
```

---

## Implementation Checklist

### Detection Function Must:
- [ ] Check for high-confidence keywords first
- [ ] Apply exclusion patterns before matching
- [ ] Support case-insensitive matching
- [ ] Handle summary AND description text
- [ ] Return confidence score
- [ ] Return matched patterns for debugging
- [ ] Support priority-based filtering

### Notification System Must:
- [ ] Immediate notify for HIGH confidence + HIGH priority
- [ ] Standard notify for HIGH confidence + MEDIUM priority
- [ ] Daily digest for MEDIUM confidence matches
- [ ] Skip LOW confidence and excluded tickets
- [ ] Include matched patterns in notification
- [ ] Provide ticket URL
- [ ] Show description preview

### Testing Must Cover:
- [ ] All 16 real ticket examples
- [ ] Edge cases with exclusion patterns
- [ ] Combination pattern matches
- [ ] False positive scenarios
- [ ] Priority level handling
- [ ] Multiple keyword matches

---

## Tuning Guidelines

### If Too Many False Positives:
1. Strengthen exclusion patterns
2. Require more keywords for medium confidence
3. Add context validation for generic terms
4. Increase confidence threshold for notifications

### If Missing Real Pixel Tickets:
1. Review missed tickets for new patterns
2. Add new keyword variations
3. Lower confidence threshold
4. Expand combination patterns

### Regular Maintenance:
1. Review false positives weekly
2. Add new patterns from missed tickets
3. Update exclusion list as needed
4. Adjust confidence scores based on accuracy
5. Collect feedback from Louis on notification quality

---

## Quick Decision Tree

```
START: New Jira Ticket Created
  |
  ├─> Contains exclusion pattern?
  |     └─> YES: SKIP
  |     └─> NO: Continue
  |
  ├─> Contains "pixel" keyword?
  |     └─> YES:
  |         ├─> In summary? → HIGH confidence → NOTIFY
  |         └─> In description with context? → HIGH confidence → NOTIFY
  |     └─> NO: Continue
  |
  ├─> Contains high-confidence phrase?
  |     └─> YES: HIGH confidence → NOTIFY
  |     └─> NO: Continue
  |
  ├─> Matches combination pattern?
  |     └─> YES: MEDIUM confidence
  |         ├─> Priority = High/Critical? → NOTIFY
  |         └─> Priority = Medium/Low? → DIGEST
  |     └─> NO: SKIP
  |
  └─> END
```

---

## Contact & Feedback

When implementing this detection logic, consider:

1. **Start Conservative:** Begin with HIGH confidence only, then expand
2. **Monitor Accuracy:** Track precision and recall over first month
3. **Iterate Quickly:** Add new patterns as they're discovered
4. **User Feedback:** Get Louis's input on notification quality
5. **Document Changes:** Keep this reference updated with new patterns

---

**Last Updated:** 2025-10-22
**Based On:** 16 real PS project tickets from April-October 2025
**Accuracy Target:** 90%+ precision, 95%+ recall on pixel tickets
