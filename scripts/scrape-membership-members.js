#!/usr/bin/env node

const fs = require('fs/promises');
const path = require('path');
const cheerio = require('cheerio');
const { decode } = require('html-entities');

const ROOT = path.resolve(__dirname, '..');
const DATA_DIR = path.join(ROOT, 'data', 'fe_networks');
const CONFIG_PATH = path.join(DATA_DIR, 'membership-organisations.json');
const OUTPUT_JSON = path.join(DATA_DIR, 'membership_members.json');
const OUTPUT_CSV = path.join(DATA_DIR, 'membership_members.csv');

const DEFAULT_HEADERS = {
  'User-Agent': 'FE-Networks-Scraper/1.0 (+github.com/JPGitHub1207)'
};

const scrapers = {
  async aocInteractiveMap(org) {
    const url = org.harvest?.source;
    if (!url) throw new Error('Missing AoC JSON endpoint');

    const res = await fetch(url, { headers: DEFAULT_HEADERS });
    if (!res.ok) {
      throw new Error(`Failed to download ${url} (${res.status})`);
    }

    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (err) {
      throw new Error(`Unable to parse JSON from ${url}: ${err.message}`);
    }

    if (!Array.isArray(data)) {
      throw new Error('Unexpected JSON structure returned by AoC');
    }

    return data.map((entry) => ({
      name: entry.name?.trim() || null,
      location: entry.region?.trim() || null,
      memberType: entry.memberClass?.trim() || null,
      website: normalizeUrl(entry.website),
      metadata: {
        id: entry.id,
        parent: entry.parent || null,
        phone: entry.phone || null,
        address: entry.address || null
      }
    }));
  },

  async landexHotspots(org) {
    const url = org.harvest?.source;
    if (!url) throw new Error('Missing Landex membership URL');

    const res = await fetch(url, { headers: DEFAULT_HEADERS });
    if (!res.ok) {
      throw new Error(`Failed to download ${url} (${res.status})`);
    }

    const html = await res.text();
    const $ = cheerio.load(html);
    const members = [];

    $('.our-members .drag_element').each((_, el) => {
      const hotspot = $(el).find('.point_style');
      const raw = hotspot.attr('data-html') || '';
      if (!raw.trim()) return;

      const snippet = cheerio.load(decode(raw));
      const locale = snippet('h2').text().replace(/\s+/g, ' ').trim();
      const college = snippet('p').first().text().replace(/\s+/g, ' ').trim();
      const href = snippet('h2 a').attr('href') || $(el).find('a').first().attr('href');
      const icon = $(el).find('img.pins_image').attr('src') || '';
      const memberType = /affili/i.test(icon) ? 'Affiliate Member' : 'Full Member';

      members.push({
        name: college || locale || null,
        location: college && locale && college !== locale ? locale : null,
        memberType,
        website: normalizeUrl(href)
      });
    });

    return members;
  }
};

function normalizeUrl(value) {
  if (!value) return null;
  let url = String(value).trim().replace(/\\\//g, '/');
  if (!url) return null;
  if (url.startsWith('//')) {
    url = 'https:' + url;
  } else if (!/^https?:/i.test(url)) {
    if (url.startsWith('www.')) {
      url = 'https://' + url;
    } else if (url.startsWith('/')) {
      return null; // relative links are not useful outside the site
    } else {
      url = 'https://' + url;
    }
  }
  return url;
}

function toCsv(rows) {
  return rows
    .map((row) =>
      row
        .map((value) => {
          if (value === null || value === undefined) return '';
          const str = String(value);
          if (/[",\n]/.test(str)) {
            return '"' + str.replace(/"/g, '""') + '"';
          }
          return str;
        })
        .join(',')
    )
    .join('\n');
}

async function main() {
  const configRaw = await fs.readFile(CONFIG_PATH, 'utf8');
  const config = JSON.parse(configRaw);

  const summary = [];
  const skipped = [];

  for (const org of config.organisations || []) {
    const harvest = org.harvest || {};
    const strategy = harvest.strategy;

    if (!harvest.enabled || !strategy || !scrapers[strategy]) {
      skipped.push({
        name: org.name,
        reason: harvest.reason || 'No scraper configured'
      });
      continue;
    }

    console.log(`→ Scraping ${org.name} (${strategy})`);
    try {
      const members = await scrapers[strategy](org);
      summary.push({
        name: org.name,
        slug: org.slug,
        website: org.website,
        membersPage: org.membersPage,
        source: harvest.source,
        harvestedAt: new Date().toISOString(),
        memberCount: members.length,
        members
      });
      console.log(`  ✓ Found ${members.length} members`);
    } catch (err) {
      skipped.push({
        name: org.name,
        reason: err.message
      });
      console.error(`  ✗ ${err.message}`);
    }
  }

  const payload = {
    generatedAt: new Date().toISOString(),
    organisations: summary
  };

  await fs.writeFile(OUTPUT_JSON, JSON.stringify(payload, null, 2), 'utf8');
  console.log(`
✓ Wrote JSON output to ${path.relative(ROOT, OUTPUT_JSON)}`);

  const csvRows = [
    [
      'organisation_slug',
      'organisation_name',
      'member_name',
      'member_location',
      'member_type',
      'member_website',
      'source_url'
    ]
  ];

  summary.forEach((org) => {
    org.members.forEach((member) => {
      csvRows.push([
        org.slug || '',
        org.name || '',
        member.name || '',
        member.location || '',
        member.memberType || '',
        member.website || '',
        org.source || ''
      ]);
    });
  });

  await fs.writeFile(OUTPUT_CSV, toCsv(csvRows), 'utf8');
  console.log(`✓ Wrote CSV output to ${path.relative(ROOT, OUTPUT_CSV)}`);

  if (skipped.length) {
    console.log('\n⚠️  Skipped organisations:');
    skipped.forEach((item) => {
      console.log(`  - ${item.name}: ${item.reason}`);
    });
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
