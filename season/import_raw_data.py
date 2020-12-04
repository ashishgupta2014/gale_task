from season.models import Season, City, CityVenue, Team, Umpire, Player, TossDecision, MatchResult, WonBy, \
    SeasonMatch, SeasonTeamPlay, DismissalKind
import pandas as pd


class InitialDataProcessor:
    """"
    focus only insert new data set. expected no update on data set
    always insert new season with complete data set.
    support incremental season insert
    current logic written only handle complete season insert
    """
    def __init__(self, matches_path, deliveries_path):
        """

        :param matches_path:
        :param deliveries_path:
        """
        self.matches_df = pd.read_csv(matches_path)
        self.deliveries_df = pd.read_csv(deliveries_path)
        # used to insert match data set. contains all season hashmap respective to db
        self.seasons = dict()
        self.city_venues = dict()
        self.teams = dict()
        self.umpires = dict()
        self.players = dict()
        self.season_matches = dict()

    def save_season_year_from_matches(self):
        """

        :return:
        """
        # add all the seasons from matches
        # creating hashmap to handle subsequent insert of season
        self.seasons = {season.year: season for season in
                        Season.objects.bulk_create(
                            [Season(year=int(year)) for year in self.matches_df.season.unique()])}

    def save_city_venue_from_matches(self):
        """

        :return:
        """
        # add master set of all the cities
        cities_name = {city.name: city for city in
                       City.objects.bulk_create(
                           [City(name=name) for name in self.matches_df.city.unique() if isinstance(name, str)])}

        venues = list()
        # load city specific venue master set
        # create hashmap by concatenating city and venue to identify unique records
        for venue in pd.Series(self.matches_df['city'] + '__' + self.matches_df['venue']).unique():
            if isinstance(venue, str):
                city, stadium = venue.split('__')
                venues.append(CityVenue(city=cities_name[city], name=stadium))

        cities_id = {city.id: city.name for city in cities_name.values()}
        self.city_venues = {cities_id[venue.city.id] + '__' + venue.name: venue for venue in
                            CityVenue.objects.bulk_create(venues)}

    def save_team_from_matches(self):
        """

        :return:
        """
        # all teams played in all the season
        self.teams = {instance.name: instance for instance in Team.objects.bulk_create(
            [Team(name=team) for team in list(set(self.matches_df.team1.unique()) | set(self.matches_df.team2.unique()))
             if isinstance(team, str)])}

    def save_umpire_from_matches(self):
        """

        :return:
        """
        # combine all the 3 columns available in matches_df
        # manage uniqueness of the names while combining
        # create a db entry in bulk and return instance
        # all umpires participated across season of matches
        self.umpires = {instance.name: instance for instance in Umpire.objects.bulk_create(
            [Umpire(name=umpire) for umpire in list(
                set(self.matches_df.umpire1.unique()) | set(self.matches_df.umpire2.unique()) | set(
                    self.matches_df.umpire3.unique())) if isinstance(umpire, str)])}

    def save_player_from_matches_deliveries(self):
        """

        :return:
        """
        # combine all the player columns to create master set of player list from both data frames
        # manage uniqueness of the names while combining
        # all players names who has played across season
        self.players = {instance.name: instance for instance in Player.objects.bulk_create(
            [Player(name=player) for player in list(
                set(self.matches_df.player_of_match.unique()) | set(self.deliveries_df.batsman.unique()) | set(
                    self.deliveries_df.non_striker.unique()) | set(self.deliveries_df.bowler.unique()) | set(
                    self.deliveries_df.fielder.unique()) | set(self.deliveries_df.player_dismissed.unique())) if
             isinstance(player, str)])}

    def save_season_matches_from_matches(self):
        """

        :return:
        """
        matches = []
        toss_decision_mapper = TossDecision.get_reverse_choice_dict()
        match_result_mapper = MatchResult.get_reverse_choice_dict()
        for index, row in self.matches_df.iterrows():
            try:
                if isinstance(row['city'], str) and isinstance(row['venue'], str):
                    won_by = WonBy.Unknown.value
                    score = 0
                    if row['win_by_runs'] > 0:
                        won_by = WonBy.RUNS.value
                        score = row['win_by_runs']
                    elif row['win_by_wickets'] > 0:
                        won_by = WonBy.WICKETS.value
                        score = row['win_by_wickets']
                    matches.append(SeasonMatch(
                        csv_match_id=int(row['id']),
                        season=self.seasons[int(row['season'])],
                        venue=self.city_venues[row['city'] + '__' + row['venue']],
                        date=row['date'],
                        team_1=self.teams[row['team1']],
                        team_2=self.teams[row['team2']],
                        toss_won_by=self.teams[row['toss_winner']],
                        toss_decision=toss_decision_mapper[row['toss_decision'].strip().lower()],
                        result=match_result_mapper[row['result'].strip().lower()],
                        dl_applied=int(row['dl_applied']),
                        winner=self.teams[row['winner']] if isinstance(row['winner'], str) else None,
                        won_by=won_by,
                        score=score,
                        man_of_match=self.players[row['player_of_match']]
                        if isinstance(row['player_of_match'], str) else None,
                        umpire_1=self.umpires[row['umpire1']] if isinstance(row['umpire1'], str) else None,
                        umpire_2=self.umpires[row['umpire2']] if isinstance(row['umpire2'], str) else None,
                        umpire_3=self.umpires[row['umpire3']] if isinstance(row['umpire3'], str) else None
                    ))

            except Exception as ex:
                print(ex)

        self.season_matches = {match_record.csv_match_id: match_record for match_record in
                               SeasonMatch.objects.bulk_create(matches)}

    def save_deliveries_of_matches(self):
        """

        :return:
        """
        # inning, over and each boll delivery records
        deliveries = []
        for match_csv_id, season_match in self.season_matches.items():
            match_delivery = self.deliveries_df[self.deliveries_df.match_id == match_csv_id]
            for index, row in match_delivery.iterrows():
                dismissal_kind = DismissalKind.NOT_OUT.value
                csv_dismissal_kind = row['dismissal_kind'].strip().lower() if isinstance(row['dismissal_kind'],
                                                                                         str) else ''
                if csv_dismissal_kind == 'bowled':
                    dismissal_kind = DismissalKind.BOWLED.value
                if csv_dismissal_kind == 'caught':
                    dismissal_kind = DismissalKind.CAUGHT.value
                if csv_dismissal_kind == 'caught and bowled':
                    dismissal_kind = DismissalKind.CAUGHT_AND_BOWLED.value
                if csv_dismissal_kind == 'hit wicket':
                    dismissal_kind = DismissalKind.HIT_WICKET.value
                if csv_dismissal_kind == 'lbw':
                    dismissal_kind = DismissalKind.LBW.value
                if csv_dismissal_kind == 'obstructing the field':
                    dismissal_kind = DismissalKind.OBSTRUCTING_THE_FIELD.value
                if csv_dismissal_kind == 'retired hurt':
                    dismissal_kind = DismissalKind.RETIRED_HURT.value
                if csv_dismissal_kind == 'run out':
                    dismissal_kind = DismissalKind.RUN_OUT.value
                if csv_dismissal_kind == 'stumped':
                    dismissal_kind = DismissalKind.STUMPED.value

                deliveries.append(SeasonTeamPlay(
                    match=season_match,
                    inning=row['inning'],
                    over=row['over'],
                    ball=row['ball'],
                    batting_by=self.teams[row['batting_team']],
                    bowling_by=self.teams[row['bowling_team']],
                    batsman=self.players[row['batsman']],
                    bowler=self.players[row['bowler']],
                    non_striker=self.players[row['non_striker']],
                    is_super_over=row['is_super_over'],
                    wide_runs=row['wide_runs'],
                    bye_runs=row['bye_runs'],
                    leg_bye_runs=row['legbye_runs'],
                    no_ball_runs=row['noball_runs'],
                    penalty_runs=row['penalty_runs'],
                    batsman_runs=row['batsman_runs'],
                    extra_runs=row['extra_runs'],
                    dismissal_kind=dismissal_kind,
                    dismissed=self.players[row['player_dismissed']] if isinstance(row['player_dismissed'],
                                                                                  str) else None,
                    fielder=self.players[row['fielder']] if isinstance(row['fielder'], str) else None
                ))
        SeasonTeamPlay.objects.bulk_create(deliveries)

    def transform_input_save(self):
        """
        responsible to save season step by step
        :return:
        """
        self.save_season_year_from_matches()
        self.save_city_venue_from_matches()
        self.save_team_from_matches()
        self.save_umpire_from_matches()
        self.save_player_from_matches_deliveries()
        self.save_season_matches_from_matches()
        self.save_deliveries_of_matches()
