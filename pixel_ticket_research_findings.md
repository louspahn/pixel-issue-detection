# Web Pixel-Related Jira Ticket Research Findings
## PS Project Analysis (Last 6 Months)

**Date:** 2025-10-22
**Project:** PS (Platform Support)
**Time Period:** April 25, 2025 - October 22, 2025
**Total Pixel-Related Tickets Found:** 16

---

## Executive Summary

This research analyzed Jira tickets in the PS project to understand patterns in web pixel-related issues. The analysis identified 16 pixel-specific tickets over the last 6 months, revealing clear patterns in how these tickets are structured, prioritized, and categorized.

**Key Findings:**
- 93.8% of pixel-related tickets have Medium priority
- 100% are submitted as "Submit a request or incident" issue type
- Most common keywords: "pixel", "conversion", "tracking", "website"
- Primary issue categories: Pixel validation, conversion tracking, pixel firing issues

---

## 1. Keyword Frequency Analysis

### Primary Keywords Found in Pixel Tickets

| Keyword | Frequency | Usage Context |
|---------|-----------|---------------|
| pixel | 14 tickets | Primary identifier for web pixel tickets |
| conversion | 8 tickets | Related to conversion tracking and pixel validation |
| tracking | 4 tickets | Associated with tracking implementation and troubleshooting |
| website | 3 tickets | Context for where pixels are implemented |
| data | 3 tickets | Related to pixel data collection and reporting |
| code | 2 tickets | Pixel code implementation requests |
| tag | 2 tickets | Used interchangeably with "pixel" in some contexts |

### Most Common Words in Ticket Summaries

| Word | Frequency |
|------|-----------|
| pixel | 5 |
| they | 5 |
| data | 3 |
| need | 3 |
| request | 2 |
| seeing | 2 |
| pixels | 2 |
| conversion | 2 |
| screenshots | 2 |
| website | 2 |

---

## 2. Ticket Characteristics

### Priority Distribution

| Priority | Count | Percentage |
|----------|-------|------------|
| Medium | 15 | 93.8% |
| High | 1 | 6.2% |
| Critical | 0 | 0% |
| Low | 0 | 0% |

**Key Finding:** Almost all pixel-related tickets are assigned Medium priority, with only rare High priority cases.

### Status Distribution

| Status | Count | Percentage |
|--------|-------|------------|
| Closed | 15 | 93.8% |
| Canceled | 1 | 6.2% |

**Key Finding:** All analyzed tickets are resolved, indicating good ticket closure practices.

### Issue Type Distribution

| Issue Type | Count | Percentage |
|------------|-------|------------|
| Submit a request or incident | 16 | 100% |

**Key Finding:** All pixel tickets come through the request/incident channel.

---

## 3. Common Pixel Issue Categories

Based on analysis of ticket descriptions, pixel-related tickets fall into these categories:

### A. Pixel Validation & Troubleshooting (Most Common)
- **Examples:**
  - PS-9534: "Ministry of Supply Pixel Validation Request" - Pixel showing 0 conversions
  - PS-9155: "Pixels not firing in DSP though appearing in Adform"
  - PS-9074: "Web Conversion - Pixel Data Troubleshooting"

- **Common Phrases:**
  - "pixel validation"
  - "pixel not firing"
  - "not seeing pixels"
  - "0 conversions"
  - "pixel troubleshooting"

### B. Conversion Tracking Issues
- **Examples:**
  - PS-8768: "No conversions pulling in"
  - PS-8297: "Website Pixel Conversion Data Not Showing"

- **Common Phrases:**
  - "conversion data"
  - "not showing conversions"
  - "conversion tracking"
  - "revenue tracking"

### C. Pixel Implementation & Setup
- **Examples:**
  - PS-8971: "Verification on universal tags"
  - PS-8537: "U-Variable ingestion in website pixel"
  - PS-8696: "Appending a pixel for line items"

- **Common Phrases:**
  - "pixel implementation"
  - "tag verification"
  - "universal tags"
  - "appending a pixel"
  - "custom variables"

### D. Third-Party Integration
- **Examples:**
  - PS-9124: "FW User Sync Pixels Change"
  - PS-7945: "Xandr GDPR updated macro"

- **Common Phrases:**
  - "user sync pixel"
  - "third-party pixel"
  - "piggyback"
  - "macro"

---

## 4. Sample Ticket Analysis

### High-Priority Example
**PS-8073 - Porter Airlines CA - Pixel Inquiry (High Priority)**
- **Issue:** Confirmation page pixel not firing correctly
- **Key Phrases:** "pixel on Confirmation page", "not firing correctly", "screenshot"
- **Detection Keywords:** pixel, confirmation, firing, not working

### Typical Medium-Priority Examples

**PS-9534 - Ad Manager Ministry of Supply Pixel Validation Request**
- **Issue:** Pixel showing 0 conversions, needs validation
- **Key Phrases:** "pixel validation", "0 conversions", "validate pixel is firing"
- **Detection Keywords:** pixel, validation, conversion, firing

