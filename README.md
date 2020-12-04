# GALE Exercise
@Author: Ashish Gupta


## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [API End Points](#api-end-points)

## General info
Project has IPL Match Season dataset from 2009 to 2017. Its provide various end points to show case the stats of each season. Season name considered as year which will be input parameter to get various types of stats.

## Technologies
* Python >= 3.6
* Django Framework (API web server)
* Postgres SQL (DB Storage)
* Django ORM (CRUD operations)
* Django Rest Framework (helps to valiadate and serialize data)

## Setup
Setup explains about ubuntu os
* Commands

  install postgresql
  
  $sudo apt install postgresql postgresql-contrib
  
  create db named: ipl_season_db 
  
  create user postgres with password postgres (all permissions to access db)
  
  if you want to use different dbname than modify djangoProject_test/settings.py file
  
  DATABASES = {
  
    'default': {
    
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        
        'NAME': 'ipl_season_db', # change db name
        
        'USER': 'postgres', # change user
        
        'PASSWORD': 'postgres', # change password
        
    }
    
}


  Create virtual env basis on above technology versions
  
  $python3 -m venv gale_task_env
  
  activate the env
  
  $source gale_task_env/bin/activate
  
  clone the project on specific folder structure
  
  $git clone https://github.com/ashishgupta2014/gale_task.git
  
  install dependencies
  
  $ cd gale_task
  
  $ pip install -r requirements.txt
  
  $ python manage.py migrate
  
  $ python manage.py runserver 0.0.0.0:9002
 
 
 
 ## API End Points
 {year} value need to be pass from 2009 to 2017
 * Top 4 teams in terms of wins
 
   end point: api/season/stats/{year}/get_top_4_teams/
 
 * Team won the most number of tosses in the season
 
   end point: api/season/stats/{year}/most_toss/
        
* player won the maximum number of Player of the Match awards in the whole season

  end point: api/season/stats/{year}/max_number_player_award/
  
* team won max matches in the whole season

  end point: api/season/stats/{year}/get_top_1_teams/
 
* location has the most number of wins for the top team

  end point: api/season/stats/{year}/most_win_location/
  
* % of teams decided to bat when they won the toss

  end point: api/season/stats/{year}/team_bat_first/
  
* location hosted most number of matches

  end point: api/season/stats/{year}/most_hosted_match_location/
  
  
* team won by the highest margin of runs  for the season

  end point: api/season/stats/{year}/highest_run_margin/
  
* season teams total wickets

  end point: api/season/stats/{year}/team_highest_wicket/
  
* team won by the highest number of wickets for the season

  end point: api/season/stats/{year}/team_won_by_highest_wickets/ 
  
* teams won the matches and toss both with their respective counts

  end point: api/season/stats/{year}/team_won_toss_matches/
  
  
