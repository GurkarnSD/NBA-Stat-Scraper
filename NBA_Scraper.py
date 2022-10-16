import string
from bs4 import BeautifulSoup
import requests
import os
from datetime import date
import pymongo
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

client = pymongo.MongoClient(os.getenv('MONGO_KEY'))
TeamInfo = client["TeamInfo"]
Teams = client["Teams"]

def team_info_puller():

    teams_page = requests.get('https://www.basketball-reference.com/teams/').text

    allteams_soup = BeautifulSoup(teams_page, 'lxml')

    activeteams = allteams_soup.find(id='div_teams_active')

    activeteams_main = activeteams.find_all(class_='full_table')

    for activeteam in activeteams_main:
        team_name = activeteam.find('th').text
        team_link = 'https://www.basketball-reference.com' + activeteam.find('th').a['href']

        team_page = requests.get(team_link).text
        team_soup = BeautifulSoup(team_page, 'lxml')
        team_logo = team_soup.find(class_="teamlogo")['src']

        team_data = activeteam.find_all(class_='right')
        post = {}
        post["team_logo"] = team_logo
        post["team_link"] = team_link
        
        for element in team_data:
            match (element['data-stat']):
                case 'year_min':
                    post["team_startyear"] = element.text
                case 'years':
                    post["team_lifespan"] = element.text
                case 'g':
                    post["team_games"] = element.text
                case 'wins':
                    post["team_wins"] = element.text
                case 'losses':
                    post["team_losses"] = element.text
                case 'win_loss_pct':
                    post["team_wlp"] = element.text
                case 'years_playoffs':
                    post["team_plyfs"] = element.text
                case 'years_division_champion':
                    post["team_divchamp"] = element.text
                case 'years_conference_champion':
                    post["team_confchamp"] = element.text
                case 'years_league_champion':
                    post["team_nbachamp"] = element.text
        
        collection = TeamInfo[f"{team_name}"]
        collection.insert_one(post)

def team_season_info_puller():
    collections = TeamInfo.list_collection_names()
    for c in collections:
        team_name = c
        team_info = TeamInfo.get_collection(c).find_one()
        team_link = team_info.get("team_link")
        team_page = requests.get(team_link).text
        teamseasons_soup = BeautifulSoup(team_page, 'lxml')
        seasons = teamseasons_soup.find('tbody').find_all('tr')
        
        for season in seasons:
            post = {}
            if season.get('class') != 'thead':
                season_info = season.find_all()
                for info in season_info:
                    match (info.get('data-stat')):
                        case 'season' :
                            post["season_year"] = info.text
                            post["season_link"] = 'https://www.basketball-reference.com' + info.a['href']
                        case 'wins':
                            post["season_wins"] = info.text
                        case 'losses':
                            post["season_losses"] = info.text
                        case 'win_loss_pct':
                            post["season_wlp"] = info.text
                        case 'coaches':
                            post["season_coach"] = info.text

                db = client[team_name.replace(" ", "")]
                collection = db["Seasons"]
                collection.insert_one(post)

def team_player_info_puller():
    collections = TeamInfo.list_collection_names()
    for team_name in collections:
        db = client[team_name.replace(" ", "")]
        collection = db["Seasons"]
        season = f"{date.today().year}-{str(date.today().year + 1)[2:4]}"
        season_info = collection.find_one({"season_year": season})
        season_link = season_info["season_link"]
        collection = db["Players"]

        current_season_page = requests.get(season_link).text
        current_season_soup = BeautifulSoup(current_season_page, 'lxml')
        season_roster = current_season_soup.find('table',id='roster').find('tbody').find_all('tr')

        for player in season_roster:
            post = {}
            player_info = player.find_all()
            for info in player_info:
                match (info.get('data-stat')):
                    case 'player':
                        post["player_name"] = info.text
                        player_link = 'https://www.basketball-reference.com' + info.a['href']
                        post["player_link"] = player_link
                        player_page = requests.get(player_link.strip()).text
                        player_page_soup = BeautifulSoup(player_page, 'lxml')
                        try:
                            post['player_img'] = player_page_soup.find(class_='media-item').img['src']
                        except:
                            post['player_img'] = 'NoImage'
                    case 'pos':
                        post["player_pos"] = info.text
                    case 'height':
                        post["player_height"] = info.text
                    case 'weight':
                        post["player_weight"] = info.text
                    case 'years_experience':
                        post["player_yearsexp"] = info.text
                    case 'college':
                        post["player_college"] = info.text

            collection.insert_one(post)

