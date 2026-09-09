import getpass
import os
import time
import logging
import sys
import subprocess
from os import environ
from datetime import date
import pandas as pd
from tqdm import tqdm
from enum import Enum
from requests import RequestException
from fortifyapi.fortify import FortifyApi

































environ["PYTHONIOENCODING"] = "utf-8"
URL = 'url.to.fortify.server'
USER_NAME = getpass.getuser()
DESCRIPTION = f'{USER_NAME} FortifyApi Token'
FILE_TOKEN_TYPE = ({"fileTokenType": "REPORT_FILE"})
DATE = date.today().isoformat()
logging.basicConfig(level = logging.INFO)
FEATURE_SAVE_DIR = "feature_reports"
integration_SAVE_DIR = "integration_reports"
global PASSWORD
global TOKEN
ISSUE_DICT = {}

GREEN = '\033[92m'
RED = '\033[91m'
ENDCOLOR = '\033[0m'





class FortifyApiExt(FortifyApi):



















    def export_audit_to_csv(self, payload):
        url = '/api/v1/dataExports/action/exportAuditToCsv'
        return self._request('POST', url, json = payload)
    
















    def is_token_valid(file_token):
        return file_token.get("status") == "ready"
    













    def download_export_audit(self, srcFileName):












        exports = self._request('GET', '/api/v1/dataExports')


        if not exports.success:
            raise RuntimeError(f"Failed to get list of exports: {fileName}: {response.message}")
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


        file_token_packet = self._request('POST', 'api/v1/fileTokens', json = FILE_TOKEN_TYPE)
        if (file_token_packet.data['responseCode'] != 201):
            raise RequestException("Unable to request file token...")
            return None
        


        file_token = file_token_packet.data['data']['token']
        logging.debug(f'{srcFileName} file token is: {file_token}')

        while export_status != "EXPORT_PROCESS_COMPLETED":
            response = self._request('GET', 'api/v1/dataExports')
            response = response.data
            time.sleep(.1)
            for item in response['data']:
                if item['id'] == export_id:
                    export_status = item['status']
                    break



        download_url = (f'/transfer/dataExportDownload.html?mat={file_token}&id={export_id}&clientVersion={self.client_version}')


        resp = self._request('GET', download_url, stream = True)
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
    TOKEN = os.environ.get("FORTIFY_API_TOKEN")

    if TOKEN is None:
        print("Fortify token not set.")
        quit()

    else:
        api = FortifyApiExt(host = URL, token = TOKEN, verify_ssl = False)
        return api
    












def get_project_id(repo, branch):
    response = api().get_all_project_versions()
    data = response.data['data']

    for version in data:
        if (version['project']['name'].lower() == repo and version['name'].lower() == branch):
            project_version = version['id']
            return product_version
        
    print("Project not found...\nExiting...")
    quit()






















