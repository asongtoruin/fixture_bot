from fixtures import draw_active_fixtures
from params import FONT_PATH

for i, img in enumerate(draw_active_fixtures(FONT_PATH, today_only=False)):
    img.save(f'{i}.png')
