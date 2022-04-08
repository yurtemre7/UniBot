# UniBot

A Discord bot intended for the use on student-run university severs.

## Features

### Moderation
 * Log messages that were deleted by moderators

### Useful
 * Reaction Roles - Allow users to self-assign roles by clicking on reactions under predefined messages
 * RSS Reader - Monitor RSS feeds for new entries and send them into an associated channel, optionally pinging a certain role

## Wanted Features
### General
 - [x] Sync commands with all servers, get rid of hard coded server ids
 - [ ] Only show commands to eligible users
 - [x] Ship bot in docker container
### Moderation
 - [ ] Extent logging of mod activities
	- [ ] Removal of reactions
	- [ ] Kicks
	- [x] Bans
	- [ ] Timeouts
	- [ ] Voice channel mutes
 - [x] Log certain users deleting their own messages
 - [ ] Check if link points to valid RSS feed before adding it 
 - [ ] Prevent users from escaping certain roles by rejoining

### Useful
 - [x] Equivalent to [isISIS.online](https://isisis.online/)

## Known Issues
 * If an admin deletes multiple messages of the same user, only the first one will be logged
 * If there are multiple new entries in an RSS feed, only the latest one will be posted
 * Bot crashes if it lacks permissions to send RSS entries into a channel

