import getpass
import json
import logging
import os
import subprocess
import sys
import time
from datetime import date
from enum import Enum
from os import environ

import pandas as pd
from fortifyapi.fortify import FortifyApi
from requests import RequestException
from tqdm import tqdm

environ['PYTHONIOENCODING'] = 'utf-8'
URL = 'url.to.fortify.server'
USER_NAME = getpass.getuser()
DESCRIPTION = f'{USER_NAME} FortifyApi Token'
FILE_TOKEN_TYPE = {'fileTokenType': 'REPORT_FILE'}
DATE = date.today().isoformat()
logging.basicConfig(level=logging.INFO)
FEATURE_SAVE_DIR = 'feature_reports'
INTEGRATION_SAVE_DIR = 'integration_reports'
global PASSWORD
global TOKEN
ISSUE_DICT = {}

GREEN = '\033[92m'
RED = '\033[91m'
ENDCOLOR = '\033[0m'


class FortifyApiExt(FortifyApi):

    def export_audit_to_csv(self, payload):
        url = '/api/v1/dataExports/action/exportAuditToCsv'
        return self._request('POST', url, json=payload)

    def is_token_valid(file_token):
        return file_token.get('status') == 'ready'

    def download_export_audit(self, srcFileName):
        exports = self._request('GET', '/api/v1/dataExports')

        if not exports.success:
            raise RuntimeError(f"Failed to get list of exports: {srcFileName}: {exports.message}")
            return None

        data = exports.data.get('data', [])
        if not data:
            raise ValueError("No data returned from data exports list...\nQuitting...")
            return None

        ids = [item['id'] for item in data if 'id' in item]
        fileNames = [item['fileName'] for item in data if 'fileName' in item]
        fileName_to_id = dict(zip(fileNames, ids))
        status = None
        export_status = None

        export_id = fileName_to_id.get(srcFileName)

        file_token_packet = self._request('POST', 'api/v1/fileTokens', json=FILE_TOKEN_TYPE)
        if (file_token_packet.data['responseCode'] != 201):
            raise RequestException("Unable to request file token...")
            return None

        file_token = file_token_packet.data['data']['token']
        logging.debug(f'{srcFileName} file token is: {file_token}')

        while export_status != 'EXPORT_PROCESS_COMPLETED':
            response = self._request('GET', 'api/v1/dataExports')
            response = response.data
            time.sleep(.1)
            for item in response['data']:
                if item['id'] == export_id:
                    export_status = item['status']
                    break

        download_url = (f'/transfer/dataExportDownload.html?mat={file_token}&id={export_id}&clientVersion={self.client_version}')

        resp = self._request('GET', download_url, stream=True)
        if not resp.success:
            raise RuntimeError(f"Failed to download export {export_id}: {resp.message}")
            return None
        else:
            file_content = resp.data

        file_token = None

        return file_content

    def get_issues(self, project_version):
        url = f'api/v1/projectVersions/{project_version}/issues?start=0&limit=-1&'
        return self._request('GET', url)

    def get_comment(self, issueId):
        url = f'/api/v1/issues/{issueId}/comments'
        return self._request('GET', url)


def api():
    TOKEN = os.environ.get('FORTIFY_API_TOKEN')

    if TOKEN is None:
        print("Fortify token not set.")
        quit()

    else:
        api = FortifyApiExt(host=URL, token=TOKEN, verify_ssl=False)
        return api


def get_project_id(repo, branch):
    response = api().get_all_project_versions()
    # TODO add error handling to all api calls
    data = response.data['data']

    for version in data:
        if (version['project']['name'].lower() == repo and version['name'].lower() == branch):
            project_version = version['id']
            return project_version

    print("Project not found...\nExiting...")
    quit()


def create_data_export(api_instance, fileName, VersionId):
    data = {
        'datasetName': 'Audit',
        'fileName': 'fileName',
        'filterSet': 'a243b195-0a59-3f8b-1403-d55b7a7d78e6',  # Insert dummy value before AI assistance
        'orderBy': 'Criticality',
        'projectVersionId': VersionId,
    }

    for i in range(3):
        response = api_instance.export_audit_to_csv(payload=data)
        if response.success:
            break
        if not response.success:
            raise RuntimeError(f"Export request failed for {fileName}: {response.message}")
            if i == 3:
                print("Quitting...")
                quit()


def empty_dir(dir_name):
    for entry in os.listdir(dir_name):
        full_path = os.path.join(dir_name, entry)
        os.remove(full_path)


