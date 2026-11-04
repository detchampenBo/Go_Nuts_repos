# Soccerblog archive extraction: feasibility research

3 November 2026. Read-only inspection of a small sample of public pages; no complete archive crawl was performed.

## Conclusion

The public pages support the proposed dataset in principle for accessible articles: one record per article, with its publication date, title, source URL and cleaned article-body text. Archive completeness, exact record count, unattended access and a reliable extraction rule across all historical templates still require validation. Do not interpret successful sample access as proof that every historical article remains available.

## Archive discovery

- The [homepage](https://www.soccerblog.com/) exposes pagination ending at page 278 at inspection time. [Page 2](https://www.soccerblog.com/page/2) was readable. The final page could not be fetched through the research browser, so 278 is an observed pagination label, not independently verified coverage or an article count.
- Monthly archives use `/YYYY/MM`, with examples available for [April 2006](https://www.soccerblog.com/2006/04), [November 2021](https://www.soccerblog.com/2021/11), [November 2023](https://www.soccerblog.com/2023/11) and [April 2025](https://www.soccerblog.com/2025/04). These pages contain linked titles and excerpts, not necessarily complete articles. Follow article links and all archive pagination rather than treating one monthly page as the complete month.
- A [2006 article](https://www.soccerblog.com/2006/04/costa-rica-paulo-wanchope-is-l.htm) remains publicly readable and identifies its publication day as 27 April 2006. This verifies historical access, not the archive's earliest date.
- The date near the top of an archive page can be the site's current header date. Publication dates must come from the individual article's metadata/byline, not that header or the month-only URL.
- The [Haaland article](https://www.soccerblog.com/2025/11/a-day-in-the-life-of-erling-haaland.htm) illustrates that pitfall directly: its byline says 1 November 2025 while research-browser snapshots contain unrelated 2026 header dates. Extract the byline's publication date. Its monthly archive list ends at March 2006 (66 posts) and lists April 2006 (240 posts); these displayed monthly counts can help cross-check an inventory from the same snapshot. March 2006 is the earliest month in that list, not a verified proof of complete historical coverage.

## Access checks and limits

The research browser could not retrieve [robots.txt](https://www.soccerblog.com/robots.txt) or [sitemap_index.xml](https://www.soccerblog.com/sitemap_index.xml). A direct local Python request initially failed DNS resolution in the restricted execution environment. Subsequent direct requests with approved network access to the homepage, robots.txt and the WordPress posts API returned **HTTP 406**. One article request with a browser-like user agent and an HTML Accept header also returned 406; testing stopped rather than trying to circumvent the restriction. These are observations from this environment, not proof of a site-wide ban or an explanation of the server's policy. No API availability or exact raw-HTML selectors were verified. A targeted search did not locate site-specific reuse terms; that is not evidence of a reuse license.

## Recommended output and validation

Use UTF-8 JSON Lines as the primary format: one article object per line, with `url`, `title`, `published_date` (ISO `YYYY-MM-DD`), `article_text`, and `retrieved_at`. Optional fields include publication timestamp when actually supplied, author, cleaned article HTML, extraction status and embedded-media presence. CSV is also possible, but JSONL handles paragraph breaks and optional metadata more naturally.

Extract only the article-body container; preserve paragraph, heading, list and quotation order. Remove navigation, sidebar widgets, advertising containers, scripts, forms, comments, related-post blocks and sharing controls. Retain editorial text that discusses advertising: removing every occurrence of “ad” would destroy legitimate content, as shown by the [April 2006 archive](https://www.soccerblog.com/2006/04).

The [June 2026](https://www.soccerblog.com/2026/06) and [April 2006](https://www.soccerblog.com/2006/04) archives include video-oriented posts with little surrounding text. An HTML-text dataset cannot include speech or image-only text unless separately transcribed. Preserve those short records and flag them instead of inventing missing prose.

For a complete crawl, first create a deduplicated article-URL inventory. Then extract each article, log failures, and reconcile discovered, successfully extracted and failed URLs. Manually compare a stratified sample across years and short/long/media-heavy posts against the visible article. Retain the failed-URL list and do not label the dataset complete until all discovered URLs are accounted for. Use a modest request rate, caching, resumable progress and backoff if access is permitted.
