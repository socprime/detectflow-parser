# Supported Sigma Rules

This document describes which Sigma rule features are supported by Detect Flow and which are not. It applies to **Sigma detection rules** for single-event matching. Correlation rules (aggregations, thresholds, temporal correlation) are not supported.

---

## Supported Features

### Modifiers (field\|modifier)

Modifiers are parsed from the detection key after the first `|`. Only one **matching** modifier per field is allowed (`contains`, `startswith`, or `endswith`), or none for exact match. The **`all`** modifier can be combined with any of these and does not count as a second "command"; it only switches list logic from OR to AND.

| Modifier   | Supported | Effect |
|-----------|-----------|--------|
| **contains** | ✅ | Substring match (case-insensitive). Value can appear anywhere in the field. |
| **startswith** | ✅ | Field value starts with one of the given strings (case-insensitive). |
| **endswith** | ✅ | Field value ends with one of the given strings (case-insensitive). |
| **Exact match** (no modifier) | ✅ | A field with no modifier is exact match (case-insensitive). |
| **all** | ✅ | When combined with a command: all listed values must match (AND). Without `all`, any value matches (OR). |

**Examples:**

- `CommandLine|contains`: command line contains any of the values (OR).
- `CommandLine|contains|all`: command line contains all of the values (AND).
- `Image|endswith`: image path ends with any of the values.
- `TargetObject|startswith`: target object starts with any of the values.

**Unsupported modifiers** (per [Sigma Modifiers Appendix](https://sigmahq.io/sigma-specification/specification/sigma-appendix-modifiers.html)); any use causes the rule to be rejected:

- **Generic:** `exists`, `cased`, `neq`
- **String:** `windash`
- **Regular expression:** `re`
- **Encoding:** `base64`, `base64offset`, `utf16`, `utf16le`, `utf16be`, `wide`
- **Numeric:** `lt`, `lte`, `gt`, `gte`
- **Time:** `minute`, `hour`, `day`, `week`, `month`, `year`
- **IP:** `cidr`
- **Specific:** `expand`, `fieldref`

---

### Condition expressions

| Pattern | Supported | Notes |
|--------|-----------|--------|
| **condition: single name** | ✅ | e.g. `condition: selection` where `selection` is a detection identifier. |
| **condition: A and B** | ✅ | Logical AND of condition names. |
| **condition: A or B** | ✅ | Logical OR of condition names. |
| **condition: not A** | ✅ | Negation of a condition (or group). |
| **condition: all of selection\*** | ✅ | All of the detection items matching the pattern (e.g. `selection_*`). |
| **condition: 1 of selection\*** | ✅ | At least one of the detection items matching the pattern. |
| **condition: all of them** | ✅ | All detection items (except `condition` and keys starting with `_`). |
| **condition: 1 of them** | ✅ | At least one detection item. |
| **Nested ( … )** | ✅ | Parentheses for grouping (e.g. `(A and B) or C`). |


---

### Keywords search

A search-identifier whose value is a **list of strings** (keywords) is applied to the full log event and values are linked with OR (Sigma default behavior is case-insensitive matching).

**Example:**

```yaml
detection:
  keywords:
    - 'keyword1'
    - 'keyword2'
  condition: keywords
```

The rule triggers if the full event contains `keyword1` **or** `keyword2` (case-insensitive).



---

### Wildcards in values

| Feature | Supported | Notes |
|--------|-----------|--------|
| **Wildcards (exact match / no modifier)** | ✅ | Unescaped `*` (any characters) and `?` (one character) in values are converted to a full-string regex (`^...$`). |
| **Escaped wildcards** | ✅ | `\*` and `\?` are treated as literal characters. |
| **Wildcards with other modifiers** | ❌ | Wildcards are rejected when used with `contains`, `startswith`, or `endswith`. |


---

### Regex

| Feature | Supported | Notes |
|--------|-----------|--------|
| **Sigma `re` modifier** | ❌ | The Sigma `re` modifier (field\|re) is not supported. In Sigma, `re` allows values to be treated as PCRE regex and supports both single values and value lists; Detect Flow rejects any use of `re`. Use a field with no modifier and wildcards in the value for simple glob-style patterns instead. |
| **Wildcard→regex (no modifier)** | ✅ | Unescaped `*`/`?` in values (field with no modifier) are converted to full-string regex (`^...$`).


---

## Not Supported

### Correlation rules, aggregations, and functions

The [Sigma Correlation Rules Specification](https://sigmahq.io/sigma-specification/specification/sigma-correlation-rules-specification.html) defines a separate format for meta-rules that correlate multiple events. Those rules use:

- **Correlation types:** `event_count`, `value_count`, `temporal`, `temporal_ordered`, `value_sum`, `value_avg`, `value_percentile`
- **Aggregation conditions** on counts or values: `gt`, `gte`, `lt`, `lte`, `eq`, `neq` (e.g. “≥ 100 events in 1h”)
- **Grouping** (`group-by`), **time window** (`timespan`), **related rules** (`rules`), **field aliases** (`aliases`)

**Detect Flow does not support Sigma Correlation rules.** Only single-event Sigma (detection) rules are evaluated; no aggregations, count thresholds, or temporal correlation are applied.

