(() => {
  document.querySelectorAll('.prediction').forEach(panel => {
    const buttons=[...panel.querySelectorAll('[data-choice]')];
    const reveal=panel.querySelector('.prediction-answer');
    buttons.forEach(button=>button.addEventListener('click',()=>{
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
      const right=button.dataset.choice===panel.dataset.answer;
      panel.querySelector('.prediction-feedback').textContent=right?'You spotted the clue. Here is the evidence.':'A twist in the story. Here is what the data shows.';
      if(reveal)reveal.open=true;
    }));
  });
  const button=document.getElementById('locate-island'), island=document.getElementById('island-reveal');
  if(button&&island)button.addEventListener('click',()=>{
    const show=island.hidden;island.hidden=!show;button.setAttribute('aria-expanded',String(show));button.textContent=show?'Hide transmission ↙':'Locate the island ↗';
  });
})();
