from ftplib import error_perm
from types import NoneType
from bs4 import BeautifulSoup
import requests
import os
from datetime import date

def team_info_puller():

    teams_page = requests.get('https://www.basketball-reference.com/teams/').text

    allteams_soup = BeautifulSoup(teams_page, 'lxml')

    activeteams = allteams_soup.find(id='div_teams_active')

    activeteams_main = activeteams.find_all(class_='full_table')

    for activeteam in activeteams_main:
        team_name = activeteam.find('th').text
        team_link = 'https://www.basketball-reference.com' + activeteam.find('th').a['href']
        team_data = activeteam.find_all(class_='right')
        for element in team_data:
            match (element['data-stat']):
                case 'year_min':
                    team_startyear = element.text
                case 'years':
                    team_lifespan = element.text
                case 'g':
                    team_games = element.text
                case 'wins':
                    team_wins = element.text
                case 'losses':
                    team_losses = element.text
                case 'win_loss_pct':
                    team_wlp = element.text
                case 'years_playoffs':
                    team_plyfs = element.text
                case 'years_division_champion':
                    team_divchamp = element.text
                case 'years_conference_champion':
                    team_confchamp = element.text
                case 'years_league_champion':
                    team_nbachamp = element.text
        with open(f'TeamInfo/{team_name}.txt','w') as f:
            f.write(team_name+'\n')
            f.write(team_link+'\n')
            f.write(team_startyear+'\n')
            f.write(team_lifespan+'\n')
            f.write(team_games+'\n')
            f.write(team_wins+'\n')
            f.write(team_losses+'\n')
            f.write(team_wlp+'\n')
            f.write(team_plyfs+'\n')
            f.write(team_divchamp+'\n')
            f.write(team_confchamp+'\n')
            f.write(team_nbachamp+'\n')

def team_season_info_puller():
    for root, dirs, files in os.walk('TeamInfo'):
        for file in files:
            with open(f'TeamInfo/{file}', 'r') as f:
                team_info = f.readlines()
                team_name = team_info[0].strip()
                team_link = team_info[1].strip()

            team_page = requests.get(team_link).text
            teamseasons_soup = BeautifulSoup(team_page, 'lxml')
            seasons = teamseasons_soup.find('tbody').find_all('tr')
            for season in seasons:
                if season.get('class') != 'thead':
                    season_info = season.find_all()
                    for info in season_info:
                        match (info.get('data-stat')):
                            case 'season' :
                                season_year = info.text
                                season_link = 'https://www.basketball-reference.com' + info.a['href']
                            case 'wins':
                                season_wins = info.text
                            case 'losses':
                                season_losses = info.text
                            case 'win_loss_pct':
                                season_wlp = info.text
                            case 'coaches':
                                season_coach = info.text
                    try: 
                        os.mkdir(f'C:/Users/Gurkarn/Desktop/CS Projects/NBA Web Scraper/Teams/{team_name}')
                        os.mkdir(f'C:/Users/Gurkarn/Desktop/CS Projects/NBA Web Scraper/Teams/{team_name}/Seasons')
                    except OSError as error: 
                        print()
                    with open(f'Teams/{team_name}/Seasons/{season_year}.txt', 'w') as f:
                        f.write(season_year+'\n')
                        f.write(season_link+'\n')
                        f.write(season_wins+'\n')
                        f.write(season_losses+'\n')
                        f.write(season_wlp+'\n')
                        f.write(season_coach+'\n')

def team_player_info_puller():
    for dir in os.listdir('Teams'):
        with open(f'Teams/{dir}/Seasons/{date.today().year}-{str(date.today().year + 1)[2:4]}.txt','r') as f:
            season_info = f.readlines()
            season_link = season_info[1].strip()

        current_season_page = requests.get(season_link).text
        current_season_soup = BeautifulSoup(current_season_page, 'lxml')
        season_roster = current_season_soup.find('table',id='roster').find('tbody').find_all('tr')
        
        try: 
            os.mkdir(f'C:/Users/Gurkarn/Desktop/CS Projects/NBA Web Scraper/Teams/{dir}/Players')
        except OSError as error: 
            print()

        for player in season_roster:
            player_info = player.find_all()
            for info in player_info:
                match (info.get('data-stat')):
                    case 'player':
                        player_name = info.text
                        player_link = 'https://www.basketball-reference.com' + info.a['href']
                    case 'pos':
                        player_pos = info.text
                    case 'height':
                        player_height = info.text
                    case 'weight':
                        player_weight = info.text
                    case 'years_experience':
                        player_yearsexp = info.text
                    case 'college':
                        player_college = info.text

            try: 
                os.mkdir(f'C:/Users/Gurkarn/Desktop/CS Projects/NBA Web Scraper/Teams/{dir}/Players/{player_name}')
            except OSError as error: 
                print()

            with open(f'Teams/{dir}/Players/{player_name}/{player_name}.txt', 'w', encoding='utf-8') as f:
                print(player_name)
                f.write(player_name + '\n')
                f.write(player_link + '\n')
                f.write(player_pos + '\n')
                f.write(player_height + '\n')
                f.write(player_weight + '\n')
                f.write(player_yearsexp + '\n')
                f.write(player_college + '\n')

if __name__ == '__main__':
    team_player_info_puller()