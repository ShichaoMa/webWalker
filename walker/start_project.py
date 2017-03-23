# -*- coding:utf-8 -*-
import string
from argparse import ArgumentParser
from shutil import move
from os.path import exists, join, abspath, dirname

from scrapy.commands import startproject
from scrapy.utils.template import render_templatefile, string_camelcase

TEMPLATES_TO_RENDER = (
        ('scrapy.cfg',),
        ('${project_name}', 'settings.py.tmpl'),
    )


class CustomStart(startproject.Command):

    def run(self, project, opt=None):

        project_name = project
        project_dir = project

        if exists(join(project_dir, 'scrapy.cfg')):
            self.exitcode = 1
            print('Error: scrapy.cfg already exists in %s' % abspath(project_dir))
            return

        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return

        self._copytree(self.templates_dir, abspath(project_dir))
        move(join(project_dir, 'module'), join(project_dir, project_name))
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            tplfile = join(project_dir,
                string.Template(path).substitute(project_name=project_name))
            render_templatefile(tplfile, project_name=project_name,
                ProjectName=string_camelcase(project_name))
        print("New web-walker project %r, using template directory %r, created in:" % \
              (project_name, self.templates_dir))
        print("    %s\n" % abspath(project_dir))
        print("You can start the demo spider with:")
        print("    custom-redis-server -h 127.0.0.1 -p 6379")
        print("    cd %s" % project_dir)
        print("    scrapy crawl bluefly")


def start():
    cmd = CustomStart()
    cmd.settings = {}
    cmd.settings["TEMPLATES_DIR"] = join(abspath(dirname(__file__)), "templates")
    parser = ArgumentParser()
    parser.add_argument("project", help="project or/and project dir")
    args = parser.parse_args()
    cmd.run(args.project)


if __name__ == "__main__":
    start()