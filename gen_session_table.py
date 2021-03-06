import re
from datetime import datetime, timedelta
import io
from collections import namedtuple

import pytz
import markdown

session_desc_text = """
Opening session [10 minutes]
Keynote Speech and question session [60 minutes]<br>Rainer Koschke, <i>Empirical Research in Software Clone Management</i>
break [10 minutes]
Speech from Sider Company [30 minutes]
break [10 minutes]
Paper presentation session: Analysis [60 minutes]<ol start="1"><li>Rainer Koschke and Marcel Steinbeck, <i>SEE Your Clones With Your Teammates</i></li><li>Yaroslav Golubev and Timofey Bryksin, <i>On the Nature of Code Cloning in Open-Source Java Projects</i></li><li>Daisuke Nishioka and Toshihiro Kamiya, <i>Towards Informative Tagging of Code Fragments to Support the Investigation of Code Clones</i></li></ol>
lunch break [20 minutes]
Paper presentation session: Code-clone detection [40 minutes]<ol start="4"><li>Andre Schafer, Wolfram Amme and Thomas Heinze, <i>STUBBER : Compiling Source Code into Bytecode Without Dependencies for Java Code Clone Detection</i></li><li>Tomoaki Tsuru, Tasuku Nakagawa, Shinsuke Matsumoto, Yoshiki Higo and Shinji Kusumoto, <i>Type-2 Code Clone Detection for Dockerfiles</i></li></ol>
break [10 minutes]
Poster session and discussion on the provocative statements [40 minutes]
break [10 minutes]
People choice award session for the technical papers and poster papers [10 minutes]
Open steering committee meeting [30 minutes]
Closing session [10 minutes]
"""[1:-1]

session_title_and_durations = []
for L in session_desc_text.split('\n'):
    m = re.match(r"(.*) \[(\d+) minutes\](.*)", L)
    assert m
    title = m.group(1)
    duration = int(m.group(2))
    paper_list = m.group(3)
    session_title_and_durations.append((title, duration, paper_list))

TimezoneInfo = namedtuple('TimezoneInfo', 'name tzobj')

timezones = [
    TimezoneInfo('UTC', pytz.utc),
    TimezoneInfo('Osaka', pytz.timezone('Asia/Tokyo')),
    TimezoneInfo('Dhaka', pytz.timezone('Asia/Dhaka')),
    TimezoneInfo('NY', pytz.timezone('America/New_York')),
    TimezoneInfo('SF', pytz.timezone('America/Los_Angeles')),
]

sio = io.StringIO()

FMT = "| " + "%-5s |" * len(timezones) + " %s | "
print(FMT % (tuple(tz.name for tz in timezones) + ('Activity',)), file=sio)
print(FMT % tuple(['-----']*6), file=sio)
t = datetime(2021, 10, 2, 12, 0, 0, tzinfo=pytz.utc)
days = [None] * len(timezones)
for title, duration, paper_list in session_title_and_durations:
    for i, (tzname, tzobj) in enumerate(timezones):
        if 'break' in title:
            print("| %5s " % '', end='', file=sio)
        else:
            u = t.astimezone(tzobj)
            day = u.day
            if day != days[i]:
                print("| Oct. %d<br> %02d:%02d " % (day, u.hour, u.minute), end='', file=sio)
            else:
                print("| %02d:%02d " % (u.hour, u.minute), end='', file=sio)
            days[i] = day
    print("| %s [%d minutes] %s|" % (title, duration, paper_list), file=sio)
    t += timedelta(minutes=duration)

md = markdown.Markdown(extensions=['tables'])
print(md.convert(sio.getvalue()))
