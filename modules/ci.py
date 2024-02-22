from concurrent.futures.thread import ThreadPoolExecutor
from urllib.request import urlopen
from bs4 import BeautifulSoup
from .project import Project
from . import utils


class CI:
    name = ''
    description = ''
    url = ''
    projects = list()
    current_run = ''
    last_abw_build = ''
    last_db_update = ''
    last_db_refresh = ''
    last_abw_build_fmtd = ''
    last_db_update_fmtd = ''
    last_db_refresh_fmtd = ''

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.url = f'http://{name}/ccnet/server/{name}/ViewServerReport.aspx'

    def get_current_run(self) -> str:
        running = None
        for project in self.projects:
            if project.is_running_row:
                return running.name
            running = project
        return ''

    def get_last_abw_build(self) -> str:
        return next(
            (project.last_build_time 
                for project in self.projects
                if 'Build' in project.name and 'ABW' in project.name), 
            None
        )

    def get_last_db_update(self) -> str:
        return next(
            (project.last_build_time 
                for project in self.projects
                if 'Update' in project.name and ('agr' in project.name or '700' in project.name)), 
            None
        )

    def get_last_db_refresh(self) -> str:
        return next(
            (project.last_build_time 
                for project in self.projects
                if 'Refresh' in project.name and ('agr' in project.name or '700' in project.name)), 
            None
        )

    @property
    def failing_projects(self) -> list[Project]:
        return [project for project in self.projects if project.is_failing]
    
    @property
    def failing_projects_no(self) -> int:
        return len(self.failing_projects)

    def fetch(self) -> None:
        self.projects = list()
        page = urlopen(self.url)
        soup = BeautifulSoup(page.read().decode("utf-8"), "html.parser")
        status_grid = soup.find('table', id='StatusGrid')
        project_tags = status_grid.find_all('tr', class_='wholeRow')
        for project_tag in project_tags:
            project = Project(self)
            self.projects.append(project)
            with ThreadPoolExecutor(max_workers=8) as executor:
                executor.submit(project.fetch, project_tag)

        self.current_run = self.get_current_run()
        self.last_abw_build = self.get_last_abw_build()
        self.last_db_update = self.get_last_db_update()
        self.last_db_refresh = self.get_last_db_refresh()

        self.last_abw_build_fmtd = utils.dt_to_string(self.last_abw_build)
        self.last_db_update_fmtd = utils.dt_to_string(self.last_db_update)
        self.last_db_refresh_fmtd = utils.dt_to_string(self.last_db_refresh)
