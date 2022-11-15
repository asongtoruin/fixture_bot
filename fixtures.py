from datetime import datetime
import json
from urllib.request import Request, urlopen

from PIL import Image, ImageDraw

from images import TextDraw, scale_from_url
from params import HEADERS


FORM_COLOURS = {
    'W': (85,172,238,255),
    'D': (253,203,88,255),
    'L': (221,46,68,255),
    'U': (49,55,61,255)
}

DAY_COLOURS = {
    0: (2, 8, 135, 255),
    1: (1, 38, 34, 255),
    2: (229, 83, 129, 255),
    3: (20, 123, 49, 255),
    4: (91, 78, 119, 255),
    5: (243, 66, 19, 255),
    6: (229, 83, 129, 255)
}

class Team:
    """Data class for team data
    """
    def __init__(self, team_data):
        self.name = team_data['team_name']
        self.id = team_data['team_id']
        self.badge = team_data.get('logo', None)
        
    def form(self, matches=5):
        form_url = (
            f'https://api-football-v1.p.rapidapi.com/v2/fixtures/team/'
            f'{self.id}/last/{matches}'
        )

        # Load up the fixtures
        form_req = Request(form_url, headers=HEADERS)
        form_content = urlopen(form_req).read()
        data = json.loads(form_content)

        fixtures = [Fixture(f) for f in data['api']['fixtures']]
        fixtures.sort(key=lambda f: f.datetime)
        
        return (f.result(self) for f in fixtures)
        
    def __eq__(self, other):
        return self.id == other.id
        

