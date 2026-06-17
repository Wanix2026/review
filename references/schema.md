# 缓存文件 JSON Schema

## manifest.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "version": { "type": "integer", "const": 2 },
    "created": { "type": "string", "format": "date-time" },
    "updated": { "type": "string", "format": "date-time" },
    "course_name": { "type": "string" },
    "files": {
      "type": "object",
      "patternProperties": {
        "^.+$": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "path": { "type": "string" },
            "ext": { "type": "string" },
            "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
            "size": { "type": "integer" },
            "status": {
              "type": "string",
              "enum": ["pending", "ok", "ok_ocr", "encrypted", "error", "skipped", "removed"]
            },
            "output": { "type": "string" },
            "pages": { "type": "integer" },
            "slides": { "type": "integer" },
            "chars": { "type": "integer" },
            "garbled_ratio": { "type": "number" },
            "warnings": {
              "type": "array",
              "items": { "type": "string" }
            },
            "error": { "type": "string" },
            "note": { "type": "string" },
            "fix_suggestion": { "type": "string" }
          },
          "required": ["name", "sha256", "status"]
        }
      }
    }
  },
  "required": ["version", "created", "files"]
}
```

## mapping.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "version": { "type": "integer", "const": 1 },
    "chapters": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "syllabus_chapter": { "type": "string" },
          "syllabus_number": { "type": "integer" },
          "hours_theory": { "type": "integer" },
          "hours_practice": { "type": "integer" },
          "mastery_level": {
            "type": "object",
            "properties": {
              "master": { "type": "array", "items": { "type": "string" } },
              "familiar": { "type": "array", "items": { "type": "string" } },
              "know": { "type": "array", "items": { "type": "string" } }
            }
          },
          "calendar_weeks": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "week": { "type": "integer" },
                "date": { "type": "string" },
                "topic": { "type": "string" },
                "hours": { "type": "integer" },
                "teacher": { "type": "string" }
              }
            }
          },
          "ppts": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "file": { "type": "string" },
                "slides": { "type": "integer" },
                "confidence": { "type": "number", "minimum": 0, "maximum": 100 },
                "auto_matched": { "type": "boolean" }
              }
            }
          },
          "status": {
            "type": "string",
            "enum": ["confirmed", "partial", "missing", "inconsistent", "new", "skipped"]
          },
          "notes": { "type": "string" }
        },
        "required": ["syllabus_chapter", "syllabus_number", "hours_theory", "hours_practice"]
      }
    }
  },
  "required": ["version", "chapters"]
}
```

## projects.json (全局)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "version": { "type": "integer", "const": 1 },
    "projects": {
      "type": "object",
      "patternProperties": {
        "^/.+$": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "last_processed": { "type": "string", "format": "date-time" },
            "type": { "type": "string", "enum": ["考试课", "考查课"] },
            "has_question_types": { "type": "boolean" },
            "question_types": { "type": "object" },
            "cache_version": { "type": "integer" },
            "extract_count": { "type": "integer" },
            "gap_count": { "type": "integer" }
          },
          "required": ["name", "last_processed"]
        }
      }
    }
  },
  "required": ["version", "projects"]
}
```