**PS-9155 - Pixels not firing in DSP**
- **Issue:** Pixels appearing in Adform but not in DSP
- **Key Phrases:** "pixels fire in DSP", "piggybacked in Adform"
- **Detection Keywords:** pixel, fire, DSP, piggyback

**PS-9074 - Web Conversion - Pixel Data Troubleshooting**
- **Issue:** Discrepancy between Samsung pixel and client's user count
- **Key Phrases:** "pixel data troubleshooting", "confirmation page data"
- **Detection Keywords:** pixel, web conversion, troubleshooting, data

---

## 5. Recommended Detection Logic

### Primary Detection Keywords (High Confidence)

These keywords alone indicate a pixel-related ticket:

1. **"pixel"** - Most reliable indicator (found in 14/16 tickets)
2. **"tracking pixel"** - Specific pixel reference
3. **"conversion pixel"** - Specific pixel type
4. **"web pixel"** - Explicit web pixel reference
5. **"website pixel"** - Explicit web pixel reference
6. **"universal tag"** - Samsung's tracking implementation

### Combination Patterns (Medium Confidence)

These combinations suggest pixel-related content:

1. **Tracking + Implementation:**
   - ("tracking" OR "tag") AND ("implement" OR "install" OR "setup" OR "deploy")

2. **Web Integration:**
   - ("javascript" OR "js") AND ("code" OR "snippet")
   - ("website" OR "web") AND ("integration" OR "embed")

3. **Validation + Conversion:**
   - "validation" AND "conversion"
   - "firing" AND ("pixel" OR "tag")

### Context Phrases (High Value)

These specific phrases are strong indicators:

- "pixel validation"
- "pixel firing"
- "pixel not firing"
- "conversion tracking"
- "universal tag"
- "tracking code"
- "pixel implementation"
- "piggyback pixel"
- "user sync pixel"
- "confirmation page pixel"
- "0 conversions"
- "pixel troubleshooting"

### Exclusion Patterns (Reduce False Positives)

Exclude tickets containing these terms to avoid misclassification:

- **"ACR"** - Automatic Content Recognition (TV-related, not web pixels)
- **"delivery report"** - Reporting tickets, not pixel implementation
- **"access request"** / **"permission"** / **"grant access"** - Access management tickets
- **"monitoring"** / **"alert"** - System monitoring tickets
- **"UDW"** / **"Snowflake"** - Data warehouse tickets (unless combined with pixel keywords)

---

## 6. Recommended Implementation

### Detection Function (Python)

```python
def is_pixel_related_ticket(summary, description):
    """
    Determine if a Jira ticket is related to web pixels.

    Args:
        summary: Ticket summary/title
        description: Ticket description text

    Returns:
        tuple: (is_pixel_related: bool, confidence: str, matched_patterns: list)
    """
    text = (summary + ' ' + description).lower()
    matched_patterns = []

    # Exclusion patterns - check first
    exclusions = [
        'acr data', 'acr report', 'acr monitoring',
        'delivery report only',
        'grant access', 'access request', 'permission request',
        'monitoring alert', 'o&o monitoring'
    ]

    for exclusion in exclusions:
        if exclusion in text:
            return (False, 'excluded', [f'excluded: {exclusion}'])

    # Primary indicators (HIGH confidence)
    primary_keywords = [
        'pixel validation',
        'pixel firing',
        'pixel not firing',
        'conversion pixel',
        'tracking pixel',
        'web pixel',
        'website pixel',
        'universal tag',
        'pixel implementation',
        'pixel troubleshooting'
    ]

    for keyword in primary_keywords:
        if keyword in text:
            matched_patterns.append(f'primary: {keyword}')

    if matched_patterns:
        return (True, 'high', matched_patterns)

    # Single keyword detection (HIGH confidence)
    if 'pixel' in text:
        # Check if it's in a relevant context
        pixel_contexts = [
            'confirmation page', 'website', 'web', 'conversion',
            'firing', 'tracking', 'code', 'implementation',
            'validation', 'troubleshooting', 'piggyback'
        ]

        if any(context in text for context in pixel_contexts):
            matched_patterns.append('primary: pixel (in context)')
            return (True, 'high', matched_patterns)

    # Combination patterns (MEDIUM confidence)
    tracking_keywords = ['tracking', 'tag', 'tags']
    action_keywords = ['implement', 'implementation', 'install', 'setup',
                       'deploy', 'add', 'append', 'create']

    has_tracking = any(k in text for k in tracking_keywords)
    has_action = any(k in text for k in action_keywords)

    if has_tracking and has_action:
        matched_patterns.append('combination: tracking + action')
        return (True, 'medium', matched_patterns)

    # JavaScript/web integration patterns (MEDIUM confidence)
    if ('javascript' in text or 'js code' in text or 'js tag' in text):
        if any(word in text for word in ['code', 'snippet', 'implementation', 'integration']):
            matched_patterns.append('combination: javascript + code')
            return (True, 'medium', matched_patterns)

    # Website integration patterns (MEDIUM confidence)
    if ('website' in text or 'web page' in text):
        if any(word in text for word in ['integration', 'embed', 'code', 'snippet']):
            matched_patterns.append('combination: website + integration')
            return (True, 'medium', matched_patterns)

    # Conversion tracking patterns (MEDIUM confidence)
    if 'conversion' in text:
        if any(word in text for word in ['tracking', 'code', 'tag', 'validation']):
            matched_patterns.append('combination: conversion + tracking')
            return (True, 'medium', matched_patterns)

    return (False, 'none', matched_patterns)


def should_notify_about_ticket(summary, description, priority='Medium'):
    """
    Determine if a ticket should trigger a notification.

    Args:
        summary: Ticket summary
        description: Ticket description
        priority: Ticket priority level

    Returns:
        tuple: (should_notify: bool, reason: str)
    """
    is_pixel, confidence, patterns = is_pixel_related_ticket(summary, description)

    if not is_pixel:
        return (False, 'Not pixel-related')

    # Always notify on high confidence matches
    if confidence == 'high':
        return (True, f'High confidence pixel ticket: {", ".join(patterns)}')

    # For medium confidence, consider priority
    if confidence == 'medium':
        if priority in ['High', 'Highest', 'Critical']:
            return (True, f'Medium confidence + high priority: {", ".join(patterns)}')
        else:
            # Could make this configurable
            return (True, f'Medium confidence pixel ticket: {", ".join(patterns)}')

    return (False, 'Low confidence match')
```