class Fixture:
    BADGE_LOOKUPS = {
        42: '<:afc:735119993175277578>',      # Arsenal
        63: '<:leeds:735122574920384542>',    # Leeds
        1373: '<:lofc:735119992978407525>',   # Leyton Orient
        50: '<:mcfc:735119993645039676>',     # Manchester City
        34: '<:nufc:753175503992651826>',     # Newcastle
        1351: '<:pvfc:735119353367887922>',   # Port Vale
        41: '<:sfc:735119993510953051>',      # Southampton
        75: '<:scfc:761638560281264149>',     # The neighbours
    }
    def __init__(self, data_dict):
        self._data = data_dict
        self.datetime = datetime.fromtimestamp(data_dict['event_timestamp'])
        self.home_team = Team(data_dict['homeTeam'])
        self.away_team = Team(data_dict['awayTeam'])
        self.venue = data_dict['venue']
        self.competition = data_dict['league']['name']
        self.status = data_dict['statusShort']
    
    @property
    def inactive(self):
        return self.status in ('PST', 'CANC', 'ABD', 'AWD', 'WO')

    @property
    def is_today(self):
        """Checks whether a fixture is taking place on the current day.

        Returns:
            bool: True if the match is taking place on the current day and not 
                  postponed, cancelled, abandoned etc, else False
        """
        return (
            self.datetime.date() == datetime.now().date()
            and not self.inactive
        )
    
    @property
    def description(self):
        """Gives description text for the fixture with emoji codes for given teams 

        Returns:
            str: match description string including teams, time and competition.
        """
        home_msg = Fixture.BADGE_LOOKUPS.get(
            self.home_team.id, self.home_team.name
        )
        
        home_form = self.home_team.form()
        away_msg = Fixture.BADGE_LOOKUPS.get(
            self.away_team.id, self.away_team.name
        )
        away_form = self.away_team.form()
        start_time = self.datetime.strftime('%H:%M')
        return (
            f'{home_msg} ({home_form}) vs {away_msg} ({away_form}) '
            f'@ {start_time} ({self.competition})'
        )
    
    def result(self, team: Team):
        if self.home_team == team:
            us, them = 'Home', 'Away'
        elif self.away_team == team:
            us, them = 'Away', 'Home'
        else:
            raise ValueError('Team not involved')
        
        if self.inactive:
            return 'U'
        
        try:
            if self._data[f'goals{us}Team'] > self._data[f'goals{them}Team']:
                return 'W'
            elif self._data[f'goals{us}Team'] < self._data[f'goals{them}Team']:
                return 'L'
            else:
                return 'D'
        except TypeError:
            return 'U'

    def draw_card(self, font_path, header_height=50, badge_size=200, pad=10, 
                  inner_gap=60, form_count=10, form_outline=2, text_scale=10):
        if form_count > 0:
            form_size = int(badge_size / form_count)
        else:
            form_size = 0

        image_width = 4*pad + 2*badge_size + inner_gap
        image_height = 4*pad + header_height + badge_size + form_size

        img = Image.new(
            mode='RGBA', size=(image_width, image_height), color=(0, 0, 0, 0)
        )
        draw = ImageDraw.Draw(img)

        # Separate text layer, scaled up for better antialiasing
        text_layer = Image.new(
            mode='RGBA', 
            size=(image_width * text_scale, image_height * text_scale), 
            color=(0, 0, 0, 0)
        )
        text_draw = TextDraw(text_layer)

        # Header fill
        h_colour = DAY_COLOURS.get(self.datetime.weekday(), DAY_COLOURS[0])
        h_x0 = h_y0 = pad
        h_x1 = image_width - pad
        h_y1 = h_y0 + header_height
        draw.rectangle(xy=[h_x0, h_y0, h_x1, h_y1], fill=h_colour, width=4)

        # Header text
        header = f'{self.competition}\n{self.venue or ""} @ {self.datetime.strftime("%H:%M")}'
        text_draw.align_text(
            header, 
            h_x0 * text_scale, (h_y0+5) * text_scale, 
            h_x1 * text_scale, (h_y1-5) * text_scale, 
            font_path=font_path, align='center'
        )

        # Home badge
        hb_x0 = pad
        hb_x1 = hb_x0 + badge_size
        hb_y0 = h_y1 + pad
        hb_y1 = hb_y0 + badge_size
        badge, x, y = scale_from_url(
            self.home_team.badge, hb_x0, hb_y0, hb_x1, hb_y1
        )
        img.paste(badge, (x, y), badge.convert('RGBA'))

        if form_count > 0:
            # Home form
            hf_x0 = hb_x0
            hf_x1 = hb_x1
            hf_y0 = hb_y1 + pad
            hf_y1 = hf_y0 + form_size

            for f in self.home_team.form(matches=form_count):
                hf_x1 = hf_x0 + form_size
                hf_y1 = hf_y0 + form_size
                draw.rectangle(
                    xy=[hf_x0, hf_y0, hf_x1, hf_y1], 
                    fill=FORM_COLOURS[f], outline=(0,0,0,0), width=form_outline
                )
                text_draw.align_text(
                    f, 
                    (hf_x0+form_outline)*text_scale, (hf_y0+form_outline)*text_scale, 
                    (hf_x1-form_outline)*text_scale, (hf_y1-form_outline)*text_scale, 
                    font_path=font_path, align='center', fill=(255, 255, 255, 100)
                )
                hf_x0 += form_size

        # Away badge
        ab_x0 = hb_x1 + 2*pad+ inner_gap
        ab_x1 = ab_x0 + badge_size
        ab_y0 = hb_y0
        ab_y1 = hb_y1
        badge, x, y = scale_from_url(
            self.away_team.badge, ab_x0, ab_y0, ab_x1, ab_y1
        )
        img.paste(badge, (x, y), badge.convert('RGBA'))

        if form_count > 0:
            # Away form
            af_x0 = ab_x0
            af_x1 = ab_x1
            af_y0 = ab_y1 + pad
            af_y1 = af_y0 + form_size

            for f in self.away_team.form(matches=form_count):
                af_x1 = af_x0 + form_size
                af_y1 = af_y0 + form_size
                draw.rectangle(
                    xy=[af_x0, af_y0, af_x1, af_y1], 
                    fill=FORM_COLOURS[f], outline=(0,0,0,0), width=form_outline
                )
                text_draw.align_text(
                    f, 
                    (af_x0+form_outline)*text_scale, (af_y0+form_outline)*text_scale, 
                    (af_x1-form_outline)*text_scale, (af_y1-form_outline)*text_scale, 
                    font_path=font_path, align='center', fill=(255, 255, 255, 100)
                )
                af_x0 += form_size

        # vs text
        text_draw.align_text(
            'VS', 
            (hb_x1+pad) * text_scale, hb_y0 * text_scale, 
            (ab_x0-pad) * text_scale, ab_y1 * text_scale, 
            font_path=font_path, align='center', fill=(127, 127, 127, 80)
        )

        # Scale down image
        text_layer = text_layer.resize((image_width, image_height))

        return Image.alpha_composite(img, text_layer)


def draw_active_fixtures(font_path, today_only=True):
    seen_teams = []

    for team in Fixture.BADGE_LOOKUPS.keys():
        next_fix_url = f'https://api-football-v1.p.rapidapi.com/v2/fixtures/team/{team}/next/1'

        fix_req = Request(next_fix_url, headers=HEADERS)
        
        fix_content = urlopen(fix_req).read()
        
        data = json.loads(fix_content)
        
        fixtures = data['api']['fixtures']
        
        if not fixtures:
            continue
        
        fix = Fixture(fixtures[0])

        home = fix.home_team.id
        away = fix.away_team.id

        if (home, away) in seen_teams:
            continue

        if fix.is_today or not today_only:
            yield fix.draw_card(font_path=font_path)

        seen_teams.append((home, away))

def draw_competition_fixtures(font_path, league_id, form_count=0):

    date = datetime.now().strftime('%Y-%m-%d')

    next_fix_url = f'https://api-football-v1.p.rapidapi.com/v2/fixtures/league/{league_id}/{date}'
                     
    fix_req = Request(next_fix_url, headers=HEADERS)
    
    fix_content = urlopen(fix_req).read()
    
    data = json.loads(fix_content)

    for f in data['api']['fixtures']:
        fix = Fixture(f)

        yield fix.draw_card(font_path=font_path, form_count=form_count)
