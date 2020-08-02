# Binance-Futures-and-Crypto-Profiles-Algorithm-
A web-based solution that helps a user to manage and optimize their portfolio of cryptocurrencies according to certain criteria. You set how the distribution within the portfolio should change according to how the price of bitcoin changes.
Binance Futures and Crypto Profiles Algorithm 

A web-based solution that helps a user to manage and optimize their portfolio of cryptocurrencies according to certain criteria.
You set how the distribution within the portfolio should change according to how the price of bitcoin changes.

Examples of how the portfolio changes based on the price of Bitcoin:

BTC price: $5,000: 40% Bitcoin 10% Ethereum 50% Dollar
BTC price: $4,000: 45% Bitcoin 15% Ethereum 40% Dollar
BTC price: $3,000: 50% Bitcoin 20% Ethereum 30% Dollar

In other words, the lower the price of bitcoin, the greater the percentage of the portfolio to be allocated to Bitcoin / Ethereum in relation to Dollar.
The same can be said the other way around. If the price of bitcoin goes up, then bitcoin should be sold for dollars and unless the allocation of dollars is greater in relation to Bitcoin.
This is the basic principle of what I am looking for.

The system

The idea is that the system should tell in real time how the portfolio is in relation to “how it should” lie.
That is, if you have too much bitcoin, the system should say how much you should sell to be in phase with the percentage criteria you have set.

data:
In order for the system to be able to tell you if you should buy / sell to be in phase, the system must first know what assets you have and also what these assets are worth.
Prices for various assets will be collected via APIn (There are several options here, but suggested Binance API as this will still be used in other contexts)
The number of each asset within the portfolio will be a combination of manual entry and API collection from commercial markets (Binance only to start with, we will expand with more when the system is up and market tested)

Example:

We have manually entered that we own 2 Bitcoin and $ 5000.
Via the API, the system knows that Binance balance is 3 Bitcoin and $ 2000.
This gives us a total portfolio: 5 Bitcoin and $ 7000.
Price per Bitcoin at a given time is $ 3,000 (Downloaded via API)
This gives the total USD portfolio value at this time $ 22,000
With this information the system can now feel that the value of the portfolio is:

$ 15,000 in BTC
$ 0 in Ethereum
$ 7,000 in USD

The system will tell us that we are not in line with our criteria, we will need to buy X number of Ethereum and X number of Bitcoin.
