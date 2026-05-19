---
layout: default
title: Archive
permalink: /archive/
---
<div class="container">
  <h1 style="margin:2rem 0 1.5rem;font-size:1.8rem">Archive</h1>
  {% assign posts_by_date = site.posts | group_by_exp: "post", "post.date | date: '%Y-%m-%d'" %}
  {% for day in posts_by_date %}
  <div class="archive-day">
    <h3 class="archive-date">{{ day.name }}</h3>
    <ul class="archive-list">
      {% for post in day.items %}
      <li class="archive-item">
        <span class="badge badge-{{ post.category }}">{{ post.category }}</span>
        <a href="{{ post.url | relative_url }}">{{ post.repo }}</a>
        <span class="archive-desc">— {{ post.description | truncate: 80 }}</span>
        <span class="archive-stars">⭐ {{ post.stars_display }}</span>
      </li>
      {% endfor %}
    </ul>
  </div>
  {% endfor %}
</div>
<style>
.archive-day{margin-bottom:2rem}
.archive-date{font-size:.85rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;border-bottom:1px solid var(--border);padding-bottom:.4rem;margin-bottom:.75rem}
.archive-list{list-style:none;display:flex;flex-direction:column;gap:.5rem}
.archive-item{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;font-size:.88rem}
.archive-item a{font-family:var(--font-mono);font-weight:600}
.archive-desc{color:var(--text-secondary)}
.archive-stars{color:var(--text-muted);margin-left:auto;white-space:nowrap}
</style>
