# IBLIS-CAST

_**Convert any YouTube channel or playlist to a RSS feed compatible with any podcast app.**_

## Why

The purpose of this project is to be able to generate a RSS feed from any Youtube url without maintaining any server.

The main problems this script try to resolve are:

- No need to have a [Youtube API Key](https://developers.google.com/youtube/v3/getting-started#before-you-start)
- No need to have any database, the RSS feed is generated for each call
- No need to download files, convert them and host them

## Features

- Choose quality (default is 720p)
- Choose number of latest items from the playlist or channel to show in the RSS feed (default is 5)
- Works with dailymotion, vimeo
- Works with unique video url

## Library and Tools

- [Youtube-dl](https://github.com/rg3/youtube-dl/) To extract videos information and the download url
- [rfeed](https://github.com/svpino/rfeed) To generate the RSS feed
- [Serverless](https://serverless.com/) To help us deploying our function
- [AWS](https://aws.amazon.com/) For exposing the api in an inexpensive way (using AWS Lambda and AWS Gateway).

## Deploy

Install and follow [instructions](https://serverless.com/framework/docs/providers/aws/guide/installation/) to setup serverless with AWS

`serverless deploy`

## Test

Get your api url in the console log after deploying, replace below and then open the url or copy it in your podcast app:
`https://XXXX.amazonaws.com/staging/getrss?url=https://www.youtube.com/channel/UC2QKuEonyj4rWPZyVcbTjqg`

To change the default values:
`https://XXXX.amazonaws.com/staging/getrss?url=https://www.youtube.com/channel/UC2QKuEonyj4rWPZyVcbTjqg&count=20&quality=1080&filterTitle=Chine`

## Test locally

`serverless invoke local --function getRss --path test.json`

## Contribute

1.  [Fork](https://help.github.com/articles/fork-a-repo/) this repository to your own GitHub account and then [clone](https://help.github.com/articles/cloning-a-repository/) it to your local device
2.  Make the necessary changes and ensure that the tests are passing
3.  Send a pull request

## Todo

- Find a way to get the uploader's thumbnail and not use the first video thumbnail
- Automatically download the latest youtube-dl and rfeed python library when a new version is available
- Test other website with the [supported sites](http://rg3.github.io/youtube-dl/supportedsites.html)
- Make it faster to be able to add more items in playlist count (now timeout occurs if we request too much items in RSS feed)
- Add option to generate RSS feed with only audio

## Known issues

- None for the moment

## Thanks

- [Youtube-dl](http://rg3.github.io/youtube-dl/) for the fantastic work
- [Podsync](https://podsync.net/) for giving me the idea

## License

Please, refer to LICENSE file
