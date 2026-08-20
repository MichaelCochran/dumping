'''
----------------------------------------------------------------------------
Library   : velociraptor
Package   : None
Class     : None
Engineers : Steve Schifris
Abstract  : This main provides an entry to velociraptor for performing Jira analytics. The entry
            handles command line arguments before invoking the "main" routine in Velociraptor.
----------------------------------------------------------------------------
'''

from velociraptor.types.config_manager import ConfigManager
from velociraptor.interfaces.jira_interface import JiraInterface
from velociraptor.interfaces.jira_analytics import JiraAnalytics
import argparse

if __name__ == "__main__":
    description = "update_jira_fields is a Velociraptor utility that enables copying between Jira fields in the same \
        project and deleting Jira field data. Arguments specifiy whether to update all issues in the project or only \
            specified ones."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-u", "--update", action='store_true',
                        help="Update Jira; without this flag, the update is simulated and logged but not performed")
    parser.add_argument("-o", "--overwrite", action='store_true',
                        help="Overwrite existing values in Jira; without this flag, only empty fields are updated")
    parser.add_argument("--output_file", nargs="?", default="update_jira_fields",
                        help="base file name for the output (will get date/time prepended and file extension added)")

    parser.add_argument('--fields', nargs='+',
                        help='pairs of comma separated fields to copy between, with a space between each pair (e.g., f1,f2 f3,f4)')

    parser.add_argument('--issues', nargs='*',
                        help='list of issue keys to update; if omitted, will update all issues')


    args = parser.parse_args()

    config_mgr = ConfigManager(args)

    print("Analyze Jira processing...")
    jiraInterface = JiraInterface(config_mgr)
    jiraAnalytics = JiraAnalytics(config_mgr, jiraInterface)
    jiraAnalytics.getLatestSprints(13199)
    print("Completed Analyze Jira processing.")
