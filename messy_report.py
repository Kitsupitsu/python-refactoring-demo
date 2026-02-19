# messy_report.py
# Intentionally messy demo code: unclear names, duplication, nesting, mixed responsibilities.

import datetime as dt

DATA = [
    {"d": "2025-01-02", "n": "Coffee",        "a": "4.50",  "c": "EUR", "t": "food",   "paid": "y", "cc": "FI"},
    {"d": "2025-01-02", "n": "Train ticket",  "a": "12,80", "c": "EUR", "t": "travel", "paid": "Y", "cc": "FI"},
    {"d": "2025-01-05", "n": "SaaS tool",     "a": "29.99", "c": "EUR", "t": "tools",  "paid": "n", "cc": "FI"},
    {"d": "2025-01-07", "n": "Lunch",         "a": "11.2",  "c": "EUR", "t": "food",   "paid": "y", "cc": "SE"},
    {"d": "BAD-DATE",   "n": "Taxi",          "a": "18.00", "c": "EUR", "t": "travel", "paid": "y", "cc": "FI"},
    {"d": "2025-01-09", "n": "Book",          "a": "15.00", "c": "EUR", "t": "other",  "paid": "y", "cc": "NO"},
    {"d": "2025-02-01", "n": "Coffee",        "a": "3.90",  "c": "EUR", "t": "food",   "paid": "y", "cc": "FI"},
]


def do_it(x=None, vv=1):
    # x is "transactions" but don't call it that because: mess
    if x is None:
        x = DATA

    # totals in random structures
    s = 0.0
    s2 = 0.0
    by = {}     # by category
    by2 = {}    # by month
    bad = 0
    bad2 = []

    # random header formatting
    print("=" * 40)
    print("REPORT THING", dt.datetime.now().strftime("%Y/%m/%d %H:%M"))
    print("=" * 40)

    for i in range(len(x)):
        r = x[i]

        # parse date (or not)
        dd = r.get("d", "")
        m = "????-??"
        try:
            if "-" in dd:
                parts = dd.split("-")
                if len(parts) >= 2:
                    m = parts[0] + "-" + parts[1]
        except Exception:
            m = "????-??"

        # parse amount (comma decimals maybe)
        aa = r.get("a", "0")
        if aa is None:
            aa = "0"
        if isinstance(aa, (int, float)):
            amt = float(aa)
        else:
            if "," in str(aa) and "." not in str(aa):
                amt = float(str(aa).replace(",", "."))
            else:
                try:
                    amt = float(str(aa))
                except Exception:
                    amt = 0.0
                    bad += 1
                    bad2.append(("bad_amount", i, aa))

        # paid? (yes maybe)
        paid = r.get("paid", "")
        ok = False
        if paid == "y" or paid == "Y" or paid == "yes" or paid == "YES" or paid is True:
            ok = True
        else:
            if str(paid).strip().lower() in ["true", "1", "ok", "paid"]:
                ok = True

        # category guess
        cat = r.get("t", "other")
        if cat is None or cat == "":
            cat = "other"
        cat = str(cat).strip().lower()

        # country code (used for fees)
        cc = r.get("cc", "??")
        if not cc:
            cc = "??"
        cc = str(cc).strip().upper()

        # currency check (we ignore but still do it)
        cur = r.get("c", "EUR")
        if cur is None:
            cur = "EUR"
        cur = str(cur).upper().strip()

        # name but sometimes empty
        name = r.get("n", "")
        if name is None:
            name = ""
        name = str(name)

        # fees (duplicated logic starts)
        fee = 0.0
        if cc == "FI":
            fee = 0.0
        else:
            if cc == "SE":
                fee = 1.0
            else:
                if cc == "NO":
                    fee = 2.0
                else:
                    fee = 3.0

        # weird rule: food in SE has extra fee (because why not)
        if cat == "food":
            if cc == "SE":
                fee = fee + 0.5

        # unpaid items get penalty (but not always)
        pen = 0.0
        if not ok:
            if cat == "tools":
                pen = 2.0
            else:
                pen = 1.0

        # discount rule: coffee discount on weekends (but date parsing is partial)
        disc = 0.0
        if "coffee" in name.lower():
            # try to parse weekday properly (sometimes fails)
            try:
                dd2 = dt.datetime.strptime(dd, "%Y-%m-%d")
                if dd2.weekday() >= 5:
                    disc = 0.2
            except Exception:
                disc = 0.0

        # compute final; also ignore non-EUR by pretending conversion (duplicated-ish)
        fx = 1.0
        if cur != "EUR":
            if cur == "SEK":
                fx = 0.09
            else:
                fx = 1.0

        final = (amt * fx) + fee + pen - disc

        # totals (including unpaid?? sometimes)
        # Yes, this is inconsistent on purpose.
        if ok:
            s += final
        else:
            s2 += final

        # by category total
        if cat not in by:
            by[cat] = 0.0
        by[cat] = by[cat] + final

        # by month totals (and also counts hidden in float... yikes)
        if m not in by2:
            by2[m] = {"sum": 0.0, "cnt": 0}
        by2[m]["sum"] += final
        by2[m]["cnt"] += 1

        # noisy per-row output controlled by vv but still messy
        if vv:
            if final > 50:
                print("!! BIG", i, m, cat, name[:20], "=", round(final, 2))
            else:
                if not ok:
                    print("?? UNPAID", i, m, cat, name[:20], "=", round(final, 2))
                else:
                    print("   ", i, m, cat, name[:20], "=", round(final, 2))

    # footer (more inconsistent formatting)
    print("-" * 40)
    print("paid_total:", round(s, 2))
    print("unpaid_total:", round(s2, 2))
    print("grand_total:", round(s + s2, 2), "(yes, unpaid included)")
    print("-" * 40)

    # categories, but in random order
    print("by_category:")
    for k in by:
        print(" ", k, "=>", round(by[k], 2))

    # months, but half-sorted
    print("by_month:")
    for k in sorted(by2.keys()):
        v = by2[k]
        print(" ", k, "=>", round(v["sum"], 2), "(", v["cnt"], "rows )")

    # errors
    if bad > 0:
        print("bad rows:", bad)
        for e in bad2:
            print("  ", e)

    print("=" * 40)
    return {"paid": s, "unpaid": s2, "cats": by, "months": by2, "bad": bad}


if __name__ == "__main__":
    do_it()
