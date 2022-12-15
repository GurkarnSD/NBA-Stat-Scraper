const { REST, SlashCommandBuilder, Routes } = require('discord.js');
require('dotenv').config();

const commands = [
    new SlashCommandBuilder().setName('teams').setDescription('Replies with Teams')
        .addStringOption(option =>
            option.setName('team')
            .setDescription('Return Info About The Selected Team')
            .setRequired(true)),
    new SlashCommandBuilder().setName('player').setDescription('Returns a players stats')
        .addStringOption(option => 
            option.setName('player')
            .setDescription('Return Info About The Selected Player')
            .setRequired(true)),
    new SlashCommandBuilder().setName('roster').setDescription('Returns a teams current roster')
        .addStringOption(option => 
            option.setName('team')
            .setDescription('Return Roster of The Selected Team')
            .setRequired(true)),
    new SlashCommandBuilder().setName('teamseason').setDescription('Returns the stats of a team during the specified season')
        .addStringOption(option => 
            option.setName('team')
            .setDescription('Return Info About The Selected Team')
            .setRequired(true))
        .addStringOption(option => 
            option.setName('season')
            .setDescription('Return Info About The Selected Season')
            .setRequired(true)),
    new SlashCommandBuilder().setName('playerseason').setDescription('Returns the stats of a player during the specified season')
        .addStringOption(option => 
            option.setName('player')
            .setDescription('Return Info About The Selected Player')
            .setRequired(true))
        .addStringOption(option => 
            option.setName('season')
            .setDescription('Return Info About The Selected Season')
            .setRequired(true)),
    new SlashCommandBuilder().setName('playerplayoff').setDescription('Returns the stats of a player during the specified playoff')
        .addStringOption(option => 
            option.setName('player')
            .setDescription('Return Info About The Selected Player')
            .setRequired(true))
        .addStringOption(option => 
            option.setName('playoff')
            .setDescription('Return Info About The Selected Playoff')
            .setRequired(true))
]

    .map(command => command.toJSON());

const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
//Routes.applicationGuildCommands(process.env.clientId, process.env.guildId) - For Development
rest.put(Routes.applicationCommands(process.env.clientId), { body: commands })
    .then((data) => console.log(`Successfully registered ${data.length} application commands.`))
    .catch(console.error)