from enum import Enum
from django.db import models
from django.db.models import Count, F, Sum
from django.db.models.aggregates import Max


class Choice(Enum):
    """
    Class for defining choices.
    """

    @classmethod
    def get_choice_name(cls, value):
        return dict(cls.CHOICES.value)[value]

    @classmethod
    def get_choices(cls):
        return list(cls.CHOICES.value)

    @classmethod
    def get_choice_value(cls, name):
        for i in cls.get_choices():
            if i[1].lower() == name.lower():
                return i[0]
        return name

    @classmethod
    def get_reverse_choice_dict(cls):
        return {i[1].lower(): i[0] for i in cls.CHOICES.value}


class Player(models.Model):
    """
    Players Master set
    """
    name = models.CharField(max_length=50, unique=True)


class Umpire(models.Model):
    """
    Umpires Master set
    """
    name = models.CharField(max_length=50, unique=True)


class City(models.Model):
    """
    City Master set
    """
    name = models.CharField(max_length=50, unique=True)


class CityVenue(models.Model):
    """
    City Venue Master set
    """
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)


class Season(models.Model):
    """
    IPL season
    """
    year = models.IntegerField(unique=True)


class Team(models.Model):
    """
    Season Teams
    """
    name = models.CharField(max_length=50, unique=True)


class TossDecision(Choice):
    """

    """
    BAT = 1
    FIELD = 2
    Unknown = 0

    CHOICES = (
        (BAT, 'Bat'),
        (FIELD, 'Field'),
        (Unknown, 'Bad Data')
    )

    default = Unknown


class MatchResult(Choice):
    """

    """
    NORMAL = 1
    TIE = 2
    NO_RESULT = 0

    CHOICES = (
        (NORMAL, 'Normal'),
        (TIE, 'Tie'),
        (NO_RESULT, 'No Result')
    )

    default = NORMAL


class WonBy(Choice):
    """

    """
    Unknown = 0
    RUNS = 1
    WICKETS = 2

    CHOICES = (
        (RUNS, 'Runs'),
        (WICKETS, 'Wickets'),
        (Unknown, 'Unknown')

    )

    default = RUNS


