import json
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime as dt

data_path = "pages/data/donations"
imgs_subdir = "pages/images"


def load_donos():
    with open(f"{data_path}.json") as fp:
        donos_dict = json.load(fp)
        print(f"loaded {len(donos_dict)} donations")
    return donos_dict


def get_donos_page(x):
    dono_url = (f"https://www.givesendgo.com/api/v1/campaigns"
                f"/legalfund-ceo-shooting-suspect/get-recent-donations?pageNo={x}")
    response = requests.get(dono_url)
    return response.json()["returnData"]["donations"]  # list


def update_donos():
    donos = load_donos()
    dono_keys = set(donos.keys())
    pg = 0
    while True:
        if pg > 0 and pg % 10 == 0:
            print(f"page {pg}")
        data = get_donos_page(pg)
        keyed_data = {f"{dono['donation_id']}": dono for dono in data}
        new_keys = set(keyed_data.keys())
        if (len(new_keys - dono_keys)) > 0:
            donos.update(keyed_data)
            pg += 1
        else:
            break
    with open(f"{data_path}.json", "w") as fp:
        json.dump(donos, fp, indent=4)
    print(f"added {len(donos)-len(dono_keys)} new donations ({len(donos)} total)")


def to_csv():
    donos_dict = load_donos()
    with open(f"{data_path}.csv", "w") as csv:
        csv.write(f"id, time, amount, name, anon, lovecount, comment\n")
        for dono in donos_dict.values():
            name = dono['donation_name'].strip("\n").replace("\n", "\\n")
            comment = dono["donation_comment"].strip("\n").replace("\n", "\\n")
            csv.write(f"{dono['donation_id']}, {dono['time']}, {dono['donation_amount']}, "
                      f"{name}, {dono['donation_anonymous']}, "
                      f"{dono['lovecount']}, {comment}\n")


def graph():
    donos_dict = load_donos()
    donos_list = [(v["time"], v["donation_amount"]) for v in donos_dict.values()]
    donos_list.sort()

    plt_x = []
    plt_y = []
    current_total = 0

    for time_str, amt_str in donos_list:
        amount = float(amt_str)
        current_total += amount
        plt_x.append(dt.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
        plt_y.append(current_total)

    figsize = (12, 6)

    # number of donations (all time):
    num_donos = plt.figure(1, figsize=figsize)
    plt.plot(plt_x, list(range(1, len(plt_x) + 1)), figure=num_donos)
    ax_1 = plt.gca()
    ax_1.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # interval
    ax_1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))  # format date
    plt.xlabel("day")
    plt.ylabel("total #")
    plt.title("number of donations over time")
    plt.grid(True)
    plt.tight_layout()
    num_donos.savefig(f"{imgs_subdir}/num_donos.png")

    # all time:
    all_time = plt.figure(2, figsize=figsize)
    plt.plot(plt_x, plt_y, figure=all_time)
    ax_2 = plt.gca()
    ax_2.xaxis.set_major_locator(mdates.DayLocator(interval=5))  # interval
    ax_2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))  # format date
    plt.xlabel("day")
    plt.ylabel("total ($)")
    plt.title("donations over time")
    plt.grid(True)
    plt.tight_layout()
    all_time.savefig(f"{imgs_subdir}/all_time.png")

    # since article:
    since_article = plt.figure(3, figsize=figsize)
    plt.plot(plt_x, plt_y, figure=since_article)
    ax_3 = plt.gca()
    ax_3.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    ax_3.xaxis.set_major_formatter(mdates.DateFormatter("%d+%H"))  # format date
    ax_3.set_xlim(left=dt(2025, 2, 4), right=dt.now())
    ax_3.set_ylim(bottom=220000)
    plt.xlabel("day+hour")
    plt.xticks(rotation=90)
    plt.ylabel("total ($)")
    plt.title("donations over time")
    plt.grid(True)
    plt.tight_layout()
    since_article.savefig(f"{imgs_subdir}/since_article.png")

    # plt.show()


update_donos()
to_csv()
graph()