### JQL Query Approach

For proactive monitoring, use this JQL query:

```jql
project = PS
AND resolution = Unresolved
AND created >= -7d
AND (
    summary ~ "pixel"
    OR summary ~ "tracking"
    OR summary ~ "conversion"
    OR description ~ "pixel"
    OR description ~ "universal tag"
)
AND NOT (
    summary ~ "ACR"
    OR summary ~ "delivery report"
    OR summary ~ "access request"
)
ORDER BY created DESC
```

---

## 7. Testing the Detection Logic

### Test Cases

#### Should Detect (True Positives)

1. "Ministry of Supply Pixel Validation Request"
   - Contains: "pixel", "validation"
   - Expected: HIGH confidence

2. "Pixels not firing in DSP though appearing in Adform"
   - Contains: "pixels", "firing"
   - Expected: HIGH confidence

3. "Need verification on universal tags"
   - Contains: "universal tags", "verification"
   - Expected: HIGH confidence

4. "Implement tracking code for website"
   - Contains: "implement", "tracking", "code", "website"
   - Expected: MEDIUM confidence

#### Should Not Detect (True Negatives)

1. "O&O Monitoring 10/22/2025"
   - Contains: monitoring alert exclusion
   - Expected: EXCLUDED

2. "Grant UDW access for user"
   - Contains: access request exclusion
   - Expected: EXCLUDED

3. "ACR Data missing for campaign"
   - Contains: ACR exclusion
   - Expected: EXCLUDED

4. "Pull delivery report for campaign"
   - Contains: delivery report (without pixel context)
   - Expected: FALSE

---

## 8. Implementation Recommendations

### Notification Triggers

**Immediate Notification (High Priority):**
- Any ticket with "pixel" + HIGH priority
- Tickets matching primary keyword phrases
- New pixel implementation requests

**Daily Digest (Medium Priority):**
- Medium confidence pixel tickets
- Tracking + implementation combinations
- Conversion tracking issues

**No Notification:**
- Excluded patterns (ACR, access requests, monitoring)
- Low confidence matches
- Resolved tickets

### Message Template

When a pixel-related ticket is detected, send a notification like:

```
New Pixel-Related Ticket Detected

Ticket: PS-XXXX
Priority: [High/Medium]
Summary: [Ticket Summary]
Confidence: [High/Medium]
Matched Patterns: [List of matched keywords/patterns]

Description Preview:
[First 200 characters of description]

URL: https://adgear.atlassian.net/browse/PS-XXXX

---
This ticket was automatically identified as pixel-related.
Confidence: [High/Medium] based on [matching criteria]
```

---

## 9. Key Insights for Louis

Based on your role and these ticket patterns:

### What to Watch For:

1. **Pixel Validation Requests** - Most common type, usually straightforward
2. **"Not Firing" Issues** - Requires technical debugging, often urgent
3. **Universal Tag Questions** - Samsung-specific implementation
4. **Third-Party Integration** - May require coordination with partners
5. **Conversion Discrepancies** - Needs data analysis and validation

### Communication Patterns:

- Clients often include **screenshots** - be ready to review
- "0 conversions" is a common complaint - check pixel implementation
- Comparison with other platforms (Adform, Google) is common
- Validation requests need quick turnaround

### Escalation Indicators:

- **HIGH Priority** pixel tickets (rare but important)
- Multiple tickets about same pixel/client
- Revenue tracking issues (business-critical)
- Launch date mentioned ("going live TODAY")

---

## Conclusion

This analysis provides a solid foundation for building an automated notification system for web pixel-related tickets. The detection logic should focus on:

1. **Primary keyword "pixel"** with context validation
2. **Combination patterns** for tracking + implementation
3. **Exclusion rules** to reduce false positives
4. **Confidence scoring** to prioritize notifications

With 16 pixel-related tickets over 6 months (approximately 3 per month), this represents a manageable volume that would benefit from automated detection and routing.
