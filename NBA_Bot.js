const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const { MongoClient } = require('mongodb');
require('dotenv').config();
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages] });
const mongo_client = new MongoClient(process.env.MONGO_KEY);

client.once('ready', () => {
	console.log('Ready!');
});

client.on('interactionCreate', async interaction => {
	if (!interaction.isChatInputCommand()) return;

	const { commandName } = interaction;
	console.log(commandName);
	
	if (commandName === 'teams') {
		const teamname = interaction.options.getString('team');
		const returnInfo = await TeamInfo(teamname);
		if (returnInfo != null){
			const teamEmbed = new EmbedBuilder().setTitle(returnInfo['team_name']).setColor(0xC70039).setThumbnail(returnInfo['team_logo'])
			.addFields(
				{ name: 'Start Year', value: returnInfo['team_startyear'], inline: true},
				{ name: 'Lifespan', value: returnInfo['team_lifespan'], inline: true },
				{ name: 'Games Played', value: returnInfo['team_games'], inline: true },
				{ name: 'Wins', value: returnInfo['team_wins'], inline :true },
				{ name: 'Losses', value: returnInfo['team_losses'], inline: true },
				{ name: 'Win/Loss Percentage', value: returnInfo['team_wlp'], inline: true },
				{ name: 'Playoff Apperances', value: returnInfo['team_plyfs'], inline: true },
				{ name: 'Division Champions', value: returnInfo['team_divchamp'], inline: true },
				{ name: 'Conference Champions', value: returnInfo['team_confchamp'], inline: true },
				{ name: 'NBA Champions', value: returnInfo['team_nbachamp'], inline: true }
			);
			await interaction.reply(
				{ embeds : [teamEmbed]}
				);
		} else {
			await interaction.reply(
				"Team Does Not Exist"
				);
		}
	}

	if (commandName === 'player') {
		const playername = interaction.options.getString('player');
		const playerInfo = await Player(playername);
		if (playerInfo != null){
			const playerEmbed = new EmbedBuilder().setTitle(playerInfo['player_name']).setColor(0xC70039).setThumbnail(playerInfo['player_img'])
			.addFields(
				{ name: 'Position', value: playerInfo['player_pos'] },
				{ name: 'Height', value: playerInfo['player_height'] },
				{ name: 'Weight', value: playerInfo['player_weight'] },
				{ name: 'Years In NBA', value: playerInfo['player_yearsexp'] },
				{ name: 'College', value: playerInfo['player_college']}
			);
			await interaction.reply(
				{ embeds : [playerEmbed]}
				);
		} else {
			await interaction.reply(
				"Player Does Not Exist"
				);
		}
	}

	if (commandName === 'roster') {
		const teamname = interaction.options.getString('team');
		const rosterReturn = await TeamRoster(teamname);
		if (rosterReturn[0].length != 0 && rosterReturn[1] != undefined ){
			var rosterString = ''
			rosterReturn[0].forEach((player) => {
				rosterString += player + '\n'
			});
			const rosterEmbed = new EmbedBuilder().setTitle(TeamNameReturn(rosterReturn[1])).setColor(0xC70039)
			.addFields(
				{ name: 'Roster', value: rosterString}
			);
			await interaction.reply(
				{ embeds: [rosterEmbed]}
			);
		} else {
			await interaction.reply(
				"Team Does Not Exist"
			);
		}
	}

	if (commandName === 'teamseason') {
		const teamname = interaction.options.getString('team');
		const season = interaction.options.getString('season');
		var year = parseInt(season);
		var seasonyear = year.toString() +'-'+ (year + 1).toString().slice(2);
		const teamseasonReturn = await TeamSeason(teamname, seasonyear);
		if (teamseasonReturn[0] != undefined && teamseasonReturn[1] != undefined){
			var wins = parseInt(teamseasonReturn[0]['season_wins']);
			var losses = parseInt(teamseasonReturn[0]['season_losses']);
			var gp = wins + losses;

			const seasonEmbed = new EmbedBuilder().setTitle(TeamNameReturn(teamseasonReturn[1])).setColor(0xC70039)
			.addFields(
				{ name: 'Season', value: teamseasonReturn[0]['season_year'] },
				{ name: 'Wins', value: teamseasonReturn[0]['season_wins'] },
				{ name: 'Losses', value: teamseasonReturn[0]['season_losses'] },
				{ name: 'Games Played', value: gp.toString() },
				{ name: 'W/L%', value: teamseasonReturn[0]['season_wlp'] },
				{ name: 'Coach', value: teamseasonReturn[0]['season_coach'] }
			);
				
			await interaction.reply(
				{ embeds: [seasonEmbed]}
				);
			} else {
				await interaction.reply(
					"Team Name and/or Season Year Does Not Exist"
					);
			}
	}

	if (commandName === 'playerseason') {
		const playername = interaction.options.getString('player');
		const playerInfo = await Player(playername);
		if (playerInfo != undefined){
			const season = interaction.options.getString('season');
			var year = parseInt(season);
			var seasonYear = year.toString() +'-'+ (year + 1).toString().slice(2);
			const plSeason = playerSeason(playerInfo, seasonYear);
			if (plSeason != undefined){
				const pSeasonEmbed = new EmbedBuilder().setTitle(playerInfo['player_name'] +' '+ season).setColor(0xC70039)
				.addFields(
					{ name: 'Age', value: plSeason['stat_age'], inline: true },
					{ name: 'Position', value: plSeason['stat_pos'], inline: true },
					{ name: 'Games Played', value: plSeason['stat_g'], inline: true },
					{ name: 'Games Started', value: plSeason['stat_gs'], inline: true },
					{ name: 'Minutes', value: plSeason['stat_mp'], inline: true },
					{ name: 'FG %', value: plSeason['stat_fg'], inline: true },
					{ name: 'FG3 %', value: plSeason['stat_fg3'], inline: true },
					{ name: 'FG2 %', value: plSeason['stat_fg2'], inline: true },
					{ name: 'FT %', value: plSeason['stat_ftpct'], inline: true },
					{ name: 'Assists', value: plSeason['stat_ast'], inline: true },
					{ name: 'Rebounds', value: plSeason['stat_trb'], inline: true },
					{ name: 'Steals', value: plSeason['stat_stl'], inline: true },
					{ name: 'Points', value: plSeason['stat_pts'], inline: true },
				);
				await interaction.reply(
					{ embeds: [pSeasonEmbed]}
				);
			} else {
				await interaction.reply(
					"Season Does Not Exist"
				);
			}
		} else {
			await interaction.reply(
				"Player Does Not Exist"
			);
		}

	}

	if (commandName === 'playerplayoff') {
		const playername = interaction.options.getString('player');
		const playerInfo = await Player(playername);
		if (playerInfo != undefined){
			const playoff = interaction.options.getString('playoff');
			var year = parseInt(playoff);
			var playoffYear = year.toString() +'-'+ (year + 1).toString().slice(2);
			const plPlayoff = playerPlayoff(playerInfo, playoffYear);
			if (plPlayoff != undefined){
				const pPlayoffEmbed = new EmbedBuilder().setTitle(playerInfo['player_name'] +' '+ playoff).setColor(0xC70039)
				.addFields(
					{ name: 'Age', value: plPlayoff['stat_age'], inline: true },
					{ name: 'Position', value: plPlayoff['stat_pos'], inline: true },
					{ name: 'Games Played', value: plPlayoff['stat_g'], inline: true },
					{ name: 'Games Started', value: plPlayoff['stat_gs'], inline: true },
					{ name: 'Minutes', value: plPlayoff['stat_mp'], inline: true },
					{ name: 'FG', value: plPlayoff['stat_fg'], inline: true },
					{ name: 'FG3', value: plPlayoff['stat_fg3'], inline: true },
					{ name: 'FG2', value: plPlayoff['stat_fg2'], inline: true },
					{ name: 'FT %', value: plPlayoff['stat_ftpct'], inline: true },
					{ name: 'Assists', value: plPlayoff['stat_ast'], inline: true },
					{ name: 'Rebounds', value: plPlayoff['stat_trb'], inline: true },
					{ name: 'Steals', value: plPlayoff['stat_stl'], inline: true },
					{ name: 'Points', value: plPlayoff['stat_pts'], inline: true },
				);
				await interaction.reply(
					{ embeds: [pPlayoffEmbed]}
				);
			} else {
				await interaction.reply(
					"Season Does Not Exist"
				);
			}
		} else {
			await interaction.reply(
				"Player Does Not Exist"
			);
		}
	}
})

