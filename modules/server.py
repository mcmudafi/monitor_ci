import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta
from urllib.request import urlopen
from .ci import CI
from . import utils


UPDATE_DELAY = 5 * 60  # 5 minutes
DATA_FILE = 'server.dat'
CONN_CHECK_URL = 'http://contprocei/ccnet/server/contprocei/ViewServerReport.aspx'
CIs = [
    ('contabwmssql', 'All ABW components test running on SQL Server database'),
    ('contabwora', 'All ABW components test running on Oracle database'),
    ('contservora', 'All ABW Server Process tests running on oracle database'),
    ('contproccomp', 'Procurement components tests only'),
    ('contprocei', 'Electronic Invoicing server process tests only'),
    ('contprocserv', 'Procurement Server Process tests only'),
    ('autprocurement', 'Procurement auto tests using SpecFlow'),
    ('autprocurementlegacy', 'Procurement auto tests using legacy framework'),
    ('autprocurementxp', 'Procurement eXperience Packs auto tests'),
    ('contcompmssqlm7su', 'All ABW components from previous version running on SQL Server database')
]


class Server:
    cis = list()
    last_update = 0.0
    last_update_fmtd = ''
    is_fetching = False
    _is_connected = False

    def __init__(self):
        self.fetch()

    @property
    def is_connected(self) -> bool:
        try:
            page = urlopen(CONN_CHECK_URL)
            return page.status == 200
        except:
            return False

    @is_connected.setter
    def is_connected(self, val) -> None:
        self._is_connected = val

    @property
    def is_update_needed(self) -> bool:
        return (time.time() - self.last_update) > UPDATE_DELAY

    def fetch(self):
        if not self.is_update_needed: return

        start = time.time()
        self.is_fetching = True
        is_connected = self.is_connected

        if is_connected:
            self.cis = [CI(*ci) for ci in CIs]
            with ThreadPoolExecutor(max_workers=8) as executor:
                for ci in self.cis:
                    executor.submit(ci.fetch)

        self.is_connected = is_connected
        self.last_update = time.time()
        self.last_update_fmtd = utils.dt_format(self.last_update + timedelta(hours=7).seconds)
        self.is_fetching = False
        print(f'Fetched in {self.last_update - start:.3}s')