def run_codeReview_script():
    this_dir = os.path.abspath(os.path.dirname(__file__))
    script_name = 'codereview.py'
    path = os.path.join(this_dir, 'codereview.py')

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Could not file codereview.py at {path}")

    cmd = [sys.executable, script_name]
    print("\nLaunching codeReview.py:\n" + ' '.join(cmd))

    try:
        subprocess.run(cmd, cwd=this_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\ncodeReview.py terminated with exit code {e.returncode}", file=sys.stderr)
        raise
    else:
        print(f"\nFinished reviewing {branch}")


def get_issue_request(api_instance, project_version):
    response = FortifyApiExt.get_issues(api_instance, project_version)
    data = response.data['data']
    issue_dict = {item['issueInstanceId']: item['id'] for item in data}
    return issue_dict


def get_comment_request(api_instance, issueId):
    response = FortifyApiExt.get_comment(api_instance, issueId)
    data = response.data['data']
    comments = {(item['userName'], item['comment']) for item in data}
    comment = '\n'.join(f'{name}: {comment}' for name, comment in comments)

    return comment


def download_report(fileName, save_dir, api_instance, versionId, branch_type):
    os.makedirs(save_dir, exist_ok=True)

    create_data_export(api_instance, fileName, versionId)
    file_content = api_instance.download_export_audit(fileName)
    dest_path = os.path.abspath(os.path.join(save_dir, fileName))
    empty_dir(save_dir)
    with open(dest_path, 'wb') as f:
        f.write(file_content)
        print(f"Successfully completed CSV download: {dest_path}")

    ISSUE_DICT = get_issue_request(api_instance, versionId)

    findingsDataFrame = pd.read_csv(dest_path)

    trueRows = findingsDataFrame[findingsDataFrame['Has Comment']].copy()
    trueRows['IssueID'] = trueRows['Instance ID'].map(ISSUE_DICT)
    matches = trueRows[trueRows['IssueID'].notna()]

    comments = []
    for _, row in tqdm(matches.iterrows(), total=len(matches), desc=f"Fetching comments for {branch_type}", unit='row'):
        issue_id = row['IssueID']
        comment = get_comment_request(api_instance, issue_id)
        comments.append(comment)

    matches['Comment'] = comments

    overlap = set(findingsDataFrame.columns).intersection(matches.columns) - {'Instance ID'}
    matches_no_dupe = matches.drop(columns=overlap)

    mergedDF = pd.merge(findingsDataFrame, matches_no_dupe, on='Instance ID', how='outer')

    mergedDF = mergedDF.drop(columns='IssueID')
    importantCols = ['Application', 'Application Version', 'Category', 'CWE', 'Primary Location', 'Line Number', 'Criticality', 'Tagged', 'Comment', 'Found Date']
    full_order = importantCols + [col for col in mergedDF.columns if col not in importantCols]

    mergedDF = mergedDF.reindex(columns=full_order)
    mergedDF = mergedDF.sort_values(by='Criticality', ignore_index=True)

    mergedDF.to_csv(dest_path, index=False)


def configureEnum():
    with open('repoConfig.json', 'r') as f:
        config = json.load(f)

    enumRepo = Enum('enumRepo', config)

    return enumRepo


if __name__ == '__main__':
    enumRepo = configureEnum()
    global repoTag1
    while True:
        try:
            print('')
            for tag in enumRepo:
                print(f"\n{tag.value} - {tag.name.lower()}")

            repo = int(input("Please enter a number: "))
            if int(repo) < 1 or int(repo) > len(enumRepo):
                raise ValueError
            else:
                repoTag1 = enumRepo(repo).name.lower()
                for ch in ('\\', '/', '_'):
                    repoTag1 = repoTag1.replace(ch, '-')
                break
        except ValueError:
            print(f"{RED}Please enter a valid number!{ENDCOLOR}")

    branch = input("Please paste the branch name: ")

    repo = repoTag1.replace('-', '_')
    for ch in ('\\', '/', '_'):
        branch = branch.replace(ch, '-')
    repo = repo.lower().strip()
    branch = branch.lower().strip()

    print(f"Searching for {branch} in {repo}.")

    featureVersionId = get_project_id(repo, branch)
    integrationVersionId = get_project_id(repo, 'integration')

    repo = repo.replace('-', '_')
    featureFileName = f'{repo}_{branch}_{DATE}.csv'
    integrationFileName = f'{repo}_integration_{DATE}.csv'

    api_instance = api()

    download_report(featureFileName, FEATURE_SAVE_DIR, api_instance, featureVersionId, 'feature')
    time.sleep(5)
    download_report(integrationFileName, INTEGRATION_SAVE_DIR, api_instance, integrationVersionId, 'integration')

    try:
        run_codeReview_script()
    except Exception as exc:
        print(f"Error while attempting to run codReview.py: {exc}", file=sys.stderr)
        sys.exit(1)
