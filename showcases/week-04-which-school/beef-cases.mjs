export const cases = [
  {
    id: 'hegel', topic: 'A system, or nonsense?', kind: 'A documented criticism',
    people: ['Georg Wilhelm Friedrich Hegel', 'Arthur Schopenhauer'],
    short: ['Hegel', 'Schopenhauer'], dates: ['1770–1831', '1788–1860'],
    images: ['hegel.jpg', 'schopenhauer.jpg'],
    positions: ['History has a rational structure.', 'A grand system can still be nonsense.'],
    explanations: ['Hegel interprets world history as the development of freedom, intelligible through reason.', 'Schopenhauer attacks Hegel’s writing as empty verbiage rather than a meaningful account of the world.'],
    context: 'Schopenhauer explicitly attacks Hegel in The Art of Controversy. This is a documented criticism, not a claim that Hegel replied in kind.',
    interpretation: 'Even explicit hostility does not separate this pair in these runs. Louvain groups patterns of links; it cannot read agreement into them.',
    sources: [
      ['Hegel · Introduction to the Philosophy of History', 'Reason and freedom in history; the first position is a paraphrase.', 'https://www.marxists.org/reference/archive/hegel/works/hi/introduction.htm'],
      ['Schopenhauer · The Art of Controversy, stratagem III', 'Schopenhauer recounts his criticism of Hegel’s writing.', 'https://www.gutenberg.org/cache/epub/10731/pg10731.html'],
    ],
  },
  {
    id: 'hobbes', topic: 'Are we born at war?', kind: 'A criticism across generations',
    people: ['Thomas Hobbes', 'Jean-Jacques Rousseau'],
    short: ['Hobbes', 'Rousseau'], dates: ['1588–1679', '1712–1778'],
    images: ['hobbes.jpg', 'rousseau.jpg'],
    positions: ['Without a common power, conflict threatens.', 'You’ve mistaken society’s passions for nature.'],
    explanations: ['For Hobbes, insecurity and competition make peace precarious where no common authority can enforce it.', 'Rousseau argues that Hobbes projects socially developed desires onto natural humans, overlooking pity and limited needs.'],
    context: 'Rousseau names and criticises Hobbes in his Discourse on Inequality. They lived in different generations: this was an argument with a text, not a face-to-face feud.',
    interpretation: 'The pair usually shares a community, but not always. Their disagreement is documented; the boundary around them still depends on the algorithm’s seed.',
    sources: [
      ['Hobbes · Leviathan, chapter XIII', 'The state of war without a common power.', 'https://www.gutenberg.org/files/3207/3207-h/3207-h.htm'],
      ['Rousseau · Discourse on Inequality, first part', 'The passages naming Hobbes challenge his account of natural humanity.', 'https://www.gutenberg.org/cache/epub/11136/pg11136.html'],
    ],
  },
  {
    id: 'plato', topic: 'Do we need another reality?', kind: 'A criticism of a teacher’s theory',
    people: ['Plato', 'Aristotle'], short: ['Plato', 'Aristotle'],
    dates: ['c. 428–348 BCE', '384–322 BCE'], images: ['plato.png', 'aristotle.jpg'],
    positions: ['Beautiful things participate in Beauty itself.', 'What do separate Forms actually explain?'],
    explanations: ['In the Phaedo, Plato’s Socrates explains beautiful things by their participation in the Form of Beauty.', 'Aristotle challenges how separate Forms could cause or explain the changing things of our world.'],
    context: 'Aristotle directly challenges the theory of Forms in Metaphysics I.9. This disagreement concerns a specific theory; it does not make their entire philosophies opposites.',
    interpretation: 'This pair sits close to a fifty-fifty split across runs. A single partition would hide that instability, even though the philosophical dispute stays the same.',
    sources: [
      ['Plato · Phaedo, 100b–101d', 'The argument from participation in Forms.', 'https://classics.mit.edu/Plato/phaedo.html'],
      ['Aristotle · Metaphysics, book I, part 9', 'The critique of Forms as explanations of sensible things.', 'https://classics.mit.edu/Aristotle/metaphysics.1.i.html'],
    ],
  },
];
