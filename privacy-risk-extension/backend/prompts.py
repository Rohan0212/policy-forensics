def build_prompt(clause_text):
    return f"""
You are a privacy compliance analyst.

Analyze the following clause and return JSON:

{{
  "mentions_biometric_data": true/false,
  "mentions_location_tracking": true/false,
  "mentions_camera_or_microphone": true/false,
  "data_retention_policy_present": true/false,
  "retention_duration_specified": true/false,
  "risk_level": "low/medium/high",
  "risk_reason": "brief explanation"
}}

Clause:
\"\"\"{clause_text}\"\"\"
"""

