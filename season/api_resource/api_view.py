from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from season.models import SeasonMatch, Season


def validate_season_year(func):
    """
    common validation for the season of the year
    handle from db season records (currently not implemented as we have static data set for input)

    future improvement needed:
        redis like cache to keep long life value until data set is not updated again. Always keep
        start season year and end season of the records. If any record season record is missing, result will go as empty

    cache required to handle validation. avoid multiple db hits to validation season year
    :param func:
    :return:
    """
    def func_validator(method=None, action_name=None, year=None):
        """
        validate year must be numeric
        validate year in between of season records. avoid db hits
        :param method
        :param action_name:
        :param year:
        :return:
        """
        # accept only numbers
        if not year.isnumeric():
            raise ValidationError(f'Season {year} must be a numeric type')
        # future improvement need to keep season year in cache memory to avoid db hits
        # currently having static data set so applied static validation.
        if not Season.objects.filter(year=int(year)).exists():
            raise ValidationError(f'Season {year} not available at our db')
        res = func(method, action_name, year)
        return res
    return func_validator


class SeasonMatchAPIResource:
    """
    Resource class act as API response and exception handler
    Handle serialization of output
    """
    model = SeasonMatch

    @validate_season_year
    def take_action(self, action_name, year):
        """
        business action logic registry
        :param action_name:
        :param year:
        :return:
        """
        year = int(year)
        if action_name == 'max_number_player_award':
            return Response(self.model.max_number_player_award(year))
        if action_name == 'highest_run_margin':
            return Response(self.model.highest_run_margin(year))
        if action_name == 'most_hosted_match_location':
            return Response(self.model.most_hosted_match_location(year))
        if action_name == 'team_bat_first':
            return Response(self.model.team_bat_first(year))
        if action_name == 'most_win_location':
            return Response(self.model.most_win_location(year))
        if action_name == 'get_top_1_teams':
            return Response(self.model.get_top_1_teams(year))
        if action_name == 'most_toss':
            return Response(self.model.most_toss(year))
        if action_name == 'get_top_4_teams':
            return Response(self.model.get_top_4_teams(year))
        if action_name == 'team_highest_wicket':
            return Response(self.model.team_highest_wicket(year))
        if action_name == 'team_won_by_highest_wickets':
            return Response(self.model.team_won_by_highest_wickets(year))
        if action_name == 'team_won_toss_matches':
            return Response(self.model.team_won_toss_matches(year))

    def perform_action(self, request, action_name, year):
        """
        :param request:
        :param action_name
        :param year:
        :return:
        """
        return self.take_action(action_name, year)


class StatsViewSet(viewsets.ViewSet):
    """

    """
    resource = SeasonMatchAPIResource()

    @action(detail=True,  methods=['get'])
    def get_top_4_teams(self, request, pk):
        """
        Top 4 teams in terms of wins
        end point: api/season/stats/{year}/get_top_4_teams/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='get_top_4_teams', year=pk)

    @action(detail=True,  methods=['get'])
    def most_toss(self, request, pk):
        """
        team won the most number of tosses in the season
        end point: api/season/stats/{year}/most_toss/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='most_toss', year=pk)

    @action(detail=True,  methods=['get'])
    def max_number_player_award(self, request, pk):
        """
        player won the maximum number of Player of the Match awards in the whole season
        end point: api/season/stats/{year}/max_number_player_award/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='max_number_player_award', year=pk)

    @action(detail=True,  methods=['get'])
    def get_top_1_teams(self, request, pk):
        """
        team won max matches in the whole season
        end point: api/season/stats/{year}/get_top_1_teams/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='get_top_1_teams', year=pk)

    @action(detail=True,  methods=['get'])
    def most_win_location(self, request, pk):
        """
        location has the most number of wins for the top team
        end point: api/season/stats/{year}/most_win_location/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='most_win_location', year=pk)

    @action(detail=True,  methods=['get'])
    def team_bat_first(self, request, pk):
        """
        % of teams decided to bat when they won the toss
        end point: api/season/stats/{year}/team_bat_first/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='team_bat_first', year=pk)

    @action(detail=True,  methods=['get'])
    def most_hosted_match_location(self, request, pk):
        """
        location hosted most number of matches
        end point: api/season/stats/{year}/most_hosted_match_location/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='most_hosted_match_location', year=pk)

    @action(detail=True,  methods=['get'])
    def highest_run_margin(self, request, pk):
        """
        team won by the highest margin of runs  for the season
        end point: api/season/stats/{year}/highest_run_margin/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='highest_run_margin', year=pk)

    @action(detail=True, methods=['get'])
    def team_highest_wicket(self, request, pk):
        """
        season teams total wickets
        end point: api/season/stats/{year}/team_highest_wicket/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='team_highest_wicket', year=pk)

    @action(detail=True, methods=['get'])
    def team_won_by_highest_wickets(self, request, pk):
        """
        team won by the highest number of wickets for the season
        end point: api/season/stats/{year}/team_won_by_highest_wickets/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='team_won_by_highest_wickets', year=pk)

    @action(detail=True, methods=['get'])
    def team_won_toss_matches(self, request, pk):
        """
        teams won the matches and toss both with their respective counts
        end point: api/season/stats/{year}/team_won_toss_matches/
        :param request:
        :param pk:
        :return:
        """
        return self.resource.perform_action(request=request, action_name='team_won_toss_matches', year=pk)
