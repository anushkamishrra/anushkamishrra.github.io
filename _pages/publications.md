---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if site.author.googlescholar %}
  For most recent publications, please check <a href="{{ site.author.googlescholar }}">my Google Scholar profile</a>.
{% endif %}

{% include base_path %}

<h2>Journal Articles</h2>
-----
{% for post in site.publications reversed %}
  {% if post.pubtype == 'journal' %}
      {% include archive-single.html %}
  {% endif %}
{% endfor %}


<h2>Conference Presentations</h2>
-----
{% for post in site.publications reversed %}
  {% if post.pubtype == 'conference' %}
      {% include archive-single.html %}
  {% endif %}
{% endfor %}

{% for post in site.publications reversed %}
  {% if post.pubtype == 'abstract' %}
      {% include archive-single.html %}
  {% endif %}
{% endfor %}
