from jinja2 import Template

PDF_TEMPLATE = """
Research Report

Document: {{ document_id }}
Session ID: {{ session_id }}
Generated: {{ timestamp }}

{% for question in questions %}
Question {{ loop.index }}: {{ question.query }}
-------------------------------------------

Document Analysis:
{{ question.rag_response }}

Academic Research:
{% for paper in question.arxiv_results %}
* {{ paper.title }}
  Published: {{ paper.published }}
  Summary: {{ paper.summary[:200] }}...
{% endfor %}

Web Research:
{% for result in question.web_results %}
* {{ result.title }}
  {{ result.snippet }}
{% endfor %}

Synthesis:
{{ question.combined_analysis }}

{% endfor %}
"""

CODELABS_TEMPLATE = """
{
  "title": "Research on {{ document_id }}",
  "description": "Research findings and analysis",
  "steps": [
    {% for question in questions %}
    {
      "title": "Question {{ loop.index }}: {{ question.query }}",
      "duration": "5:00",
      "content": {{ question.content | tojson }}
    }{% if not loop.last %},{% endif %}
    {% endfor %}
  ]
}
""" 