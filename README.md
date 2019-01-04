# IBLIS-CAST

How to convert any youtube channel or playlist to a RSS feed compatible with all your podcast app.

## Library and tools
For get the download url we will use youtube-dl
For create the rss feed we use rfeed
For expose the api, we will use AWS Lambda et AWS Gateway
To help us to deploy our function we will use the serverless framework

## How to deploy

serverless deploy --aws-profile 20ss_admin --stage v1 

serverless invoke local --function getRss --path test.jsonstage