client.login(process.env.DISCORD_TOKEN);

function TeamNameReturn(teamname){
	const reg1 = /[a-z][A-Z]/g
	function replacer(match) {
		return match[0]+" "+match[1];
	}
	return teamname.replace(reg1, replacer)
}

async function TeamInputChecker(teamname){
	try {
		await mongo_client.connect();
		const Teams = await mongo_client.db('Requests').collection('Teams').find().toArray();
		var dict = {}
		Teams.forEach((result) => {
			dict = result
		});
		return dict[teamname.toLowerCase()];
 	} catch (error) {
		console.log("Error - TeamInputChecker")
	} finally {
        await mongo_client.close();
    }
}

async function PlayerInputChecker(playername){
	try {
		await mongo_client.connect();
		const Names = await mongo_client.db('Requests').collection('Names').find().toArray();
		var dict = {}
		Names.forEach((result) => {
			dict = result
		});
		return dict[playername.toLowerCase()];
 	} catch (error) {
		console.log("Error - PlayerInputChecker")
	} finally {
        await mongo_client.close();
    }
}

async function TeamInfo(teamname) {
    try {
		const team = await TeamInputChecker(teamname);
		await mongo_client.connect();
        const TeamInfo = mongo_client.db('TeamInfo');
        var Team = TeamInfo.collection(team).find();
        var data = await Team.toArray();
		var dict = {}
        data.forEach((result) => {
            dict = result
        })
		return dict;

    } catch (error) {
		console.log("Error - TeamInfo");
		return null;
	} finally {
        await mongo_client.close();
    }
}

