from ftplib import error_perm
from multiprocessing.resource_sharer import stop
import string
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

            # Avoid punctuation in txt file names
            txt_filename = player_name.translate(str.maketrans('', '', string.punctuation))

            with open(f'Teams/{dir}/Players/{player_name}/{txt_filename}.txt', 'w', encoding='utf-8') as f:
                print(player_name)
                f.write(player_name + '\n')
                f.write(player_link + '\n')
                f.write(player_pos + '\n')
                f.write(player_height + '\n')
                f.write(player_weight + '\n')
                f.write(player_yearsexp + '\n')
                f.write(player_college + '\n')

def player_info_puller():
    for dir in os.listdir('Teams'):
        for player_name in os.listdir(f'Teams/{dir}/Players'):
            txt_filename = player_name.translate(str.maketrans('', '', string.punctuation))
            with open(f'Teams/{dir}/Players/{player_name}/{txt_filename}.txt', 'r', encoding='utf-8') as f:
                player_info = f.readlines()
                player_link = player_info[1]

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

            try: 
                os.mkdir(f'C:/Users/Gurkarn/Desktop/CS Projects/NBA Web Scraper/Teams/{dir}/Players/{player_name}/Seasons')
                os.mkdir(f'C:/Users/Gurkarn/Desktop/CS Projects/NBA Web Scraper/Teams/{dir}/Players/{player_name}/Playoffs')
            except OSError as error: 
                print()

            if seasonal_data_exists:
                for season in seasonal_stats_table:
                    for stat in season.find_all():
                        match (stat.get('data-stat')):
                            case 'season':
                                stat_season = stat.text
                            case 'age':
                                stat_age = stat.text
                            case 'pos':
                                stat_pos = stat.text
                            case 'g':
                                stat_g = stat.text
                            case 'gs':
                                stat_gs = stat.text
                            case 'mp_per_g':
                                stat_mp = stat.text
                            case 'fg_per_g':
                                stat_fg = stat.text
                            case 'fga_per_g':
                                stat_fga = stat.text
                            case 'fg_pct':
                                stat_fgpct = stat.text
                            case 'fg3_per_g':
                                stat_fg3 = stat.text
                            case 'fg3a_per_g':
                                stat_fg3a = stat.text
                            case 'fg3_pct':
                                stat_fg3pct = stat.text
                            case 'fg2_per_g':
                                stat_fg2 = stat.text
                            case 'fg2a_per_g':
                                stat_fg2a = stat.text
                            case 'fg2_pct':
                                stat_fg2pct = stat.text
                            case 'efg_pct':
                                stat_efg = stat.text
                            case 'ft_per_g':
                                stat_ft = stat.text
                            case 'fta_per_g':
                                stat_fta = stat.text
                            case 'ft_pct':
                                stat_ftpct = stat.text
                            case 'orb_per_g':
                                stat_orb = stat.text
                            case 'drb_per_g':
                                stat_drb = stat.text
                            case 'trb_per_g':
                                stat_trb = stat.text
                            case 'ast_per_g':
                                stat_ast = stat.text
                            case 'stl_per_g':
                                stat_stl = stat.text
                            case 'blk_per_g':
                                stat_blk = stat.text
                            case 'tov_per_g':
                                stat_tov = stat.text
                            case 'pf_per_g':
                                stat_pf = stat.text
                            case 'pts_per_g':
                                stat_pts = stat.text
                    with open(f'Teams/{dir}/Players/{player_name}/Seasons/{stat_season}.txt', 'w', encoding='utf-8') as f:
                        f.write(stat_season + '\n')
                        f.write(stat_age + '\n')
                        f.write(stat_pos + '\n')
                        f.write(stat_g + '\n')
                        f.write(stat_gs + '\n')
                        f.write(stat_mp + '\n')
                        f.write(stat_fg + '\n')
                        f.write(stat_fga + '\n')
                        f.write(stat_fgpct + '\n')
                        f.write(stat_fg3 + '\n')
                        f.write(stat_fg3a + '\n')
                        f.write(stat_fg3pct + '\n')
                        f.write(stat_fg2 + '\n')
                        f.write(stat_fg2a + '\n')
                        f.write(stat_fg2pct + '\n')
                        f.write(stat_efg + '\n')
                        f.write(stat_ft + '\n')
                        f.write(stat_ftpct + '\n')
                        f.write(stat_orb + '\n')
                        f.write(stat_drb + '\n')
                        f.write(stat_trb + '\n')
                        f.write(stat_ast + '\n')
                        f.write(stat_stl + '\n')
                        f.write(stat_blk + '\n')
                        f.write(stat_tov + '\n')
                        f.write(stat_pf + '\n')
                        f.write(stat_pts + '\n')

            if playoff_data_exists:
                for playoff in playoff_stats_table:
                    for stat in playoff.find_all():
                        match (stat.get('data-stat')):
                            case 'season':
                                stat_season = stat.text
                            case 'age':
                                stat_age = stat.text
                            case 'pos':
                                stat_pos = stat.text
                            case 'g':
                                stat_games = stat.text
                            case 'gs':
                                stat_gstarted = stat.text
                            case 'mp_per_g':
                                stat_mp = stat.text
                            case 'fg_per_g':
                                stat_fg = stat.text
                            case 'fga_per_g':
                                stat_fga = stat.text
                            case 'fg_pct':
                                stat_fgpct = stat.text
                            case 'fg3_per_g':
                                stat_fg3 = stat.text
                            case 'fg3a_per_g':
                                stat_fg3a = stat.text
                            case 'fg3_pct':
                                stat_fg3pct = stat.text
                            case 'fg2_per_g':
                                stat_fg2 = stat.text
                            case 'fg2a_per_g':
                                stat_fg2a = stat.text
                            case 'fg2_pct':
                                stat_fg2pct = stat.text
                            case 'efg_pct':
                                stat_efg = stat.text
                            case 'ft_per_g':
                                stat_ft = stat.text
                            case 'fta_per_g':
                                stat_fta = stat.text
                            case 'ft_pct':
                                stat_ftpct = stat.text
                            case 'orb_per_g':
                                stat_orb = stat.text
                            case 'drb_per_g':
                                stat_drb = stat.text
                            case 'trb_per_g':
                                stat_trb = stat.text
                            case 'ast_per_g':
                                stat_ast = stat.text
                            case 'stl_per_g':
                                stat_stl = stat.text
                            case 'blk_per_g':
                                stat_blk = stat.text
                            case 'tov_per_g':
                                stat_tov = stat.text
                            case 'pf_per_g':
                                stat_pf = stat.text
                            case 'pts_per_g':
                                stat_pts = stat.text
                    with open(f'Teams/{dir}/Players/{player_name}/Playoffs/{stat_season}.txt', 'w', encoding='utf-8') as f:
                        f.write(stat_season + '\n')
                        f.write(stat_age + '\n')
                        f.write(stat_pos + '\n')
                        f.write(stat_g + '\n')
                        f.write(stat_gs + '\n')
                        f.write(stat_mp + '\n')
                        f.write(stat_fg + '\n')
                        f.write(stat_fga + '\n')
                        f.write(stat_fgpct + '\n')
                        f.write(stat_fg3 + '\n')
                        f.write(stat_fg3a + '\n')
                        f.write(stat_fg3pct + '\n')
                        f.write(stat_fg2 + '\n')
                        f.write(stat_fg2a + '\n')
                        f.write(stat_fg2pct + '\n')
                        f.write(stat_efg + '\n')
                        f.write(stat_ft + '\n')
                        f.write(stat_ftpct + '\n')
                        f.write(stat_orb + '\n')
                        f.write(stat_drb + '\n')
                        f.write(stat_trb + '\n')
                        f.write(stat_ast + '\n')
                        f.write(stat_stl + '\n')
                        f.write(stat_blk + '\n')
                        f.write(stat_tov + '\n')
                        f.write(stat_pf + '\n')
                        f.write(stat_pts + '\n')

if __name__ == '__main__':
    player_info_puller()