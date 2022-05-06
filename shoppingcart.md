# shoppingcart

separate import in forest/forest dir
new items are actions, arbitrarily created
dict of items per user
{user1: {item1: stuff}, item2: {otherstuff}}
q's: how does user track and add to cart
how does cart get emptied after purchase - just delete a user's cart once they send a purchase? is the cart always the same as the purchase?
pdict per person, one key per user, tuple of user's info and their cart? starts flow from there
only take shipping info once
once user goes to buy, run "buy" on each entry in their cart based on the cart pdict
charge them once? just add the prices
move buy command away from user, and make the user facing 'buy' actually just add to cart, info in DM?
forest/forest/cart.py
contains pdict
current buy is in imogen/gelato.py
move buy to generalized place?
for testing, work off imogen-postgres to use existing buy? or just rewrite in cart.py?
zoey: testing stub, with nonexistent prices and items, dont work in prod
merchantbot?
store.py
for prototyping, make a separate bot, can merge later
