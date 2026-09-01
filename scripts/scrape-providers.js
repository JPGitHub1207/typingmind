#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const axios = require('axios');
const cheerio = require('cheerio');
const pLimit = require('p-limit').default;

const BASE = 'https://findapprenticeshiptraining.apprenticeships.education.gov.uk';
const OUTPUT_DIR = path.join(__dirname, '..', 'data');
const OUTPUT_JSON = path.join(OUTPUT_DIR, 'providers_by_course.json');
const OUTPUT_CSV = path.join(OUTPUT_DIR, 'providers_by_course.csv');

const http = axios.create({
  baseURL: BASE,
  timeout: 30000,
  headers: {
    'User-Agent': 'TypingMind-scraper/1.0 (+https://example.org)'
  },
  maxRedirects: 5
});

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function normaliseWhitespace(str) {
  return str.replace(/\s+/g, ' ').trim();
}

function extractLevelFromTitle(title) {
  const m = title.match(/\(level\s*(\d+)\)/i);
  return m ? m[1] : '';
}

function needsSkipCourse(title) {
  const t = title.toLowerCase();
  // Skip "Team Leading Level 3" => commonly listed as "Team leader or supervisor (level 3)"
  const teamLeader = /team\s*(leader|leading)[^)]*\(level\s*3\)/i.test(title) || /team\s*leader.*level\s*3/i.test(t) || /team\s*leading.*level\s*3/i.test(t);
  // Skip "Operations Management level 5" => commonly "Operations department manager (level 5)"
  const opsManager = /(operations\s*(department\s*)?manager)[^)]*\(level\s*5\)/i.test(title) || /operations\s*management.*level\s*5/i.test(t);
  return teamLeader || opsManager;
}

async function fetchHtml(urlPath, query = {}) {
  const q = new URLSearchParams(query).toString();
  const fullPath = q ? `${urlPath}?${q}` : urlPath;
  const { data } = await http.get(fullPath);
  return typeof data === 'string' ? data : String(data);
}

function parseCourseList(html) {
  const $ = cheerio.load(html);
  const courses = [];
  $('h2.das-search-results__heading a.das-search-results__link[href^="/courses/"]').each((_, el) => {
    const $a = $(el);
    const href = $a.attr('href') || '';
    const text = normaliseWhitespace($a.text());
    const idMatch = href.match(/\/courses\/(\d+)/);
    if (!idMatch) return;
    const larsCode = idMatch[1];
    const level = extractLevelFromTitle(text);
    courses.push({ larsCode, title: text, level });
  });

  // Determine pagination max
  let totalPages = 1;
  $('.app-pagination-nav a').each((_, el) => {
    const txt = $(el).text().trim();
    const n = parseInt(txt, 10);
    if (!isNaN(n)) totalPages = Math.max(totalPages, n);
  });
  return { courses, totalPages };
}

function parseProviders(html) {
  const $ = cheerio.load(html);
  const providers = [];
  $('div.app-course-provider a[id^="provider-"]').each((_, el) => {
    const $a = $(el);
    const id = $a.attr('id') || '';
    const name = normaliseWhitespace($a.text());
    const ukprnMatch = id.match(/provider-(\d{8})/);
    if (ukprnMatch) {
      providers.push({ ukprn: ukprnMatch[1], name });
    } else {
      // Fallback: try to parse from href if present
      const href = $a.attr('href') || '';
      const hrefMatch = href.match(/providers\/(\d{8})/);
      if (hrefMatch) {
        providers.push({ ukprn: hrefMatch[1], name });
      } else {
        providers.push({ ukprn: '', name });
      }
    }
  });

  // Pagination
  let totalPages = 1;
  $('.app-pagination-nav a').each((_, el) => {
    const txt = $(el).text().trim();
    const n = parseInt(txt, 10);
    if (!isNaN(n)) totalPages = Math.max(totalPages, n);
  });

  return { providers, totalPages };
}

