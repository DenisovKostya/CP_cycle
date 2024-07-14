import sys
import argparse
from Information import Information
from CodeforcesResults import CodeforcesResults
from AtcoderResults import AtcoderResults
from CodechefResults import CodechefResults


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # updates ratings automatically
    parser.add_argument(
        '--add_contest',
        type=str,
        help='add contest (key words: codeforces, atcoder, tlx, codechef, dmoj)'
    )
    parser.add_argument(
        '--update_table',
        type=str,
        help='updates viewers table'
    )
    parser.add_argument(
        '--update_tlx',
        type=str,
        help='update tlx'
    )

    args = parser.parse_args()
    while input("have you download your google sheet (Y/N)? Please do it in case of any error to recreate a table: ") != 'Y':
        continue

    update_tlx = True
    if args.update_tlx is not None:
        update_tlx = False
        print("not updating tlx")

    with Information(update_tlx=update_tlx) as info:
        if args.add_contest is not None:
            if args.add_contest == "codeforces":
                contestId = input("Input codeforces contest id: ")
                type_of_competition = input("type of competition(see Competition.get_coeff): ")
                info.add_competition(
                    CodeforcesResults.get_results(
                        contestId,
                        info.format_for_platform("codeforces"),
                        info.get_free_column(),
                        type_of_competition
                    )
                )
            if args.add_contest == "atcoder":
                contestId = input("Input atcoder contest id: ")
                type_of_competition = input("type of competition(see Competition.get_coeff): ")
                info.add_competition(
                    AtcoderResults.get_results(
                        contestId,
                        info.format_for_platform("atcoder"),
                        info.get_free_column(),
                        type_of_competition
                    )
                )
            if args.add_contest == "tlx":
                pass
            if args.add_contest == "codechef":
                contestId = input("Input codechef contest id: ")
                type_of_competition = input("type of competition(see Competition.get_coeff): ")
                add = [0, 0, 0, 0]
                add[1] = int(input("Bonus for div. 3: "))
                add[2] = int(input("Bonus for div. 2: "))
                add[3] = int(input("Bonus for div. 1: "))
                info.add_competition(
                    CodechefResults.get_results(
                        contestId,
                        info.format_for_platform("codechef"),
                        info.get_free_column(),
                        type_of_competition,
                        add
                    )
                )
            if args.add_contest == "dmoj":
                pass
        if args.update_table is not None:
            info.update_view_table = True
        if args.add_contest == "rating":
            have = []
            for user in info.users:
                have.append([user.get_summary_delta(), user.nicks['codeforces'], user.get_delta('codeforces'),
                             user.get_delta('atcoder'),
                             user.get_delta('tlx'),
                             user.get_delta('codechef'),
                             user.get_delta('dmoj')])


            def compare(item1):
                return item1[0]
            have.sort(key=compare)
            for user in have:
                print(user[1], user[0], user[2], user[3], user[4], user[5], user[6])
