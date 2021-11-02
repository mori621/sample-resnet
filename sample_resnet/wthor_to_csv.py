import argparse
import struct
import pandas as pd


def parse_arg():
    parser = argparse.ArgumentParser(description="WTHOR reader.")
    parser.add_argument("FILES", type=str, nargs="+", help="WTHOR files.")
    return parser.parse_args()


def unpack_common_header(bytes):
    v = struct.unpack("<4bihh4b", bytes)
    common_header = {
        "file_year_upper": v[0],
        "file_year_lower": v[1],
        "file_month": v[2],
        "file_date": v[3],
        "num_games": v[4],
        "num_record": v[5],
        "game_year": v[6],
        "board_size": v[7],
        "game_type": v[8],
        "depth": v[9],
        "reserve": v[10],
    }
    return common_header


def unpack_game_header(bytes):
    v = struct.unpack("<hhhbb", bytes)
    game_header = {
        "game_id": v[0],
        "black_player_id": v[1],
        "white_player_id": v[2],
        "black_stones": v[3],
        "black_stones_theoretical": v[4],
    }
    return game_header


def unpack_play_record(bytes):
    return struct.unpack("<60b", bytes)


def read_wthor_file(file):
    with open(file, "rb") as f:
        common_header = unpack_common_header(f.read(16))
        games = []
        for i in range(common_header["num_games"]):
            game = {}
            game["header"] = unpack_game_header(f.read(8))
            game["play"] = unpack_play_record(f.read(60))
            games.append(game)
    return (common_header, games)


def show_play_record(record):
    num_alpha = ["a", "b", "c", "d", "e", "f", "g", "h"]
    record_str = []
    for move in record:
        upper = move // 10
        lower = move % 10
        record_str.append('{}{}'.format(num_alpha[upper - 1], lower))
    return record_str

def read_wthor_files(files):
    return_list = []
    for file in files:
        (header, games) = read_wthor_file(file)
        #print("year:{}, num_of_games:{}".format(header["game_year"], header["num_games"]))
        for idx, game in enumerate(games):
            #print("game :{}".format(idx))
            return_list.append(show_play_record(game["play"]))

    df = pd.DataFrame(return_list)
    #csv形式を保存
    df.to_csv('dataset.csv')


if __name__ == "__main__":
    args = parse_arg()
    read_wthor_files(args.FILES)