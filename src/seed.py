from .db import list_players, upsert

SEED = [
    {"player_id":"demo-001","name":"Alex Morgan","age":21,"position":"RW","nationality":"England","team":"Northbridge FC","league":"League One","foot":"Left","speed":88,"crossing":79,"dribbling":84,"passing":72,"finishing":67,"defending":35,"physicality":62,"appearances":31,"minutes":2110,"goals":9,"assists":11,"market_value":650000,"potential":86,"source":"demo-seed"},
    {"player_id":"demo-002","name":"Daniel Silva","age":22,"position":"RW","nationality":"Portugal","team":"Riverside Athletic","league":"Championship","foot":"Right","speed":82,"crossing":86,"dribbling":77,"passing":81,"finishing":70,"defending":40,"physicality":66,"appearances":36,"minutes":2450,"goals":8,"assists":13,"market_value":1800000,"potential":82,"source":"demo-seed"},
    {"player_id":"demo-003","name":"Sam Okoro","age":19,"position":"RW","nationality":"Nigeria","team":"Eastborough United","league":"League Two","foot":"Left","speed":94,"crossing":68,"dribbling":90,"passing":61,"finishing":74,"defending":29,"physicality":54,"appearances":28,"minutes":1740,"goals":12,"assists":7,"market_value":250000,"potential":92,"source":"demo-seed"},
    {"player_id":"demo-004","name":"Luca Bennett","age":23,"position":"LW","nationality":"Scotland","team":"Harbour City","league":"League One","foot":"Right","speed":86,"crossing":81,"dribbling":82,"passing":75,"finishing":71,"defending":38,"physicality":68,"appearances":33,"minutes":2300,"goals":10,"assists":10,"market_value":900000,"potential":78,"source":"demo-seed"},
    {"player_id":"demo-005","name":"Milan Petrovic","age":20,"position":"CM","nationality":"Serbia","team":"Central Rovers","league":"League Two","foot":"Right","speed":71,"crossing":73,"dribbling":75,"passing":88,"finishing":59,"defending":70,"physicality":73,"appearances":30,"minutes":2205,"goals":5,"assists":9,"market_value":350000,"potential":88,"source":"demo-seed"},
    {"player_id":"demo-006","name":"Ethan Clarke","age":24,"position":"ST","nationality":"Wales","team":"Valley Town","league":"Championship","foot":"Right","speed":78,"crossing":52,"dribbling":69,"passing":58,"finishing":91,"defending":25,"physicality":85,"appearances":38,"minutes":2675,"goals":19,"assists":5,"market_value":3200000,"potential":80,"source":"demo-seed"},
]


def seed_if_empty() -> None:
    if not list_players():
        upsert(SEED)