function toCsv(rows, headers) {
  const esc = (v) => {
    if (v === null || v === undefined) return '';
    const s = String(v);
    if (/[",\n]/.test(s)) return '"' + s.replace(/"/g, '""') + '"';
    return s;
  };
  const lines = [headers.map(esc).join(',')];
  for (const row of rows) {
    const line = headers.map((h) => esc(row[h])).join(',');
    lines.push(line);
  }
  return lines.join('\n') + '\n';
}

async function main() {
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  console.log('Fetching first courses page...');
  const firstHtml = await fetchHtml('/courses');
  const first = parseCourseList(firstHtml);
  const totalCoursePages = first.totalPages;
  const coursesMap = new Map();

  for (const c of first.courses) {
    if (!needsSkipCourse(c.title)) coursesMap.set(c.larsCode, c);
  }

  console.log(`Detected ${totalCoursePages} courses pages.`);

  for (let page = 2; page <= totalCoursePages; page++) {
    console.log(`Fetching courses page ${page}/${totalCoursePages}...`);
    const html = await fetchHtml('/courses', { PageNumber: page });
    const parsed = parseCourseList(html);
    for (const c of parsed.courses) {
      if (!needsSkipCourse(c.title)) coursesMap.set(c.larsCode, c);
    }
    await sleep(500); // be polite
  }

  const courses = Array.from(coursesMap.values());
  console.log(`Total courses (after skip): ${courses.length}`);

  const limit = pLimit(4);

  const results = [];

  async function scrapeCourseProviders(course) {
    const { larsCode, title, level } = course;
    const providersAccum = new Map(); // ukprn -> name

    // Fetch first providers page with Distance=All to get totalPages
    let html;
    try {
      html = await fetchHtml(`/courses/${larsCode}/providers`, { Distance: 'All' });
    } catch (err) {
      console.warn(`Failed to fetch providers for course ${larsCode} (${title}): ${err.message}`);
      return { ...course, providers: [], providerCount: 0 };
    }

    let parsed = parseProviders(html);
    for (const p of parsed.providers) {
      providersAccum.set(p.ukprn || p.name, p.name);
    }

    const totalPages = parsed.totalPages;
    for (let page = 2; page <= totalPages; page++) {
      try {
        const pageHtml = await fetchHtml(`/courses/${larsCode}/providers`, { Distance: 'All', PageNumber: page });
        parsed = parseProviders(pageHtml);
        for (const p of parsed.providers) providersAccum.set(p.ukprn || p.name, p.name);
        await sleep(250);
      } catch (err) {
        console.warn(`Failed providers page ${page} for course ${larsCode}: ${err.message}`);
      }
    }

    const providers = Array.from(providersAccum.entries()).map(([ukprn, name]) => ({ ukprn: /^\d{8}$/.test(ukprn) ? ukprn : '', name }));

    return { larsCode, title, level, providers, providerCount: providers.length };
  }

  const tasks = courses.map((course) => limit(() => scrapeCourseProviders(course)));
  for (let i = 0; i < tasks.length; i++) {
    try {
      const res = await tasks[i];
      results.push(res);
      if ((i + 1) % 10 === 0) console.log(`Scraped ${i + 1}/${tasks.length} courses...`);
    } catch (err) {
      console.warn(`Error scraping course index ${i}: ${err.message}`);
    }
  }

  // Sort results by title
  results.sort((a, b) => a.title.localeCompare(b.title));

  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(results, null, 2));
  console.log(`Wrote JSON: ${OUTPUT_JSON}`);

  const csvRows = [];
  for (const r of results) {
    if (!r.providers || r.providers.length === 0) {
      csvRows.push({ larsCode: r.larsCode, courseName: r.title, level: r.level, providerUkprn: '', providerName: '' });
    } else {
      for (const p of r.providers) {
        csvRows.push({ larsCode: r.larsCode, courseName: r.title, level: r.level, providerUkprn: p.ukprn, providerName: p.name });
      }
    }
  }
  const csv = toCsv(csvRows, ['larsCode', 'courseName', 'level', 'providerUkprn', 'providerName']);
  fs.writeFileSync(OUTPUT_CSV, csv, 'utf8');
  console.log(`Wrote CSV: ${OUTPUT_CSV}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