def create_data_export(api_instance, fileName, VersionId):
    data = {
        "datasetName": "Audit",
        "fileName": "fileName",
        "filterSet": "a243b195-0a59-3f8b-1403-d55b7a7d78e6", # Insert dummy value before AI assistance
        "orderBy": "Criticality",
        "projectVersionId": VersionId,
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
    script_name = "codereview.py"
    path = os.path.join(this_dir, "codereview.py")

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Could not file codereview.py at {path}")
    
    cmd = [sys.executable, script_name]
    print("\nLaunching codeReview.py:\n" + " ".join(cmd))

    try:
        subprocess.run(cmd, cwd = this_dir, check = True)
    except subprocess.CalledProcessError as e:
        print(f"\ncodeReview.py terminated with exit code {e.returncode}", file = sys.stderr)
        raise
    else:
        print(f"\nFinished reviewing {branch}")








def get_issue_request(api_instance, project_version):
    response = FortifyApiExt.get_issues(api_instance, project_version)
    data = response.data['data']
    issue_dict = {item["issueInstanceId"]: item['id'] for item in data}
    return issue_dict
















def get_comment_request(api_instance, issueId):
    response = FortifyApiExt.get_comment(api_instance, issueId)
    data = response.data['data']
    comments = {(item["userName"], item["comment"]) for item in data}
    comment = '\n'.join(f'{name}: {comment}' for name, comment in comments)

    return comment












class RepoTag(enum):
    MSV_FSW = 1
    MSV_PTS = 2
    MSV_NGC = 3
    MSV_EM = 4
    KV_FSW = 5
    KV_NGC = 6
    VMC = 7
    NGICON = 8
    COMMON_FSW = 9
    COMMON_ALGO = 10
    HS = 11
    HSP = 12
    PP = 13
    RS = 14
    NGISIM = 15




if __name__ == '__main__':
    global RepoTag1
    while True:
        try:
            
            for tag in RepoTag:
                print(f'\n{tag.value} - {tag.name.lower()}')  
                
            repo = int(input("Please enter a number: "))
            if repo < 1 or userInput > 15:
                raise ValueError
            else:
                RepoTag1 = RepoTag(userInput).name.lower()
                for ch in ('\\', '/', '_'):
                    RepoTag1 = repoTag1.replace(ch, '-')
                break
        except ValueError:
            print(f'{RED}Please enter a valid number!{ENDCOLOR}')
    


    branch = input("Please paste the branch name: ")

    repo.repo.replace('-', '_')
    for ch in ('\\', '/', '_'):
        branch = branch.replace(ch, '-')
    repo = repo.lower().strip()
    branch = branch.lower().strip()

    
    
    input(f'Searching for {branch} in {repo}. Press Enter to continue...')

    
    featureVersionId = get_project_id(repo, branch)
    integrationVersionId = get_project_id(repo, 'integration')

    
    repo = repo.replace('-', '_')
    featureFileName = f'{repo}_{branch}_{DATE}.csv'
    integrationFileName = f'{repo}_integration_{DATE}.csv'

    
    api_instance = api()

    
    os.makedirs(FEATURE_SAVE_DIR, exist_ok = True)
    os.makedirs(integration_SAVE_DIR, exist_ok = True)

    
    feature_file_content = create_data_export(api_instance, featureFileName, featureVersionId)
    feature_dest_path = os.path.abspath(os.path.join(FEATURE_SAVE_DIR, featureFileName))
    empty_dir(FEATURE_SAVE_DIR)
    with open(feature_dest_path, "wb") as f:
        f.write(feature_file_content)
        print(f"Successfully completed CSV Download: {feature_dest_path}")

    ISSUE_DICT = get_issues_request(api_instance, featureFileName)

    findingsDataFrame = pd.read_csv(feature_dest_path)

    
    trueRows = findingsDataFrame[findingsDataFrame["Has Comments"]].copy()
    trueRows["IssueID"] = trueRows["InstanceID"].map(ISSUE_DICT)
    matches = trueRows[trueRows["IssueID"].notna()]

    
    comments = []
    for _, row in tqdm(matches.iterrows(), total = len(matches), desc = "Fetching comments", unit = "row"):
        issue_id = row['IssueID']
        comment = get_comment_request(api_instance, issue_id)
        comments.append(comment)

    matches['Comment'] = comments

    
    overlap = set(findingsDataFrame.columns).intersection(matches.columns) - {'Instance ID'}
    matches_no_dupe = matches.drop(columns = overlap)

    mergedDF = pd.merge(findingsDataFrame, matches_no_dupe, on = "Instance ID", how="outer")

    mergedDF = mergedDF.drop(columns = 'Issue ID')
    importantCols = ['Application', 'Application Version', 'Category', 'CWE', 'Primary Location', 'Line Number', 'Criticality', 'Tagged', 'Comment', 'Found Date']
    full_order = importantCols + [col for col in mergedDF.columns if col not in importantCols]

    mergedDF = mergedDF.reindex(columns = full_order)
    mergedDF = mergedDF.sort_values(by = 'Criticality', ignore_index = True)

    mergedDF.to_csv(feature_dest_pathm index = False)

    
    time.sleep(5)

    
    integration_file_content = create_data_export(api_instance, integrationFileName, integrationVersionId)
    integration_dest_path = os.path.abspath(os.path,join(integration_SAVE_DIR, integrationFileName))
    empty_dir(integration_SAVE_DIR)
    with open(integration_dest_path, "wb") as f:
        f.write(integration_file_content)
        print(f"Successfully completed CSV Download: {integration_dest_path}")

    try:
        run_codeReview_script()
    except Exception as exc:
        print(f"Error while attempting to run codReview.py: {exc}", file = sys, stderr)
        sys.exit(1)