#!/usr/bin/env node

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import https from 'node:https';
import cheerio from 'cheerio';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SEARCH_URL = 'https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=3';

function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; OfstedScraper/1.0)' } }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return resolve(fetch(new URL(res.headers.location, url).toString()));
      }
      if (res.statusCode !== 200) {
        reject(new Error(`Request failed with status ${res.statusCode}`));
        return;
      }
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

function parseResults(html, limit = 10) {
  const $ = cheerio.load(html);
  const items = [];
  $('ul.results-list > li.search-result').each((i, el) => {
    if (items.length >= limit) return false;

    const titleEl = $(el).find('h3.search-result__title a');
    const name = titleEl.text().trim();

    const category = $(el)
      .find('.search-result__provider-info li:contains("Category:") strong')
      .first()
      .text()
      .trim() || null;

    const address = $(el).find('address.search-result__address').text().trim() || null;

    // Rating may not exist
    const rating = $(el)
      .find('.search-result__provider-info li:contains("Rating:") strong')
      .first()
      .text()
      .trim() || null;

    const latestReport = $(el)
      .find('.search-result__provider-info li:contains("Latest report:") time')
      .first()
      .text()
      .trim() || null;

    const urn = $(el)
      .find('.search-result__provider-info li:contains("URN:") strong')
      .first()
      .text()
      .trim() || null;

    const href = titleEl.attr('href');
    const providerUrl = href ? new URL(href, 'https://reports.ofsted.gov.uk').toString() : null;

    items.push({ name, category, address, rating, latestReport, urn, providerUrl });
  });
  return items;
}

async function main() {
  const html = await fetch(SEARCH_URL);
  const results = parseResults(html, 10);
  const outDir = path.resolve(__dirname, '..', 'data');
  await fs.mkdir(outDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const jsonPath = path.join(outDir, `ofsted-fes-first-10-${ts}.json`);
  const csvPath = path.join(outDir, `ofsted-fes-first-10-${ts}.csv`);

  await fs.writeFile(jsonPath, JSON.stringify(results, null, 2), 'utf8');

  const headers = ['Name', 'Category', 'Address', 'Rating', 'Latest report', 'URN', 'Provider URL'];
  const lines = [headers.join(',')];
  for (const r of results) {
    const row = [r.name, r.category, r.address, r.rating, r.latestReport, r.urn, r.providerUrl]
      .map((v) => {
        if (v == null) return '';
        const s = String(v).replace(/"/g, '""');
        return `"${s}"`;
      })
      .join(',');
    lines.push(row);
  }
  await fs.writeFile(csvPath, lines.join('\n'), 'utf8');

  console.log(JSON.stringify({ count: results.length, jsonPath, csvPath }, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
