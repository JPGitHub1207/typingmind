#!/usr/bin/env node

/**
 * Helper script to collect and organize further education network data
 * Usage: node collect-data.js
 */

const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, 'further-education-networks.json');

// Load existing data
function loadData() {
  try {
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error loading data file:', error.message);
    process.exit(1);
  }
}

// Save data
function saveData(data) {
  try {
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
    console.log('✓ Data saved successfully');
  } catch (error) {
    console.error('Error saving data file:', error.message);
    process.exit(1);
  }
}

// Add entry to a specific category
function addEntry(data, region, category, entry) {
  const regionData = data.regions.find(r => r.region === region);
  
  if (!regionData) {
    console.error(`Region "${region}" not found`);
    return false;
  }

  const categoryKey = category === 'network' ? 'networks' :
                     category === 'community' ? 'communitiesOfPractice' :
                     category === 'membership' ? 'membershipOrganisations' : null;

  if (!categoryKey) {
    console.error(`Invalid category: ${category}. Use 'network', 'community', or 'membership'`);
    return false;
  }

  // Check for duplicates
  const exists = regionData[categoryKey].some(e => 
    e.name.toLowerCase() === entry.name.toLowerCase()
  );

  if (exists) {
    console.log(`⚠ Entry "${entry.name}" already exists in ${region}`);
    return false;
  }

  regionData[categoryKey].push(entry);
  return true;
}

// Add national entry
function addNationalEntry(data, category, entry) {
  const categoryKey = category === 'network' ? 'networks' :
                     category === 'community' ? 'communitiesOfPractice' :
                     category === 'membership' ? 'membershipOrganisations' : null;

  if (!categoryKey) {
    console.error(`Invalid category: ${category}. Use 'network', 'community', or 'membership'`);
    return false;
  }

  const exists = data.national[categoryKey].some(e => 
    e.name.toLowerCase() === entry.name.toLowerCase()
  );

  if (exists) {
    console.log(`⚠ Entry "${entry.name}" already exists in national`);
    return false;
  }

  data.national[categoryKey].push(entry);
  return true;
}

// Generate summary report
function generateReport(data) {
  console.log('\n=== Further Education Networks Summary ===\n');
  
  let totalNetworks = 0;
  let totalCommunities = 0;
  let totalMemberships = 0;

  data.regions.forEach(region => {
    const networks = region.networks.length;
    const communities = region.communitiesOfPractice.length;
    const memberships = region.membershipOrganisations.length;

    if (networks > 0 || communities > 0 || memberships > 0) {
      console.log(`${region.region}:`);
      console.log(`  Networks: ${networks}`);
      console.log(`  Communities of Practice: ${communities}`);
      console.log(`  Membership Organisations: ${memberships}`);
      console.log('');
    }

    totalNetworks += networks;
    totalCommunities += communities;
    totalMemberships += memberships;
  });

  const nationalNetworks = data.national.networks.length;
  const nationalCommunities = data.national.communitiesOfPractice.length;
  const nationalMemberships = data.national.membershipOrganisations.length;

  console.log('National:');
  console.log(`  Networks: ${nationalNetworks}`);
  console.log(`  Communities of Practice: ${nationalCommunities}`);
  console.log(`  Membership Organisations: ${nationalMemberships}`);
  console.log('');

  console.log('=== Totals ===');
  console.log(`Total Regional Networks: ${totalNetworks}`);
  console.log(`Total Regional Communities: ${totalCommunities}`);
  console.log(`Total Regional Membership Organisations: ${totalMemberships}`);
  console.log(`Total National Networks: ${nationalNetworks}`);
  console.log(`Total National Communities: ${nationalCommunities}`);
  console.log(`Total National Membership Organisations: ${nationalMemberships}`);
  console.log(`\nGrand Total: ${totalNetworks + totalCommunities + totalMemberships + nationalNetworks + nationalCommunities + nationalMemberships} entries\n`);
}

// Export CSV
function exportCSV(data, filename = 'further-education-networks.csv') {
  const rows = [];
  rows.push(['Type', 'Category', 'Region', 'Name', 'Member Count', 'Membership Types', 'Website', 'Description']);

  // Regional entries
  data.regions.forEach(region => {
    region.networks.forEach(entry => {
      rows.push([
        'Network',
        'Regional',
        region.region,
        entry.name,
        entry.memberCount || '',
        Array.isArray(entry.membershipTypes) ? entry.membershipTypes.join('; ') : '',
        entry.website || '',
        entry.description || ''
      ]);
    });

    region.communitiesOfPractice.forEach(entry => {
      rows.push([
        'Community of Practice',
        'Regional',
        region.region,
        entry.name,
        entry.memberCount || '',
        Array.isArray(entry.membershipTypes) ? entry.membershipTypes.join('; ') : '',
        entry.website || '',
        entry.description || ''
      ]);
    });

    region.membershipOrganisations.forEach(entry => {
      rows.push([
        'Membership Organisation',
        'Regional',
        region.region,
        entry.name,
        entry.memberCount || '',
        Array.isArray(entry.membershipTypes) ? entry.membershipTypes.join('; ') : '',
        entry.website || '',
        entry.description || ''
      ]);
    });
  });

  // National entries
  data.national.networks.forEach(entry => {
    rows.push([
      'Network',
      'National',
      'All Regions',
      entry.name,
      entry.memberCount || '',
      Array.isArray(entry.membershipTypes) ? entry.membershipTypes.join('; ') : '',
      entry.website || '',
      entry.description || ''
    ]);
  });

  data.national.communitiesOfPractice.forEach(entry => {
    rows.push([
      'Community of Practice',
      'National',
      'All Regions',
      entry.name,
      entry.memberCount || '',
      Array.isArray(entry.membershipTypes) ? entry.membershipTypes.join('; ') : '',
      entry.website || '',
      entry.description || ''
    ]);
  });

  data.national.membershipOrganisations.forEach(entry => {
    rows.push([
      'Membership Organisation',
      'National',
      'All Regions',
      entry.name,
      entry.memberCount || '',
      Array.isArray(entry.membershipTypes) ? entry.membershipTypes.join('; ') : '',
      entry.website || '',
      entry.description || ''
    ]);
  });

  // Convert to CSV
  const csv = rows.map(row => 
    row.map(cell => {
      const str = String(cell || '');
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return `"${str.replace(/"/g, '""')}"`;
      }
      return str;
    }).join(',')
  ).join('\n');

  fs.writeFileSync(filename, csv, 'utf8');
  console.log(`✓ CSV exported to ${filename}`);
}

// CLI interface
const args = process.argv.slice(2);
const command = args[0];

if (command === 'report') {
  const data = loadData();
  generateReport(data);
} else if (command === 'export') {
  const data = loadData();
  const filename = args[1] || 'further-education-networks.csv';
  exportCSV(data, filename);
} else {
  console.log(`
Usage:
  node collect-data.js report          - Generate summary report
  node collect-data.js export [file]   - Export to CSV (default: further-education-networks.csv)

To add entries, edit further-education-networks.json directly or use a JSON editor.
  `);
}