def player_info_puller():
    collections = TeamInfo.list_collection_names()
    for team_name in collections:
        db = client[team_name.replace(" ", "")]
        collection = db.Players.find()
        for player_info in collection:
            player_name = player_info.get("player_name")
            player_link = player_info.get("player_link")

            player_page = requests.get(player_link.strip()).text
            player_page_soup = BeautifulSoup(player_page, 'lxml')

            seasonal_data_exists = True
            playoff_data_exists = True

            try:
                seasonal_stats_table = player_page_soup.find('table', id='per_game').find('tbody').find_all('tr')
            except AttributeError as error:
                seasonal_data_exists = False

            try:
                playoff_stats_table = player_page_soup.find('table', id='playoffs_per_game').find('tbody').find_all('tr')
            except AttributeError as error:
                playoff_data_exists = False

            collection = db["Players"]

            if seasonal_data_exists:
                seasons = {}
                for season in seasonal_stats_table:
                    post = {}
                    for stat in season.find_all():
                        match (stat.get('data-stat')):
                            case 'season':
                                stat_season = stat.text
                            case 'age':
                                post["stat_age"] = stat.text
                            case 'pos':
                                post["stat_pos"] = stat.text
                            case 'g':
                                post["stat_g"] = stat.text
                            case 'gs':
                                post["stat_gs"] = stat.text
                            case 'mp_per_g':
                                post["stat_mp"] = stat.text
                            case 'fg_per_g':
                                post["stat_fg"] = stat.text
                            case 'fga_per_g':
                                post["stat_fga"] = stat.text
                            case 'fg_pct':
                                post["stat_fgpct"] = stat.text
                            case 'fg3_per_g':
                                post["stat_fg3"] = stat.text
                            case 'fg3a_per_g':
                                post["stat_fg3a"] = stat.text
                            case 'fg3_pct':
                                post["stat_fg3pct"] = stat.text
                            case 'fg2_per_g':
                                post["stat_fg2"] = stat.text
                            case 'fg2a_per_g':
                                post["stat_fg2a"] = stat.text
                            case 'fg2_pct':
                                post["stat_fg2pct"] = stat.text
                            case 'efg_pct':
                                post["stat_efg"] = stat.text
                            case 'ft_per_g':
                                post["stat_ft"] = stat.text
                            case 'fta_per_g':
                                post["stat_fta"] = stat.text
                            case 'ft_pct':
                                post["stat_ftpct"] = stat.text
                            case 'orb_per_g':
                                post["stat_orb"] = stat.text
                            case 'drb_per_g':
                                post["stat_drb"] = stat.text
                            case 'trb_per_g':
                                post["stat_trb"] = stat.text
                            case 'ast_per_g':
                                post["stat_ast"] = stat.text
                            case 'stl_per_g':
                                post["stat_stl"] = stat.text
                            case 'blk_per_g':
                                post["stat_blk"] = stat.text
                            case 'tov_per_g':
                                post["stat_tov"] = stat.text
                            case 'pf_per_g':
                                post["stat_pf"] = stat.text
                            case 'pts_per_g':
                                post["stat_pts"] = stat.text
                    seasons[stat_season] = post
                
                player_info["Seasons"] = seasons

            if playoff_data_exists:
                playoffs = {}
                for playoff in playoff_stats_table:
                    post = {}
                    for stat in playoff.find_all():
                        match (stat.get('data-stat')):
                            case 'season':
                                stat_season = stat.text
                            case 'age':
                                post["stat_age"] = stat.text
                            case 'pos':
                                post["stat_pos"] = stat.text
                            case 'g':
                                post["stat_g"] = stat.text
                            case 'gs':
                                post["stat_gs"] = stat.text
                            case 'mp_per_g':
                                post["stat_mp"] = stat.text
                            case 'fg_per_g':
                                post["stat_fg"] = stat.text
                            case 'fga_per_g':
                                post["stat_fga"] = stat.text
                            case 'fg_pct':
                                post["stat_fgpct"] = stat.text
                            case 'fg3_per_g':
                                post["stat_fg3"] = stat.text
                            case 'fg3a_per_g':
                                post["stat_fg3a"] = stat.text
                            case 'fg3_pct':
                                post["stat_fg3pct"] = stat.text
                            case 'fg2_per_g':
                                post["stat_fg2"] = stat.text
                            case 'fg2a_per_g':
                                post["stat_fg2a"] = stat.text
                            case 'fg2_pct':
                                post["stat_fg2pct"] = stat.text
                            case 'efg_pct':
                                post["stat_efg"] = stat.text
                            case 'ft_per_g':
                                post["stat_ft"] = stat.text
                            case 'fta_per_g':
                                post["stat_fta"] = stat.text
                            case 'ft_pct':
                                post["stat_ftpct"] = stat.text
                            case 'orb_per_g':
                                post["stat_orb"] = stat.text
                            case 'drb_per_g':
                                post["stat_drb"] = stat.text
                            case 'trb_per_g':
                                post["stat_trb"] = stat.text
                            case 'ast_per_g':
                                post["stat_ast"] = stat.text
                            case 'stl_per_g':
                                post["stat_stl"] = stat.text
                            case 'blk_per_g':
                                post["stat_blk"] = stat.text
                            case 'tov_per_g':
                                post["stat_tov"] = stat.text
                            case 'pf_per_g':
                                post["stat_pf"] = stat.text
                            case 'pts_per_g':
                                post["stat_pts"] = stat.text
                    playoffs[stat_season] = post
                
                player_info["Playoffs"] = playoffs
            
            newvalues = { "$set": player_info}
            filter = { "player_name": player_name}
            collection.update_one(filter, newvalues)            

def drop_databases():
    db_list = client.list_database_names()
    for db in db_list:
        try:
            print("Dropping: ", db)
            client.drop_database(db)
        except:
            print("Error")

if __name__ == '__main__':
    drop_databases()
    team_info_puller()
    team_season_info_puller()
    team_player_info_puller()
    player_info_puller()