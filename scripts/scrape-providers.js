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

const CLI_OPTIONS = (() => {
  const opts = { max: Infinity };
  for (const arg of process.argv.slice(2)) {
    if (arg.startsWith('--max=')) {
      const value = parseInt(arg.split('=')[1], 10);
      if (!Number.isNaN(value) && value > 0) {
        opts.max = value;
      }
    }
  }
  return opts;
})();

const FLUSH_INTERVAL = Math.max(1, parseInt(process.env.FLUSH_INTERVAL || '25', 10));

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

function needsSkipCourse() {
  return false; // retain hook but include every course
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

  const hasNext = $('.app-pagination-nav a').toArray().some((el) => {
    const txt = $(el).text().trim().toLowerCase();
    return txt.startsWith('next');
  });

  return { courses, hasNext };
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

  const hasNext = $('.app-pagination-nav a').toArray().some((el) => {
    const txt = $(el).text().trim().toLowerCase();
    return txt.startsWith('next');
  });

  return { providers, hasNext };
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

function writeOutputsFromMap(map, { logOutput = false } = {}) {
  const results = Array.from(map.values()).sort((a, b) => a.title.localeCompare(b.title));

  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(results, null, 2));

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

  if (logOutput) {
    console.log(`Wrote JSON: ${OUTPUT_JSON}`);
    console.log(`Wrote CSV: ${OUTPUT_CSV}`);
    const providerPairs = csvRows.length;
    console.log(`Summary -> courses: ${results.length}, provider-course pairs: ${providerPairs}`);
  }
}

async function main() {
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  console.log('Fetching courses catalogue...');
  const coursesMap = new Map();

  let page = 1;
  while (true) {
    const query = page > 1 ? { PageNumber: page } : {};
    console.log(`Fetching courses page ${page}...`);
    const html = await fetchHtml('/courses', query);
    const parsed = parseCourseList(html);
    for (const c of parsed.courses) {
      if (!needsSkipCourse(c.title)) coursesMap.set(c.larsCode, c);
    }
    await sleep(100);
    if (!parsed.hasNext) break;
    page += 1;
  }

  const courses = Array.from(coursesMap.values());
  console.log(`Total courses detected: ${courses.length}`);

  const existingResults = fs.existsSync(OUTPUT_JSON)
    ? JSON.parse(fs.readFileSync(OUTPUT_JSON, 'utf8'))
    : [];
  const resultMap = new Map(existingResults.map((item) => [item.larsCode, item]));

  console.log(`Existing course records: ${resultMap.size}`);

  let pendingCourses = courses.filter((course) => !resultMap.has(course.larsCode));
  if (Number.isFinite(CLI_OPTIONS.max)) {
    pendingCourses = pendingCourses.slice(0, CLI_OPTIONS.max);
  }

  if (pendingCourses.length === 0) {
    console.log('No new courses to scrape. Regenerating outputs...');
    writeOutputsFromMap(resultMap, { logOutput: true });
    return;
  }

  console.log(`Courses remaining to scrape this run: ${pendingCourses.length}`);

  const limit = pLimit(10);

  async function scrapeCourseProviders(course) {
    const { larsCode, title, level } = course;
    const providersAccum = new Map(); // ukprn -> name

    // Fetch first providers page with Distance=All to get totalPages
    let providersPage = 1;
    let hasNext = true;

    while (hasNext) {
      try {
        const query = { Distance: 'All' };
        if (providersPage > 1) query.PageNumber = providersPage;
        const html = await fetchHtml(`/courses/${larsCode}/providers`, query);
        const parsed = parseProviders(html);
        for (const p of parsed.providers) {
          providersAccum.set(p.ukprn || p.name, p.name);
        }
        hasNext = parsed.hasNext;
        providersPage += 1;
        await sleep(100);
      } catch (err) {
        console.warn(`Failed providers page ${providersPage} for course ${larsCode}: ${err.message}`);
        break;
      }
    }

    const providers = Array.from(providersAccum.entries()).map(([ukprn, name]) => ({ ukprn: /^\d{8}$/.test(ukprn) ? ukprn : '', name }));

    return { larsCode, title, level, providers, providerCount: providers.length };
  }

  const tasks = pendingCourses.map((course) => limit(() => scrapeCourseProviders(course)));
  const totalCourses = courses.length;
  const alreadyScraped = resultMap.size;
  let processedThisRun = 0;

  for (let i = 0; i < tasks.length; i++) {
    try {
      const res = await tasks[i];
      processedThisRun += 1;
      if (res && res.larsCode) {
        resultMap.set(res.larsCode, res);
      }

      const overallProcessed = alreadyScraped + processedThisRun;
      if (overallProcessed % 10 === 0 || processedThisRun % 10 === 0) {
        console.log(`Scraped ${overallProcessed}/${totalCourses} courses...`);
      }

      if (processedThisRun % FLUSH_INTERVAL === 0 || processedThisRun === tasks.length) {
        writeOutputsFromMap(resultMap);
      }
    } catch (err) {
      console.warn(`Error scraping course index ${i}: ${err.message}`);
    }
  }

  writeOutputsFromMap(resultMap, { logOutput: true });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
