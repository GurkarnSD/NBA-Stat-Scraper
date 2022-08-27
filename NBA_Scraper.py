from types import NoneType
from bs4 import BeautifulSoup
import requests

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
        with open(f'TeamStats/{team_name}.txt','w') as f:
            f.write(team_name)
            f.write('\n'+team_link)
            f.write('\n'+team_startyear)
            f.write('\n'+team_lifespan)
            f.write('\n'+team_games)
            f.write('\n'+team_wins)
            f.write('\n'+team_losses)
            f.write('\n'+team_wlp)
            f.write('\n'+team_plyfs)
            f.write('\n'+team_divchamp)
            f.write('\n'+team_confchamp)
            f.write('\n'+team_nbachamp)

if __name__ == '__main__':
    team_info_puller()
