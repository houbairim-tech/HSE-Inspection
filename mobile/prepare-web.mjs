import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const root = process.cwd();
const www = path.join(root, 'www');
fs.rmSync(www, { recursive: true, force: true });
fs.mkdirSync(www, { recursive: true });

execFileSync('unzip', ['-q', 'DOC-20261119-WA0121.zip', '-d', path.join(root, '.source')], { stdio: 'inherit' });
const source = path.join(root, '.source', 'desktop');
fs.copyFileSync(path.join(source, 'index.html'), path.join(www, 'index.html'));
fs.copyFileSync(path.join(source, 'manifest.webmanifest'), path.join(www, 'manifest.webmanifest'));
fs.copyFileSync(path.join(source, 'icon.png'), path.join(www, 'icon.png'));

const css = fs.readFileSync(path.join(root, 'mobile', 'mobile.css'), 'utf8');
const index = path.join(www, 'index.html');
let html = fs.readFileSync(index, 'utf8');
html = html.replace('</head>', `<style id="androidMobileUI">${css}</style>\n</head>`);
html = html.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0" />', '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no" />');
html = html.replace(/<script src="libs\\/xlsx\\.full\\.min\\.js"><\\/script>/, '<script src="libs/xlsx.full.min.js"></script>');
fs.writeFileSync(index, html, 'utf8');

const xlsx = path.join(root, 'node_modules', 'xlsx', 'dist', 'xlsx.full.min.js');
fs.mkdirSync(path.join(www, 'libs'), { recursive: true });
fs.copyFileSync(xlsx, path.join(www, 'libs', 'xlsx.full.min.js'));

const epc = path.join(source, 'epc');
if (fs.existsSync(epc)) fs.cpSync(epc, path.join(www, 'epc'), { recursive: true });

fs.rmSync(path.join(root, '.source'), { recursive: true, force: true });
console.log('Prepared Android web assets:', fs.statSync(index).size, 'bytes');