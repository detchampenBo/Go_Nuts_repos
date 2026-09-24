export function neighbourhood(data, names) {
  const pair = names.map(name => data.philosophers.findIndex(p => p.name === name));
  if (pair.some(i => i < 0)) throw new Error('A featured philosopher is missing from the data.');
  const neighbours = pair.map(() => new Set());
  for (const [a, b] of data.edges) pair.forEach((p, k) => {
    if (a === p) neighbours[k].add(b);
    if (b === p) neighbours[k].add(a);
  });
  const sort = list => [...list].sort((a, b) => data.philosophers[b].degree - data.philosophers[a].degree || data.philosophers[a].name.localeCompare(data.philosophers[b].name));
  const shared = sort([...neighbours[0]].filter(i => neighbours[1].has(i)));
  const exclusive = neighbours.map((set, k) => sort([...set].filter(i => !neighbours[1-k].has(i) && !pair.includes(i))));
  return { pair, neighbours, shared, exclusive, direct: neighbours[0].has(pair[1]) };
}

export function pairSummary(together) {
  const same = together.filter(Boolean).length;
  return { same, total: together.length, majority: same * 2 === together.length ? 'tie' : same * 2 > together.length ? 'together' : 'apart' };
}
