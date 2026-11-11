# Do older players cross transfer community boundaries more often?

Among transfers out of Europe’s top-five leagues, are players aged 30 or older at the time of the move more likely than players under 30 to join a club outside those leagues?


## Idea for a Null Model
https://arxiv.org/abs/1210.5288
Comments:	Camera ready version for IEEE Workshop on Network Science; fixed some typos in table
Subjects:	Social and Information Networks (cs.SI); Physics and Society (physics.soc-ph)
Cite as:	arXiv:1210.5288 [cs.SI]
 	(or arXiv:1210.5288v4 [cs.SI] for this version)
 
https://doi.org/10.48550/arXiv.1210.5288
Focus to learn more
Journal reference:	Proceedings of IEEE 2013 2nd International Network Science Workshop (NSW 2013), pp. 22--30

Use a directed Erdős–Rényi graph to randomize which clubs can trade, then simulate your transfers over those random routes. The extra step matters because the random graph itself has no ages or transfer counts. NetworkX documentation
1. Generate random routes. For each season, take the same clubs and the same number of distinct outgoing routes from top-five clubs as in your data. Draw that many ordered club pairs uniformly at random from the eligible pairs. Exclude self-links. Redraw if a club with observed departures has no random outgoing route.
2. Put transfers on those routes. Keep each observed transfer’s origin club and age group. Give it a random destination from that club’s simulated outgoing routes. Sample with replacement so several players can take the same route.
3. Pool the seasons and measure the gap. Calculate the percentage of 30+ transfers that go outside the top five minus the under-30 percentage. Repeat the simulation 999 times and plot the observed gap against the simulated gaps.
This asks “How large an age gap would we see if clubs had random trading partners?” The age-label shuffle asks “How large an age gap would we see on the actual routes if age were unrelated to destination within each origin club?”