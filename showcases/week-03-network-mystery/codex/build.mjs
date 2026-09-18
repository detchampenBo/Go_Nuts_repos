import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const dir=path.dirname(fileURLToPath(import.meta.url));
let html=fs.readFileSync(path.join(dir,'template.html'),'utf8');
for(const [token,file] of [['STYLE','style.css'],['CASE','case.js'],['LOGIC','logic.js'],['APP','app.js']])html=html.replace(`/* ${token} */`,fs.readFileSync(path.join(dir,file),'utf8'));
fs.writeFileSync(path.join(dir,'prototype.html'),html);
console.log('Built portable prototype.html; no server or external assets required.');
