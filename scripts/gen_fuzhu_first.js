// gen_fuzhu_first.js
// 从 cn_dicts_moqi/base.dict.yaml 生成"首字辅码"派生词表 cn_dicts_moqi/fuzhu_first.dict.yaml
// 用途：Shift+字母 给首字补辅码后（如 yivi -> yiaavi），让 "yiaa vi" 这种编码能查到整词
// 原理：码表 algebra 的 derive 规则在 xform 之后执行，首字辅码已被删掉，无法靠 derive 生成；
//       因此在词库层直接生成一份"首字双拼+辅码 + 其余音节双拼"的词条，import 进主词库。
// 用法：node scripts/gen_fuzhu_first.js

const fs = require('fs');
const path = require('path');

/**
 * 将带辅码的词条码转换为首字辅码编码
 * 例：yi[aa vi[gw -> yiaa vi ；yi[a vi[gw -> yia vi
 * @param {string} code 词条原始码（音节间以空格分隔，辅码包在 [ ] 中）
 * @returns {string|null} 新码；无首字辅码时返回 null
 */
function convert(code) {
  // 提取首音节及紧随其后的辅码（1~2 位），剩余部分含后续音节及各自的辅码
  const m = code.match(/^(\w\w)\[(\w{1,2})\s+(.+)$/);
  if (!m) return null;
  const first = m[1];       // 首字双拼，如 yi
  const fuzhu = m[2];       // 首字辅码，如 aa
  const rest = m[3].replace(/\[[a-z]+/g, '').replace(/\s+/g, ' ').trim(); // 去掉其余辅码并规整空格
  if (rest === '') return null;
  return first + fuzhu + ' ' + rest;
}

/**
 * 解析词典文件，提取词条并生成派生码
 * @param {string} file 词典文件路径
 * @returns {Array<{word:string, code:string, weight:number}>} 派生词条列表
 */
function parseDict(file) {
  const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/);
  const out = [];
  let inBody = false;
  for (const line of lines) {
    if (!inBody) {
      if (line.startsWith('---')) { inBody = true; continue; }
      continue; // 跳过头部注释
    }
    if (!line || line.startsWith('#') || line.startsWith('...')) continue;
    const parts = line.split('\t');
    if (parts.length < 2) continue;
    const word = parts[0], code = parts[1];
    const weight = parts[2] ? parseInt(parts[2], 10) : 0;
    const newCode = convert(code.trim());
    if (newCode) out.push({ word, code: newCode, weight });
  }
  return out;
}

/**
 * 主函数：生成派生词表文件
 */
function main() {
  const root = path.resolve(__dirname, '..');
  const src = path.join(root, 'cn_dicts_moqi', 'base.dict.yaml');
  const dst = path.join(root, 'cn_dicts_moqi', 'fuzhu_first.dict.yaml');

  let entries = parseDict(src);
  // 按权重降序排列，保证高频词在前
  entries.sort((a, b) => b.weight - a.weight);
  // 同词同码去重（保留权重高者）
  const seen = new Set();
  entries = entries.filter(e => {
    const k = e.word + '\t' + e.code;
    if (seen.has(k)) return false;
    seen.add(k);
    return true;
  });

  const header = [
    '# Rime dictionary',
    '# encoding: utf-8',
    '# 首字辅码派生词表（由 scripts/gen_fuzhu_first.js 自动生成，勿手改）',
    '# 供 Shift+字母 给首字补辅码后查整词使用',
    '',
    '---',
    'name: fuzhu_first',
    'version: "1"',
    'sort: by_weight',
    'use_preset_vocabulary: false',
    '',
    '...',
    ''
  ].join('\n');

  const body = entries.map(e => `${e.word}\t${e.code}\t${e.weight}`).join('\n');
  fs.writeFileSync(dst, header + body + '\n', 'utf8');
  console.log('entries:', entries.length, '->', dst);
}

main();
