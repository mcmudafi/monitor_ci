import json
from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag
from .test import Test
from . import utils


class Project:
    ci = ''
    name = ''
    url = ''
    last_build_time = ''
    last_build_time_fmtd = ''
    broken_days = ''
    volunteer = ''
    failing_text = ''
    last_build_link = ''
    test_results = list()
    build_log = ''

    def __init__(self, ci):
        self.ci = ci.name

    @property
    def failing_tests_no(self) -> int:
        if self.test_results: return len(self.test_results)
        if self.build_log: return 1
        return 0

    @property
    def is_failing(self) -> bool:
        return self.failing_tests_no > 0

    @property
    def is_running_row(self) -> bool:
        return not self.name

    def fetch(self, project: Tag) -> None:
        self.fetch_project_info(project)
        self.fetch_fails_info(project)

        if self.broken_days:
            print(f'{self.ci}: {self.name} is failing')
            self.fetch_results()

    def fetch_project_info(self, project: Tag) -> None:
        project_name = project.find('td', class_='project--name')
        if not project_name: return

        project_name = project_name.find('a')
        self.name = project_name.text

        self.last_build_time = project.find('td', class_='lastBuildTime').text
        self.last_build_time_fmtd = utils.dt_to_string(self.last_build_time)

        project_link = project_name.get('href')
        self.url = f'http://{self.ci}{project_link}'

        report_link = project_name['href']
        report_link = report_link.replace('ViewProjectReport', 'ViewLatestBuildReport')
        self.last_build_link = f'http://{self.ci}{report_link}'

    def fetch_fails_info(self, project: Tag) -> None:
        broken_days = project.find('div', class_='brokenDays')
        if not broken_days: return

        self.broken_days = broken_days.text

        failing_text = next((tag for tag in project.find_all('a') if 'Fail' in tag.text), None)
        failing_text = failing_text.text if failing_text else ''
        self.failing_text = failing_text.replace('FailedCoverage', 'Failed. Coverage')

        fixer = project.find('script')
        if fixer:
            fixer = fixer.text
            fixer = fixer[fixer.find('showVolunteer'):]
            fixer = fixer[fixer.find('{'):fixer.find('}')+1]
            self.volunteer = json.loads(fixer)['volunteer']
        else:
            self.volunteer = ''

    def fetch_results(self) -> None:
        page = urlopen(self.last_build_link)
        soup = BeautifulSoup(page.read().decode("utf-8"), "html.parser")

        self.fetch_regular_test_runs(soup)
        self.fetch_cpp_test_runs(soup)

        if not self.test_results:
            self.fetch_log(page.url)

    def fetch_regular_test_runs(self, soup: BeautifulSoup) -> None:
        run_1 = next((tag for tag in soup.find_all('div') if 'Run #1:' in tag.text), None)
        if run_1:
            self.test_results = list()
            table = run_1.parent
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if cols:
                    self.test_results.append(Test(cols))

    def fetch_cpp_test_runs(self, soup: BeautifulSoup) -> None:
        cpp_assert = next((tag for tag in soup.find_all('td', class_='sectionheader') if 'CppUnit run:' in tag.text), None)
        if cpp_assert:
            self.test_results = list()
            table = cpp_assert.parent.parent
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if cols:
                    self.test_results.append(Test(cols))

    def fetch_log(self, url: str) -> None:
        if not url.endswith('ViewBuildLog.aspx'):
            url = url.replace('ViewBuildReport.aspx', 'ViewBuildLog.aspx')

        page = urlopen(url)
        soup = BeautifulSoup(page.read().decode("utf-8"), "html.parser")
        log = soup.find('pre', class_='log')
        if log:
            root = BeautifulSoup(log.text, "lxml")

            # Typical error for MSBuild executions
            buildresults = root.find_all('msbuild', success='false')
            if buildresults:
                buildresults = buildresults[-1]
                message_error = buildresults.find('error')
                if message_error:
                    return buildresults.text.strip()

            # Typical error for non MSBuild executions
            buildresults = root.find_all('buildresults')
            if buildresults:
                buildresults = buildresults[-1]
                message_error = buildresults.find('message', level='Error')
                if not message_error:
                    message_error = buildresults.find('message')
                return buildresults.text.strip()

            # Last resort to just fetch the log
            return root.text