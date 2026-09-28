// Deliberately constructed, connected undirected contact network; not Marvel canon.
const CASE={title:'The hidden mastermind',rooms:[
{name:'Luke Cage',x:290,y:160},{name:'MJ',x:840,y:380},
{name:'Nick Fury',x:700,y:180},{name:'Daredevil',x:120,y:315},
{name:'Wolverine',x:510,y:70},{name:'Elektra',x:85,y:510},
{name:'Maria Hill',x:920,y:90},{name:'Black Widow',x:320,y:460},
{name:'Spider-Man',x:555,y:335}],
edges:[[0,2],[0,3],[0,4],[0,8],[1,2],[1,8],[2,4],[2,6],[2,7],[2,8],[3,5],[3,7],[4,8],[7,8]],
suspects:[
{name:'Black Widow',room:7,color:'#fd738e',symbol:'widow',note:'The covert operative'},
{name:'Spider-Man',room:8,color:'#57e6eb',symbol:'spider',note:'The neighbourhood hero'},
{name:'Daredevil',room:3,color:'#e5a2ff',symbol:'devil',note:'The rooftop vigilante'},
{name:'Wolverine',room:4,color:'#ffd469',symbol:'claws',note:'The lone fighter'}],
clues:[
{name:'The contact list',topic:'Degree · direct connections',statement:'The mastermind has exactly three direct contacts in this network.',question:'Who has the wrong number of contacts?',instruction:'Choose a hero. Light up their direct contacts and count the links. Clear the hero who does not fit.',math:'k(v) = number of neighbours; the clue requires k = 3.'},
{name:'The fast messenger',topic:'Closeness · average distance',statement:'The mastermind is at most 1.75 steps away from everyone else, on average.',question:'Who is too far from the rest of the network?',instruction:'Send waves from each remaining hero until everyone is reached. Compare the average distance with 1.75.',math:'C(v) = 8 / Σ d(v,u) = 1 / mean distance. Smaller mean distance means higher closeness.'},
{name:'The hidden broker',topic:'Betweenness · shortest-path traffic',statement:'The mastermind carries at least 10% of shortest-path traffic between other people.',question:'Who carries too little traffic?',instruction:'Run the traffic playback, then compare the remaining heroes. Endpoints earn no credit; tied shortest routes split the credit.',math:'B(v) = (1/28) Σ σ(s,t through v) / σ(s,t), over the 28 unordered pairs excluding v.'}]
};
if(typeof module!=='undefined')module.exports=CASE;
