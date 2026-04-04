# Architecture

## Workflow Overview
The workflow runs every 15 minutes and performs the following steps:

1. Fetch crypto market data from an API
2. Extract BTC and ETH price information
3. Check whether the 24h price change exceeds the threshold
4. Send an alert if conditions are met
5. Store the result for later analysis