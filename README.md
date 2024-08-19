This program is meant to take the 100 newest listed coins on coinmarketcap and sort them by their volume, dilluted marketcap, price change over 24hr and volume change over 24hr.
It fetches the twitter accounts of the new cryptos from coinmarketcap.
After a pruning step that throws out tokens with low volume, or low volume to marketcap ratio or very poor price performance the remaining coins are passed into a URL with social blade.
The social blade data is scraped to create a final list of 5 crypto currencies that may be promising. 
The results from the previous run are saved in a file.  When ran again these coins will have their new prices scraped and compared to get the approximate returns.
The results are currently saved to a collection in MongoDB, with a prior collection holding the results from previous runs, and current collection holding the freshly scraped coins.