async function TeamRoster(teamname) {
	try {
		const team = await TeamInputChecker(teamname);
        await mongo_client.connect();
        const Team = mongo_client.db(team);
        var Players = await Team.collection('Players').find().toArray();
		var Roster = []
        Players.forEach((player) => {
			Roster.push(player['player_name'])
		})
		return [Roster, team];
    } catch (error) {
		console.log("Error - TeamRoster")
	} finally {
        await mongo_client.close();
    }
}

async function Player(playername) {
	try {
		const player = await PlayerInputChecker(playername);
        await mongo_client.connect();
        const Teams = await mongo_client.db('TeamInfo').listCollections().toArray();
		var returnPlayer;
		await Promise.all(Teams.map(async (team) => {
			var Player = await mongo_client.db(team['name']).collection('Players').find({player_name: player}).toArray();
			if ( typeof Player[0] !== 'undefined'){
				returnPlayer = Player[0];
				return;
			}
		  }));
		return returnPlayer;

    } catch (error) {
		console.log("Error - Player");
		return null;
	} finally {
        await mongo_client.close();
    }
}

async function TeamSeason(teamname, seasonyear) {
	try {
		const team = await TeamInputChecker(teamname);
        await mongo_client.connect();
        const Team = mongo_client.db(team);
        var Seasons = await Team.collection('Seasons').find().toArray();
		var returnSeason;
		Seasons.forEach((season) => {
			if (season['season_year'] === seasonyear) {
				returnSeason = season;
			}
		})
		return [returnSeason, team];

    } catch (error) {
		console.log("Error - TeamSeason")
	} finally {
        await mongo_client.close();
    }
}

function playerSeason(playerInfo, seasonYear) {
	var seasons = playerInfo['Seasons'];
	var season = seasons[seasonYear];
	return season;
}

function playerPlayoff(playerInfo, playoffYear) {
	var playoffs = playerInfo['Playoffs'];
	var playoff = playoffs[playoffYear];
	return playoff;
}