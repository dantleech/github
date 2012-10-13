import cliapp
import logging
import requests
import json
import git
import base64

class GithubApp(cliapp.Application):

    def make_req(self, method, req, payload = {}):
        url = 'https://api.github.com/%s' % (req)
        if self.settings['verbose']:
            print 'Making [%s] request: %s' % (method, url)

        headers = {};
        payload = json.dumps(payload)

        if self.settings['token']:
            headers['Authorization'] = 'token %s' % (self.settings['token'])

        if method == 'get':
            r = requests.get(url, headers=headers)
        if method == 'post':
            r = requests.post(url, data=payload, headers=headers)
            
        j = json.loads(r.text or r.content)

        if self.settings['verbose']:
            print json.dumps(j, indent=2)

        if (r.ok):
            if (self.settings['verbose']):
                print 'Response: %s' % (json.dumps(j, indent=2))
            return j
        else:
            print "Error: %s" % j['message']
            if j['errors']:
                print "Errors:"
                for error in j['errors']:
                    print "-- %s" % error['message']

    def get_current_repo(self):
        path = self.settings['project_path']
        repo = git.Repo(path)
        return repo
        

    def add_settings(self):
        self.settings.string(['token', 't'], 'Github OAuth token', metavar='oauth tokenusername')
        self.settings.string(['username', 'u'], 'Github username', metavar='username')
        self.settings.string(['project_path', 'pp'], 'Project path', metavar='project-path')
        self.settings.string(['project_owner', 'po'], 'Project owner', metavar='project-owner')
        self.settings.string(['project_name', 'pn'], 'Project name', metavar='project-name')
        self.settings.boolean(['verbose', 'v'], 'Be verbose', metavar='verbose')

    def cmd_list(self, args):
        repos = self.make_req('get', 'users/' + self.settings['username'] + '/repos');
        for repo in repos:
            print repo['full_name']

    def cmd_create_pr(self, args):
        payload = {
                'title': 'Dans PR',
                'base': 'master',
                'head': 'dantleech:issue-2365',
                }

        req = self.make_req('post', 'repos/%s/%s/pulls' % (
            self.settings['project_owner'],
            self.settings['project_name']
        ), payload)
    
    def cmd_status(self, args):
        repo = self.get_current_repo()
        

app = GithubApp(version='0.0.1')
app.settings.config_files=['example.conf']
app.setup_logging()
app.run()