class SeasonMatch(models.Model):
    """
    Season Match Details
    """
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    venue = models.ForeignKey(CityVenue, on_delete=models.SET_NULL, related_name='match_location', null=True)
    date = models.DateField()
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_team1')
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_team2')
    toss_won_by = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_toss_won')
    toss_decision = models.IntegerField(choices=TossDecision.get_choices(),
                                        default=TossDecision.default.value)
    result = models.IntegerField(choices=MatchResult.get_choices(), default=MatchResult.default.value)
    dl_applied = models.IntegerField(default=0)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, related_name='team_won', null=True)
    won_by = models.IntegerField(choices=WonBy.get_choices(), default=MatchResult.default.value)
    score = models.IntegerField(default=0)
    man_of_match = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    umpire_1 = models.ForeignKey(Umpire, on_delete=models.SET_NULL, null=True, blank=True, related_name='first_umpire')
    umpire_2 = models.ForeignKey(Umpire, on_delete=models.SET_NULL, null=True, blank=True, related_name='second_umpire')
    umpire_3 = models.ForeignKey(Umpire, on_delete=models.SET_NULL, null=True, blank=True, related_name='third_umpire')
    csv_match_id = models.IntegerField()  # needed to handle import logic of deliveries

    @staticmethod
    def most_toss(year):
        """
        team won the most number of tosses in the season
        :param year:
        :return:
        """

        qs = SeasonMatch.objects.filter(season__year=year)
        qs = qs.values('toss_won_by__name').annotate(count=Count('toss_won_by')).order_by('-count')
        return qs[:1]

    @staticmethod
    def get_top_4_teams(year):
        """
        Top 4 teams in terms of wins
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year, result=MatchResult.NORMAL.value)
        qs = qs.values('winner__name').annotate(count=Count('winner')).order_by('-count')
        return qs[:4]

    @staticmethod
    def max_number_player_award(year):
        """
        player won the maximum number of Player of the Match awards in the whole season
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year)
        qs = qs.values('man_of_match__name').annotate(count=Count('man_of_match')).order_by('-count')
        if len(qs) > 1:
            last_record = qs[0]
            res = list(filter(lambda x: last_record['count'] == x['count'], qs))
            return res
        return list(qs)

    @staticmethod
    def get_top_1_teams(year):
        """
        team won max matches in the whole season
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year, result=MatchResult.NORMAL.value)
        qs = qs.values('winner__name').annotate(count=Count('winner')).order_by('-count')
        return qs[:1]

    @staticmethod
    def most_win_location(year):
        """
        location has the most number of wins for the top team
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year, result=MatchResult.NORMAL.value)
        qs = qs.values('venue__name', 'winner__name').annotate(count=Count('winner')).order_by('-count')
        return qs[:1]

    @staticmethod
    def team_bat_first(year):
        """
         % of teams decided to bat when they won the toss
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.values('toss_won_by')
        only_bat = qs.filter(season__year=year, toss_decision=TossDecision.BAT.value).count()
        bat_and_ball = qs.filter(season__year=year,
                                 toss_decision__in=[TossDecision.BAT.value, TossDecision.FIELD.value]).count()
        if bat_and_ball > 0:
            return {'percent_team_decided_bat_first': round((only_bat * 100) / bat_and_ball, 2)}
        return {'percent_team_decided_bat_first': 0}

    @staticmethod
    def most_hosted_match_location(year):
        """
        location hosted most number of matches
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year)
        qs = qs.values('venue__name').annotate(count=Count('venue')).order_by('-count')
        return qs[:1]

    @staticmethod
    def highest_run_margin(year):
        """
        team won by the highest margin of runs  for the season
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year, won_by=WonBy.RUNS.value)
        margin = qs.aggregate(margin=Max('score'))
        return qs.filter(score=margin['margin']).values('winner__name', 'score')

    @staticmethod
    def team_highest_wicket(year):
        """
        season teams total wickets
        :param year:
        :return:
        """
        wickets = list(DismissalKind.get_reverse_choice_dict().values())
        wickets.pop(DismissalKind.NOT_OUT.value)
        qs = SeasonTeamPlay.objects.filter(match__season__year=year, dismissal_kind__in=wickets)
        qs = qs.values('bowling_by__name').annotate(count=Count('pk')).order_by('-count')
        return qs

    @staticmethod
    def team_won_by_highest_wickets(year):
        """
        team won by the highest number of wickets for the season
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year, won_by=WonBy.WICKETS.value)
        wickets = qs.aggregate(wickets=Max('score'))
        return qs.filter(score=wickets['wickets']).values('winner__name', 'score')

    @staticmethod
    def team_won_toss_matches(year):
        """
        teams won the matches and toss both with their respective counts
        :param year:
        :return:
        """
        qs = SeasonMatch.objects.filter(season__year=year, result=MatchResult.NORMAL.value)
        qs_win_toss = qs.values_list('toss_won_by__id', flat=True).distinct()
        qs = SeasonMatch.objects.filter(season__year=year, result=MatchResult.NORMAL.value,
                                        winner__id__in=list(qs_win_toss))
        return qs.values('winner__name').annotate(count=Count('pk')).order_by('-count')


class DismissalKind(Choice):
    """

    """
    NOT_OUT = 0
    BOWLED = 1
    CAUGHT = 2
    CAUGHT_AND_BOWLED = 3
    LBW = 4
    RUN_OUT = 5
    STUMPED = 6
    HIT_WICKET = 7
    OBSTRUCTING_THE_FIELD = 8
    RETIRED_HURT = 9

    CHOICES = (
        (NOT_OUT, 'Not Out'),
        (BOWLED, 'Bowled'),
        (CAUGHT, 'Caught'),
        (CAUGHT_AND_BOWLED, 'Caught and Bowled'),
        (LBW, 'Leg Bowled Wicket'),
        (RUN_OUT, 'Run Out'),
        (STUMPED, 'Stumped'),
        (HIT_WICKET, 'Hit Wicket'),
        (OBSTRUCTING_THE_FIELD, 'Obstructing The Field'),
        (RETIRED_HURT, 'Retired Hurt'),
    )

    default = NOT_OUT


class SeasonTeamPlay(models.Model):
    """
    Season specific Team Play of batting and bowling
    """
    match = models.ForeignKey(SeasonMatch, on_delete=models.CASCADE)
    inning = models.IntegerField()
    batting_by = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='batting_team')
    bowling_by = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='bowling_team')
    over = models.IntegerField()
    ball = models.IntegerField()
    batsman = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player_batsman')
    bowler = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player_bowler')
    non_striker = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='player_non_striker')
    is_super_over = models.BooleanField(default=False)
    wide_runs = models.IntegerField(default=0)
    bye_runs = models.IntegerField(default=0)
    leg_bye_runs = models.IntegerField(default=0)
    no_ball_runs = models.IntegerField(default=0)
    penalty_runs = models.IntegerField(default=0)
    batsman_runs = models.IntegerField(default=0)
    extra_runs = models.IntegerField(default=0)
    dismissal_kind = models.IntegerField(choices=DismissalKind.get_choices(), default=DismissalKind.default.value)
    dismissed = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='player_dismissed')
    fielder = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='player_fielder')
