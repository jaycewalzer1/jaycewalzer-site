# Injectable PrEP for People Experiencing Homelessness

This is a transmission microsimulation and cost-effectiveness model of long-acting injectable PrEP (lenacapavir, with cabotegravir as a comparator) delivered to adults experiencing homelessness. It compares five arms: usual care, clinic delivery, two low-barrier outreach arms, and a control arm that gets the same outreach with no injection. The model tracks people week by week: infection through mixing groups, the care cascade, delivery capacity, refusal and missed visits, then costs and QALYs. Paired random streams make two identical arms come out exactly identical.

An important caveat: most inputs are hypothetical placeholders, and 107 of 118 parameter rows have no source. It is a structure for a decision, not an answer to one. Within those assumptions, three findings stand out:
- Outreach with no injection (arm E) is the most cost-effective arm, at $84,691 per QALY over 5 years.
- The break-even dose price runs from −$443 to $20,478, depending on what an averted infection is allowed to be worth.
- Elimination can't be bought. Saturating delivery takes incidence from 1.337 to 0.163 per 100 person-years, and 63% of the infections left come from outside the population.

stack: Python, PyTorch, NumPy, pandas, matplotlib, pytest
links: https://github.com/jaycewalzer1/prep-model
