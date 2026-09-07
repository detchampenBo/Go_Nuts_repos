(() => {
  const button=document.getElementById('inspect-spidey');
  button?.addEventListener('click',()=>{
    const sort=document.getElementById('balance-sort'),hero=document.getElementById('balance-hero');
    sort.value='in';sort.dispatchEvent(new Event('change',{bubbles:true}));
    hero.value='Spider-Man';hero.dispatchEvent(new Event('change',{bubbles:true}));
    hero.focus({preventScroll:true});
    document.querySelector('.balance-scroll').scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  });
})();
