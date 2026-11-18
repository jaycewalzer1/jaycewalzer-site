# SilverKey

SilverKey was my startup. I was Founder and CEO from April 2025 to August 2026 and led a 9-person team. It was an operating system for home transactions, with a React web app, a React Native app, a Flask API and an OpenAPI contract in one monorepo. It integrated eXp Realty, DocuSign, ATTOM and Plaid.

I architected the property ranking. Each home gets two scores for each buyer. One is the cosine similarity between the buyer's preferences and the listing, both embedded with all-MiniLM-L6-v2. The other is an LLM's compatibility judgment. The final score blends the two with weights learned per user: an L2-regularized logistic regression predicts likes from the two scores, and its coefficients, normalized, become that buyer's blend. Personal weights need at least 10 impressions and one like, and retrain after 10 more. Until then, new buyers borrow the weights of a cohort based on budget, age, zip and home type.

I also built an LLM contract-extraction pipeline that feeds a per-state compliance engine, for example for FEMA flood zones.

The demo runs the real web app and API locally on an empty database. Listings come from a paid MLS feed, so search shows no homes.

stack: React, React Native, TypeScript, Flask, PostgreSQL, Redis, Celery, OpenAPI, sentence-transformers, scikit-learn, AWS
links: https://github.com/jaycewalzer1/SilverKey-Inc
