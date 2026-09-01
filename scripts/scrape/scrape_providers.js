#!/usr/bin/env node

/*
Scrape provider organisations for a given course (LARS code) from
https://findapprenticeshiptraining.apprenticeships.education.gov.uk

Usage:
  node scripts/scrape/scrape_providers.js 105

Outputs:
  data/providers-<lars>.json
  data/providers-<lars>.csv
*/

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const writeFile = promisify(fs.writeFile);
const mkdir = promisify(fs.mkdir);

const fetch = require('node-fetch');
const cheerio = require('cheerio');

const BASE = 'https://findapprenticeshiptraining.apprenticeships.education.gov.uk';

async function fetchHtml(url) {
  const res = await fetch(url, {
    headers: {
      'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    },
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} for ${url}`);
  }
  return await res.text();
}

function absolutize(href) {
  if (!href) return null;
  if (href.startsWith('http')) return href;
  return BASE + href;
}

function parseListPage(html, larsCode) {
  const $ = cheerio.load(html);
  const providers = [];

  // Each provider card has a link id="provider-<ukprn>" under h2 title
  $('a.govuk-link[id^="provider-"]').each((_, a) => {
    const $a = $(a);
    const name = $a.text().trim();
    const href = $a.attr('href');
    const ukprn = ($a.attr('id') || '').replace('provider-', '').trim();

    // Summary card container to extract training options and achievement rate snippets from the list page
    const card = $a.closest('.govuk-summary-card');
    const trainingOptions = card.find('.govuk-summary-list__key:contains("Training options")')
      .parent()
      .find('.govuk-summary-list__value')
      .text()
      .replace(/\s+/g, ' ')
      .trim() || null;

    const achievementRate = card.find('.govuk-summary-list__key:contains("Course achievement rate")')
      .parent()
      .find('.govuk-summary-list__value')
      .text()
      .replace(/\s+/g, ' ')
      .trim() || null;

    providers.push({
      ukprn,
      name,
      listPageUrl: absolutize(href),
      larsCode,
      trainingOptionsListSnippet: trainingOptions,
      achievementRateListSnippet: achievementRate,
    });
  });

  // Pagination: find next link
  let nextPageUrl = null;
  const nextLink = $('nav.app-pagination-nav a:contains("Next »")').attr('href')
    || $('nav.app-pagination-nav a:contains("Next >>")').attr('href')
    || $('nav.app-pagination-nav a:contains("Next")').attr('href');
  if (nextLink) nextPageUrl = absolutize(nextLink);

  return { providers, nextPageUrl };
}

function parseProviderPage(html) {
  const $ = cheerio.load(html);

  // Basic header
  const name = $('h1.govuk-heading-xl').first().text().trim() || null;
  const caption = $('span.govuk-caption-l').first().text().trim();
  const ukprnMatch = caption && caption.match(/UKPRN\s+(\d+)/i);
  const ukprn = ukprnMatch ? ukprnMatch[1] : null;

  // Contact details summary-list
  const contact = {};
  $('dl.govuk-summary-list .govuk-summary-list__row').each((_, row) => {
    const key = $(row).find('.govuk-summary-list__key').text().trim();
    const valueEl = $(row).find('.govuk-summary-list__value');
    const valueText = valueEl.text().replace(/\s+/g, ' ').trim();
    if (/Registered address/i.test(key)) contact.registeredAddress = valueText || null;
    else if (/Email/i.test(key)) {
      contact.email = (valueEl.find('a[href^="mailto:"]').attr('href') || '').replace('mailto:', '') || valueText || null;
    } else if (/Telephone/i.test(key)) contact.telephone = valueText || null;
    else if (/Website/i.test(key)) contact.website = valueEl.find('a').attr('href') || valueText || null;
  });

  // Narrative / Ofsted blurb section if present
  let ofstedBlurb = null;
  $('p.govuk-body').each((_, p) => {
    const t = $(p).text().trim();
    if (/Ofsted/i.test(t)) {
      ofstedBlurb = t;
    }
  });

  // Reviews summary on the provider page (if present)
  const reviews = {};
  // These are shown as star blocks with label spans; capture counts if visible in text
  const employerReviewSummary = $('#feedback-2 .das-rating, #feedback-1 .das-rating').first().parent().text().replace(/\s+/g, ' ').trim();
  if (employerReviewSummary) reviews.employerReviewsSummary = employerReviewSummary;
  const apprenticeReviewSummary = $('#feedback-2 .govuk-!-margin-top-9 .das-rating, #feedback-1 .govuk-!-margin-top-9 .das-rating').first().parent().text().replace(/\s+/g, ' ').trim();
  if (apprenticeReviewSummary) reviews.apprenticeReviewsSummary = apprenticeReviewSummary;

  return { name, ukprn, contact, ofstedBlurb, reviews };
}

async function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

async function main() {
  const larsCode = process.argv[2] || '105';
  const startUrl = `${BASE}/courses/${larsCode}/providers`;

  const outDir = path.join(process.cwd(), 'data');
  await mkdir(outDir, { recursive: true });

  const seenUkprn = new Set();
  const results = [];

  let pageUrl = startUrl;
  let pageIndex = 1;

  while (pageUrl) {
    const html = await fetchHtml(pageUrl);
    const { providers, nextPageUrl } = parseListPage(html, larsCode);

    for (const p of providers) {
      if (seenUkprn.has(p.ukprn)) continue;
      seenUkprn.add(p.ukprn);

      let providerDetails = {};
      try {
        if (p.listPageUrl) {
          const providerHtml = await fetchHtml(p.listPageUrl);
          providerDetails = parseProviderPage(providerHtml);
        }
      } catch (e) {
        providerDetails.error = String(e.message || e);
      }

      results.push({
        ...p,
        ...providerDetails,
      });

      // polite crawling
      await delay(250);
    }

    pageUrl = nextPageUrl;
    pageIndex += 1;

    // extra politeness between pages
    if (pageUrl) await delay(750);
  }

  // Write JSON
  const jsonPath = path.join(outDir, `providers-${larsCode}.json`);
  await writeFile(jsonPath, JSON.stringify(results, null, 2));

  // Write CSV (simple)
  const headers = [
    'ukprn','name','larsCode','registeredAddress','email','telephone','website','trainingOptionsListSnippet','achievementRateListSnippet','ofstedBlurb','listPageUrl'
  ];
  const toCsv = (s) => {
    if (s == null) return '';
    const str = String(s).replace(/\r?\n|\r/g, ' ').replace(/\s+/g, ' ').trim();
    if (str.includes('"') || str.includes(',') ) return '"' + str.replace(/"/g, '""') + '"';
    return str;
  };
  const csvLines = [headers.join(',')];
  for (const r of results) {
    const row = [
      r.ukprn,
      r.name,
      r.larsCode,
      r.contact?.registeredAddress,
      r.contact?.email,
      r.contact?.telephone,
      r.contact?.website,
      r.trainingOptionsListSnippet,
      r.achievementRateListSnippet,
      r.ofstedBlurb,
      r.listPageUrl,
    ].map(toCsv);
    csvLines.push(row.join(','));
  }
  const csvPath = path.join(outDir, `providers-${larsCode}.csv`);
  await writeFile(csvPath, csvLines.join('\n'));

  console.log(`Saved ${results.length} providers to:\n - ${jsonPath}\n - ${csvPath}`);
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}
