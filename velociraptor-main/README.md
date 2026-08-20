# Velociraptor

<!-- markdownlint-disable MD033 -->

## About this Tool

Velociraptor is an extensible data analysis framework that enables programs to generate work performance reports *configurably* based on program-unique rules and preferences. It currently bundles a single application:

### Velociraptor Copy and Compare

Velociraptor Copy and Compare identifies and reconciles differences between a program's IMS and Jira project(s), based on a configurable linking between IMS tasks and Jira work items. Copy and Compare can be configured to display, compare, and even automatically update any data field (such as start dates, end dates and percent complete) based on the program's source of truth. Currently the automatic update only works for Jira fields. This tool enables engineering teams to focus on work planned and prioritized in Jira while Planners and Program Managers can manage more effectively at the IMS task level, knowing the QBD traces to the work product backlog.

#### Inputs

1. An Excel-compatible export of an IMS (see [Sheet Interface Configuration](#sheet-interface-configuration))
1. A Jira project or set of projects (see [Jira Interface Configuration](#jira-interface-configuration))
1. A configuration file (see [Configuration Description](#configuration-description))

#### Outputs

An Excel-compatible report of the comparison between the IMS and Jira projects will be produced. Highlighted cells quickly identify differences between data fields of interest.

## Quickstart

Velociraptor Copy and Compare can be run via a GitLab project pipeline or downloaded, deployed, and run locally.

Setting up a GitLab project provides an on-demand automated deploy and run that can be configured to run on at scheduled times (e.g., every Monday morning at 6am) and that any authorized user can run at will. The output Excel file is emailed to a configurable list of recipients. Setup for this approach is described in [Velociraptor Pipeline README](https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor-pipeline/-/blob/main/README.md).

Local deployment is typically best for air-gapped deployments and for individual users who want to locally manage their installation. The output Excel file is saved locally after each run. Instructions follow in the sections below.

### Generate a Jira Token

1. In a browser, Go to your [Jira instance](https://ebstools-jira.us.lmco.com/)
1. Click on your avatar in the upper-right
1. Click "Profile" in the dropdown

    !["Profile"](docs/img/profile.png?raw=True)

1. On the left navigation, click "Personal Access Tokens"

    !["Personal Access Tokens"](docs/img/access_tokens.png?raw=True)

1. Click the "Create Token" button

    !["Create Token Button"](docs/img/create_token.png?raw=True)

1. Give the token a name (ex. evm)
1. Set the Days until expiry to 180 (this is the max value)
1. Click Create

    !["Create Token Form"](docs/img/token_form.png?raw=True)

1. Copy and save the token in a safe spot for future use

### Running on Windows

1. Go to Releases page <https://gitlab.us.lmco.com/lockheed-martin-space/agile-evm/velociraptor/-/releases>
1. Under 'Other' click "Windows Velociraptor (Airgapped)" to download (towards the top of the screen)
1. Extract the zip file to a known location
1. Inside the extracted folder within the `config` directory, modify the file called `config.json`
1. Open the file in Notepad and modify the contents according the configuration description

## Configuration Description

The configuration is written using standard [JavaScript Object Notation (JSON)](https://www.json.org/) format.
String values must be encapulated in double quotes (`""`) and `boolean` values are `true` or `false` (case-sensitive).

Environment variables can be referenced in place of any attribute value using the format `"{$MY_ENV_VAR}"`.

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="schema_version">schema_version</a> | float | Required | Indicates the schema version of this configuration file. Must be set to `5` for compatibility with this version of software. |
| <a name="data_directory_path">data_directory_path</a> | string | `<project dir>/data/` | Absolute or relative (from the project root) directory path from which to read data inputs. |
| <a name="output_directory_path">output_directory_path</a> | string | `<project dir>/output/` | Absolute or relative (from the project root) directory path to which to write data outputs. |
| <a name="output_file_name">output_file_name</a> | string | Required | Suffix applied to output report file name after timestamp information. |
| <a name="field_update_default">field_update_default</a> | boolean | `false` | Specifies the default [updatable](#field-updatable) value to apply to each [Field](#field) in the [fields list](#fields). |
| <a name="field_overwrite_default">field_overwrite_default</a> | boolean | `false` | Specifies the default [overwritable](#field-overwritable) value to apply to each [Field](#field) in the [fields list](#fields). |
| <a name="field_insert_default">field_insert_default</a> | boolean | `false` | Specifies the default [insertable](#field-insertable) value to apply to each [Field](#field) in the [fields](#fields) list. |
| <a name="display_format_defaults">display_format_defaults</a> | dictionary\[[DataTypeEnum](#datatypeenum), string\] | Optional | Set of key-value pairs that specify the default [display_format](#field-metadata-display_format) to apply when rendering fields of a particular [DataTypeEnum](#datatypeenum). See [Display Format](#display-format). |
| <a name="excel_display_format_defaults">excel_display_format_defaults</a> | dictionary\[[DataTypeEnum](#datatypeenum), string\] | Optional | Set of key-value pairs that specify the default [excel_display_format](#field-metadata-excel_display_format) to apply when rendering fields of a particular [DataTypeEnum](#datatypeenum). See [Excel Display Format](#excel-display-format). |
| <a name="list_display_format_default">list_display_format_default</a> | [ListDisplayFormat](#listdisplayformat) | Optional | Default [ListDisplayFormat](#listdisplayformat) to apply when rendering field values that are lists. See [List Display Format](#listdisplayformat). |
| <a name="data_interfaces">data_interfaces</a> | list\[[DataInterface](#datainterface)\] | Required | List of data interfaces and their attributes to be used in generating the output report. |
| <a name="left_source">left_source</a> | [Source](#source) | Required | Of the two sources to be compared, these attributes apply to the left source. See [Source](#source). |
| <a name="right_source">right_source</a> | [Source](#source) | Required | Of the two sources to be compared, these attributes apply to the right source. See [Source](#source). |
| <a name="fields">fields</a> | list\[[Field](#field)\] | Required | All fields used for comparison and display are defined in this list of multiple [Field](#field) elements. |
| <a name="field_pairs">field_pairs</a> | list\[[FieldPair](#fieldpair)\] | Required | All field comparisons are defined in this list of multiple [FieldPair](#fieldpair) elements. |
| <a name="comparison">comparison</a> | [ComparisonConfig](#comparisonconfig) | Required |  Configuration related to the comparison output report. |

### DataInterface

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="datainterface-id">id</a> | string | Required | Identifier for the data interface; must be unique among all [DataInterface](#datainterface) elements. |
| <a name="datainterface-type">type</a> | [DataInterfaceTypeEnum](#datainterfacetypeenum) | Required | Enumeratated type; see [DataInterfaceTypeEnum](#datainterfacetypeenum). |
| <a name="datainterface-config">config</a> | Any | Optional | Variable configuration attributes depending on the [type](#datainterface-type); see [Data Interface Configuration](#data-interface-configuration). |

#### DataInterfaceTypeEnum

| Enumeration | Description |
| ----------- | ----------- |
| <a name="datainterfaceenum-sheet">SHEET</a> | A Microsoft Excel Worksheet data interface. |
| <a name="datainterfaceenum-jira">JIRA</a> | A Jira data interface. |

#### Data Interface Configuration

The DataInterface [config](#datainterface-config) is variable depending on the type of data interface is represented, as described below.

##### Sheet Interface Configuration

Any worksheet to be used as a data interface must conform to a few rules:

- Any accessible data must be contained on the first worksheet tab
- Data is organized in rows where each column represents a field of that row
- The first row solely contains column headers which uniquely identify the field contained in that column

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="sheet-interface-configuration-input_file">input_file</a> | string | Required | The worksheet file name (relative to the [data_directory_path](#sheet-interface-configuration-data_directory_path)). |
| <a name="sheet-interface-configuration-data_directory_path">data_directory_path</a> | string | `<project dir>/data/` | Absolute or relative (from the project root) directory path from which to read data inputs. |
| <a name="sheet-interface-configuration-query_string">query_string</a> | string | Optional | Query string to apply to the worksheet to fetch all issues to be analyzed. See [pandas.DataFrame.query](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html) for more details. |
| <a name="sheet-interface-configuration-filter">filter</a> | string | Optional | [Expression](#expression) used to evaluate whether an issue fetched as a result of the [query_string](#sheet-interface-configuration-query_string) should be included in the output report. Expression must evaluate to `true` or `false`, and will be included in the output if the expression evaluates to `true`. |

###### Sheet Source Data

A [Field](#field) [data_id](#field-data_id) may reference data contained in a Sheet source record by the exact text contained in its Worksheet column header.

###### Sheet Source Special Data

A [Field](#field) [data_id](#field-data_id) additionally may reference special data in a Sheet:

- `__row_number`: The row number of the corresponding record within the spreadsheet.

##### Jira Interface Configuration

A Jira interface can be configured to fetch data from any connected Jira server

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="jira-interface-configuration-server">server</a> | string | Required | The Jira server URL. |
| <a name="jira-interface-configuration-jql_string">jql_string</a> | string | Required | The JQL query to apply in order to fetch all issues to be analyzed. See [Jira Query Language](https://www.atlassian.com/software/jira/guides/jql/) for more details. |
| <a name="jira-interface-configuration-filter">filter</a> | string | Optional | [Expression](#expression) used to evaluate whether an issue fetched as a result of the [jql_string](#jira-interface-configuration-jql_string) should be included in the output report. Expression must evaluate to `true` or `false`, and will be included in the output if the expression evaluates to `true`. |
| <a name="jira-interface-configuration-write_enabled">write_enabled</a> | boolean | `false` | Indicates whether to enable Jira write operations (e.g. update an issue). No changes will be reflected back to Jira with any configuration unless this flag is enabled explicitly. |
| <a name="jira-interface-configuration-ca_bundle">ca_bundle</a> | string | `"{$REQUESTS_CA_BUNDLE}"` | The file path to the LM CA certificate bundle. |
| <a name="jira-interface-configuration-token">token</a> | string | `"{$JIRA_TOKEN}"` | The Jira token. |
| <a name="jira-interface-configuration-max_issues">max_issues</a> | integer | `2000` | The maximum number of issues to fetch at a time from Jira. |
| <a name="jira-interface-configuration-issue_dump_json_file">issue_dump_json_file</a> | string | Optional | The file name to output the queried Jira issues in JSON format (relative to the [output_directory_path](#jira-interface-configuration-output_directory_path) directory). |
| <a name="jira-interface-configuration-output_directory_path">output_directory_path</a> | string | `<project dir>/output/` | Absolute or relative (from the project root) directory path to which to write data outputs. |
| <a name="jira-interface-configuration-graph_provider_plugin_descriptor">graph_provider_plugin_descriptor</a> | [PluginDescriptor](#plugindescriptor) | Optional | A [PluginDescriptor](#plugindescriptor) element that describes a plugin supporting the [JiraIssueGraphProvider](#jiraissuegraphprovider-plugins) interface to create a relationship graph of Jira issues. |
| <a name="jira-interface-configuration-value_provider_plugin_descriptors">value_provider_plugin_descriptors</a> | list\[[PluginDescriptor](#plugindescriptor)\] | Optional | A list of [PluginDescriptor](#plugindescriptor) elements that describe plugins supporting the [JiraValueProvider](#jiravalueprovider-plugins) interface to calculate values from Jira [DataInterface](#datainterface) fields. |

###### Jira Source Data

A [Field](#field) [data_id](#field-data_id) may reference data contained in a Jira source record by its Jira field identifier. Reference *\[server url\]/rest/api/2/field* (e.g. *[https://ebstools-jira.us.lmco.com/rest/api/2/field](https://ebstools-jira.us.lmco.com/rest/api/2/field)*) to find the Jira field id associated with a given human-readable Jira field name (must be logged into Jira). Some fields (particularly built-in Jira fields such as `issuetype`, and `status`) are of complex type and contain embedded sub-elements. Reference *\[server url\]/rest/api/2/[field name]* (e.g. *[https://ebstools-jira.us.lmco.com/rest/api/2/status](https://ebstools-jira.us.lmco.com/rest/api/2/status)*) to find available sub-field ids. It is acceptable to define a field name targetting a particular sub-element using dot notation (e.g. `issuetype.name`). If a field references multiple elements or sub-elements, it will return a list of those elements. Multi-element sub-fields are intended to be read-only and not updated. Updates should only be performed on top-level fields where the structure is defined in its entirety.
exact text contained in the Worksheet column header.

###### PluginDescriptor

Velociraptor functionality can be customized or extended by a plugin described by a PluginDescriptor.

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="plugindescriptor-module_name">module_name</a> | string | Required | The python module containing the plugin class. |
| <a name="plugindescriptor-class_name">class_name</a> | string | Required | The name of the plugin class. |
| <a name="plugindescriptor-config">config</a> | Any | Optional | The plugin-specific configuration. |

###### JiraIssueGraphProvider Plugins

JiraIssueGraphProvider Plugins provide a means to define relationships between Jira issues and form a relationship graph. This graph may be used by [JiraValueProvider Plugins](#jiravalueprovider-plugins) to produce new reportable values. See below for JiraIssueGraphProvider Plugins that are included with Velociraptor.

###### JiraIssueGraphProvider

Creates a directed Jira issue graph based on specified Jira issue links and/or Epic link.

- `module_name: "velociraptor.plugins.jira_issue_graph_provider"`
- `class_name: "JiraIssueGraphProvider"`
- `config:`

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="jiraissuegraphprovider-child_parent_issue_links">child_parent_issue_links</a> | list\[[IssueLink](#jiraissuegraphprovider-issuelink)\] | Optional* | A list of [IssueLink](#jiraissuegraphprovider-issuelink) elements to establish parent-child relationships of Jira issues. |
| <a name="jiraissuegraphprovider-parent_link_epic_data_id">parent_link_epic_data_id</a> | string | Optional* | [data_id](#field-data_id) of the Jira epic link field. Should only be configured if the epic link is used to described a parent-child relationship. |
| | | | * At least one must be configured |

###### JiraIssueGraphProvider IssueLink

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="jiraissuegraphprovider-issuelink-link_id">link_id</a> | string | Required | Unique identifier of the issue link type. |
| <a name="jiraissuegraphprovider-is_parent_inward">is_parent_inward</a> | boolean | Required | `true` if the parent issue is on the inward side of the issue link. `false` if the parent issue is on the outward side of the issue link. |

The [link_id](#jiraissuegraphprovider-issuelink-link_id) and [is_parent_inward](#jiraissuegraphprovider-is_parent_inward) may be specific to the Jira server hosting the target projects. Reference *\[server url\]/rest/api/2/issueLinkType* (e.g. *[https://ebstools-jira.us.lmco.com/rest/api/2/issueLinkType](https://ebstools-jira.us.lmco.com/rest/api/2/issueLinkType)*) to find the id of the issue link, as well as whether the parent is on the inward or outward end of the link (must be logged into Jira).

EBS Jira Server defintions for commonly used parent-child issue links:

| Link name | Link ID | Inward | Outward |
| --------- | ------- | ------ | ------- |
| Agile Hive Link | `"11000"` | Parent of | Child of |
| Feature Link | `"10400"` | Story to Feature | Feature to Story |
| Parent Child | `"10700"` | is parent to | is child of |
| Parent-Child | `"11200"` | is child of | is parent of |
| Parent / Child Issue Link | `"11400"` | is parent issue of | is child issue of |
| Parent to Child relations | `"10900"` | is child of | is parent of |

EBS Jira Server definition for parent link Epic field:

| Field name | Field ID |
| ---------- | -------- |
| Epic Link | `"customfield_10100"` |

###### JiraValueProvider Plugins

JiraValueProvider Plugins extend Jira's reporting capability by providing additional [Field](#field) [id](#field-id) values that can be included reports. See below for JiraValueProvider Plugins that are included with Velociraptor.

###### JiraIssueTreeDepthProvider

Creates special Jira source field values related to tree depth, based on parent-child relationships described by the [graph_provider_plugin_descriptor](#jira-interface-configuration-graph_provider_plugin_descriptor) (required when this plugin is configured). The resulting set of Jira issues is assumed to form multiple issue trees, each rooted at a single top-level issue, where each issue has only a single parent issue, and there are no link cycles. Each returned issue will contain a Jira source [data_id](#field-data_id) `__tree_depth` indicating how many ancestors the issue has (top-level is 0).

- `module_name: "velociraptor.plugins.jira_issue_tree_depth_provider"`
- `class_name: "JiraIssueTreeDepthProvider"`

###### JiraAggregationProvider

Creates custom Jira source field aggregated values, based on parent-child relationships described by the [issue_graph_provider_plugin_descriptor](#jira-interface-configuration-issue_graph_provider_plugin_descriptor) (required when this plugin is configured). The [jql_string](#jira-interface-configuration-jql_string) must query all issues to be included in the aggregation. The resulting set of Jira issues is assumed to form multiple issue trees, each rooted at a single top-level issue, where each issue has only a single parent issue, and there are no link cycles. Each returned issue will contain the configured Jira source fields and values inclusive of all of its children in the tree.

- `module_name: "velociraptor.plugins.jira_aggregation_provider"`
- `class_name: "JiraAggregationProvider"`
- `config:`

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="jiraaggregationprovider-field_id">field_id</a> | string | Required | [id](#field-id) of the Jira [Field](#field) value from each child issue to aggregate. |
| <a name="jirapercentcompleteprovider-produced_data_id">produced_data_id</a> | string | Required | [data_id](#field-data_id) of the Jira [Field](#field) to produce containing the aggregated value. Must start with `"__"`. |
| <a name="jiraaggregationprovider-aggregation_type">aggregation_type</a> | [AggregationTypeEnum](#aggregationtypeenum) | Required | Aggregation function to apply. Missing values from child issues are ignored. |

###### AggregationTypeEnum

| Enumeration | Description |
| ----------- | ----------- |
| <a name="aggregation_type-sum">SUM</a> | Returns the sum of the collected values. |
| <a name="aggregation_type-count">COUNT</a> | Returns the number of the collected values. |
| <a name="aggregation_type-min">MIN</a> | Returns the minimum of the collected values. |
| <a name="aggregation_type-max">MAX</a> | Returns the maximum of the collected values. |
| <a name="aggregation_type-avg">AVG</a> | Returns the average (arithmetic mean) of the collected values. |
| <a name="aggregation_type-list">LIST</a> | Returns a list of all collected values. |
| <a name="aggregation_type-dlist">DLIST</a> | Returns a list of all distinct collected values (no duplicates). |

###### JiraIssueSprintProvider

Creates special Jira source field values related to previous, current, and future sprints. Each returned issue will contain a Jira source [data_id](#field-data_id) `__sprints` containing a *list* of Sprints, each with the following sub-elements:

- `start_date`: The start date of the sprint.
- `end_date`: The end date of the sprint.
- `activated_date`: The date the sprint was activated.
- `complete_date`: The date of the sprint was completed.

Each of these fields should be configured with a [DATE](#datatypeenum-date) [Field](#field) [type](#field-type).

All of a particular date type (e.g. all start dates) may be grouped together as a field and returned as a list using a sub-field id (e.g. `__sprints.start_date`). This then can be configured as a [Field](#field) configured with a [transform](#field-transform) to process the list, for example to select the earliest (`min()`) among the start dates. Finally, a [JiraAggregationProvider](#jiraaggregationprovider) may be used to collect all "earliest start dates" of child issues, and select the earliest of those to find the start date of a top-level issue.

- `module_name: "velociraptor.plugins.jira_issue_sprint_provider"`
- `class_name: "JiraIssueSprintProvider"`
- `config:`

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="jiraissuesprintprovider-sprint_data_id">sprint_data_id</a> | string | Required | [data_id](#field-data_id) of the Jira [Field](#field) containing sprint information (EBS Jira Server: `customfield_10104`). |

###### JiraPercentCompleteProvider

Creates special Jira source field values related to percent completion calculations, based on parent-child relationships described by the [issue_graph_provider_plugin_descriptor](#jira-interface-configuration-issue_graph_provider_plugin_descriptor) (required when this plugin is configured). The [jql_string](#jira-interface-configuration-jql_string) must query all issues to be included in the calculation of percent complete. The resulting set of Jira issues is assumed to form multiple issue trees, each rooted at a single top-level issue, where each issue has only a single parent issue, and there are no link cycles. Each returned issue will contain the following Jira source fields and values inclusive of all of its children in the tree:

- `__story_count`: The count of all completed stories.
- `__completed_story_count`: The count of all stories.
- `__story_points_sum`: The sum of all story points.
- `__completed_story_points_sum`: The sum of all completed story points.
- `__percent_completed_story_points`: The percent complete (completed story points ÷ story points).

Each of these fields should be configured with a numeric (e.g. [NUMBER](#datatypeenum-number), [PERCENT](#datatypeenum-percent)) [Field](#field) [type](#field-type).

A Jira issue is considered to complete if it has a Status that is in the Jira "Done" Status Category. A completed Jira issue has all of its story points allocated to its completed points total.

- `module_name: "velociraptor.plugins.jira_percent_complete_provider"`
- `class_name: "JiraPercentCompleteProvider"`
- `config:`

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="jirapercentcompleteprovider-story_points_data_id">story_points_data_id</a> | string | Required | [data_id](#field-data_id) of the Jira [Field](#field) containing story points (EBS Jira Server: `customfield_10106`). |
| <a name="jirapercentcompleteprovider-include_parents_in_totals">include_parents_in_totals</a> | boolean | `false` | If `false`, only stories with no children will be counted in the totals. If `true`, all stories will be counted. |

### Source

A Source defines a collection of data from a single entity like a Microsoft Excel Worksheet or Jira, typically accessed through a [DataInterface](#datainterface).

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="source-id">id</a> | string | Required | Identifier for the source; must be unique among all [Source](#source) elements. |
| <a name="source-name">name</a> | string | *Value of [id](#source-id)* | Human-readable source identifier for outputs. |
| <a name="source-data_interface_id">data_interface_id</a> | string | Required | Interface identifier corresponding to the [id](#datainterface-id) of a configured [DataInterface](#datainterface). |
| <a name="source-pk_field_id">pk_field_id</a> | string | Optional | [Field](#field) [id](#field-id) of the source's primary key (attribute to uniquely identify a record). May be omitted or set to `None` if this source is not linked back to the other source, or there is no primary key. |
| <a name="source-fk_field_id">fk_field_id</a> | string | Optional | [Field](#field) [id](#field-id) of the source's foreign key (attribute to match with the [pk_field_id](#source-pk_field_id) value of the other [Source](#source)). May be omitted or set to `None` if the other source does not link to this source. |

#### Special Sources

All configurations have access to these sources for specialized use:

- <a name="special-sources-calculated">Calculated</a>:** Provides access to special [DataTypeEnum](#datatypeenum) options that do not come directly from a [DataInterface](#datainterface) but instead are calculated. A [Field](#field) element's [source_id](#field-source_id) should reference it by the `"__calculated"` [id](#source-id). Since this source does not provide any data, a referencing [Field](#field) element's [data_id](#field-data_id) may be named arbitrarily, as long as it adheres to any other constraints.

### Field

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="field-id">id</a> | string | *Concatenation of values of [source_id](#field-source_id) and [data_id](#field-data_id)* | Identifier for the field; must be unique among all [Field](#field) elements. |
| <a name="field-name">name</a> | string |  *Value of [id](#field-id)* | Human-readable field identifier for outputs. |
| <a name="field-source_id">source_id</a> | string | Required | Identifier referencing the [id](#source-id) of an underlying configured [Source](#source). |
| <a name="field-data_id">data_id</a> | string | Required | Identifier referencing underlying [data](#data-id) within the [source_id](#field-source_id); rules are dependent on the configured source type. See [Data ID](#data-id). |
| <a name="field-type">type</a> | [DataTypeEnum](#datatypeenum) | Required | Data type of the Field; see [DataTypeEnum](#datatypeenum). |
| <a name="field-output_type">output_type</a> | DataTypeEnum | Optional | [DataTypeEnum](#datatypeenum) to assume for output purposes, if different than [type](#field-type); see [DataTypeEnum](#datatypeenum) |
| <a name="field-metadata">metadata</a> | [Metadata](#metadata) | Optional | Collection of configuration items for specific cases. See [Metadata](#metadata). |
| <a name="field-calculation">calculation</a> | string | Optional | Custom [Expression](#expression) used to calculate this field's value from other fields' values. If defined, [data_id](#field-data_id) must start with `"__"`, unless it has a [source_id](#field-source_id) referencing the [Calculated Source](#special-sources-calculated). See [Expression](#expression). |
| <a name="field-transform">transform</a> | string | Optional | Custom [Expression](#expression) used to transform this field's underlying value. See [Expression](#expression). |
| <a name="field-updatable">updatable</a> | boolean | *Value of [field_update_default](#field_update_default)* | Indicates whether this field can be updated (create a new value or modify an existing value) in the data source. |
| <a name="field-overwritable">overwritable</a> | boolean | *Value of [field_overwrite_default](#field_overwrite_default)* | Indicates whether this field can be overwritten (modify an existing value) in the data source; when false, higher precedence than [updatable](#field-updatable) when a value already exists. |
| <a name="field-insertable">insertable</a> | boolean | *Value of [field_insert_default](#field_insert_default)* | Indicates whether this field can be inserted (specified when creating a new record) in the data source. |
| <a name="field-display">display</a> | boolean | `false` | Indicates whether to display this field in the output report. |
| <a name="field-display_index">display_index</a> | integer | Optional | Positional index to display this field in the output report; must be unique among all [Field](#field) and [FieldPair](#fieldpair) elements. See [Display Index](#display-index). |

#### Data ID

Determinining the [data_id](#field-data_id) is dependent on the type of [Source](#source).

- [Sheet Source Data](#sheet-source-data)
- [Jira Source Data](#jira-source-data)
- [Special Sources](#special-sources)

#### DataTypeEnum

There are several supported ways to represent data for display and comparison purposes. When creating [FieldPair](#fieldpair) elements, only [Field](#field) elements of the same Native type should be paired together.

| Enumeration | Description | Native type |
| ----------- | ----------- | ----------- |
| <a name="datatypeenum-date">DATE</a> | A date type. | date |
| <a name="datatypeenum-string">STRING</a> | A string type. | string |
| <a name="datatypeenum-number">NUMBER</a> | A number type with floating-point precision. | float |
| <a name="datatypeenum-ims_hours">IMS_HOURS</a> | A special type for a Microsoft Project duration expressed in hours to enable comparison of only the numerical portion of the value. | float |
| <a name="datatypeenum-ims_charge_number">IMS_CHARGE_NUMBER</a> | A special type for full charge numbers that appear in the IMS to enable display and comparison of only the suffix (`"700LMBGNDC2L"` instead of `"LMB-1312-G1A+700LMBGNDC2L"`). | string |
| <a name="datatypeenum-jira_key">JIRA_KEY</a> | A special type for the Jira key format to favor logical ordering over lexicographical ordering (`"XYZ-2"` will precede `"XYZ-10"`). Should only be paired with other [Field] (#field) elements of [type](#field-type) JIRA_KEY. | string (display), custom (comparison) |
| <a name="datatypeenum-percent">PERCENT</a> | A percent type with floating-point precision and represented as a fraction of 1 (100% is equivalent to 1.0). | float |
| <a name="datatypeenum-formula">FORMULA</a> | Always comes from the [Calculated Source](#special-sources-calculated). Not suitable for pairing (display only). [Field](#field) elements of this [type](#field-type) must define a [metadata](#field-metadata) [value](#field-metadata-value) with the Microsoft Excel formula to apply. Recommended to specify [output_type](#field-output_type). Columns are substituted in the formula using the format `{{[id]}}` where \[id\] is the [id](#field-id) of [Field](#field) corresponding to that column (e.g. `"={{sheet:Baseline Start}}-{{jira_forecast_start}}"`). | n/a |
| <a name="datatypeenum-bolean">BOOLEAN</a> | A boolean type that is either True or False. | bool |
| <a name="datatypeenum-json">JSON</a> | A JSON-encoded structure. | string (display), Any (comparison) |
| <a name="datatypeenum-any">ANY</a> | A general pass-through type with no special rules. | Any |

#### Metadata

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="field-metadata-value">value</a> | string | Optional | Variable format depending on the type of the [source_id](#field-source_id). |
| <a name="field-metadata-display_format">display_format</a> | [Display Format](#display-format) | Optional | Specifies the [Display Format](#display-format) to apply when rendering this field in places other than Excel data cells. Its usage is currently limited to comment messages on Excel data cells (e.g. "Old value" on the "Merged" output report worksheet). See [Display Format](#display-format). |
| <a name="field-metadata-excel_display_format">excel_display_format</a> | string | Optional | Specifies the [Excel Display Format](#excel-display-format) to apply when rendering this field in an Excel data cell. See [Excel Display Format](#excel-display-format). |
| <a name="field-metadata-list_display_format">list_display_format</a> | [ListDisplayFormat](#listdisplayformat) | Optional | Specifies the default [ListDisplayFormat](#listdisplayformat) to apply when rendering field values that are lists. See [List Display Format](#listdisplayformat). |

#### Expression

An Expression is a `string` composed of literals, [functions](#expression-functions), [names](#expression-names), and [operators](#expression-operators) to express a value for a [Field](#field). Python's [Abstract Syntax Trees](https://docs.python.org/3/library/ast.html) are used to parse the expression, but symbols must be explicitly whitelisted to be supported. In most cases, this is a trivial software update. See below for currently-supported symbols:

##### Expression Functions

- `value(x)`: Returns the value of [Field](#field) with the [id](#field-id) of `'x'` (expressed as a string encapsulated in single quotes). Only available for a [Jira Interface Configuration](#jira-interface-configuration) [filter](#jira-interface-configuration-filter) or [Field](#field) [calculation](#field-calculation) Expression. If the field references a normal [source_id](#field-source_id), the Expression may only reference Field elements within that same [source_id](#field-source_id). If [source_id](#field-source_id) references the [Calculated Source](#special-sources-calculated), then the Expression may reference any other Field element, however the resulting Field may not be used for comparison in a [FieldPair](#fieldpair) (display only).
- `randint(x)`: Returns a random `int` below `x`.
- `rand()`: Returns a random `float` between 0 and 1.
- `int(x)`: Returns `x` converted to an `int`.
- `float(x)`: Returns `x` converted to a `float`.
- `str(x)`: Returns `x` converted to an `str`.
- `sum(x)`: Returns the sum of the elements of `x`. Empty elements are ignored.
- `count(x)`: Returns the count of the elements of `x`. Empty elements are ignored.
- `min(x)`: Returns the minimum of the elements of `x`. Empty elements are ignored.
- `max(x)`: Returns the maximum of the elements of `x`. Empty elements are ignored.
- `avg(x)`: Returns the average (arithmetic mean) of the elements of `x`. Empty elements are ignored.
- `date(...)`: Returns a `date` from the specified arguments.  See python [date](https://docs.python.org/3/library/datetime.html#date-objects).
- `timedelta(...)`: Returns a `date` from the specified arguments.  See python [timedelta](https://docs.python.org/3/library/datetime.html#timedelta-objects).

##### Expression Names

- `self`: Returns the underlying value of [Field](#field) which references it. Only available for a [transform](#field-transform) Expression.
- `True`: The literal `true`.
- `False`: The literal `false`.

##### Expression Operators

- `+`: Add. `x + y`
- `-`: Subtract. `x - y`
- `/`: Divide. `x / y`
- `*`: Multiply. `x * y`
- `**`: Exponent (to the power of). `x ** y`
- `%`: Modulus (remainder). `x % y`
- `>>`: Right shift. `x >> y`
- `<<`: Left shift. `x << y`
- `&`: Btiwise and. `x & y`
- `|`: Bitwise or. `x | y`
- `~`: Bitwise invert. `~x`
- `^`: Bitwise expclusive or (xor). `x ^ y`
- `if`: Conditional. `'Some value' if x == y else 'Other value'`

###### Boolean Expression Operators

- `==`: Equals. `x == y`
- `!=`: Does not equal. `x == y`
- `<`: Less than. `x < y`
- `>`: Greater than. `x > y`
- `<=`: Less than or equal to. `x <= y`
- `>=`: Greater than or equal to. `x >= y`
- `in`: Contains. `x in y`
- `and`: Logical and. `x and y`
- `or`: Logical or. `x or y`
- `not`: Logical invert. `not x`

##### Display Format

In general, a Display Format is expressed as a [Python format string](https://docs.python.org/3/library/string.html), on which the `format()` method is called with a single argument: the target field's value which will always be in the 0-index. For example, `"{0:.2f} hours"` could be used to represent a [Field](#field) having a [NUMBER](#datatypeenum-number) [type](#field-type) or [output_type](#field-output_type) with 2 decimal digits of precision followed by a string literal to indicate units ("hours").

###### ListDisplayFormat

A special Display Format is available for lists which comprise multiple elements within a single value. A list's format is described by a [ListDisplayFormat](#listdisplayformat).

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="listdisplayformat-list_prefix">list_prefix</a> | string | Optional | String prefix for the entire list |
| <a name="listdisplayformat-list_suffix">list_suffix</a> | string | Optional | String suffix for the entire list |
| <a name="listdisplayformat-item_prefix">item_prefix</a> | string | Optional | String prefix for each item in the list |
| <a name="listdisplayformat-item_delimiter">item_delimiter</a> | string | `", "` | String delimiter for each item in the list |
| <a name="listdisplayformat-item_suffix">item_suffix</a> | string | Optional | String suffix for each item in the list |

##### Excel Display Format

An Excel Display Format is the same as a [number format code](https://support.microsoft.com/en-us/office/number-format-codes-5026bbd6-04bc-48cd-bf33-80f18b4eae68) for Microsoft Excel.

### FieldPair

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="fieldpair-id">id</a> | string | *Concatenation of the [data_id](#field-data_id) values of [Field](#field) elements referenced by [left_field_id](#fieldpair-left_field_id) and [right_field_id](#fieldpair-right_field_id)* | Identifier for the field pair; must be unique among all [FieldPair](#fieldpair) elements. |
| <a name="fieldpair-left_field_id">left_field_id</a> | string | Required | [Field](#field) [id](#field-id) from the [left_source](#left_source) to compare. |
| <a name="fieldpair-right_field_id">right_field_id</a> | string | Required | [Field](#field) [id](#field-id) from the [right_source](#right_source) to compare. |
| <a name="fieldpair-sor">sor</a> | [SorEnum](#sorenum) | Required | Enumerated type to indicate which field is the system of record (source of truth) for copying values. See [SorEnum](#sorenum). |
| <a name="fieldpair-display">display</a> | boolean | `true` | Indicates whether to display this field pair in the output report. |
| <a name="fieldpair-display_index">display_index</a> | integer | Optional | Positional index to display this field pair in the output report; must be unique among all [Field](#field) and [FieldPair](#fieldpair) elements. See [Display Index](#display-index). |

#### Display Index

Display Index is a mechanism to incidate a preferred order to dipslay [Field](#field) and [FieldPair](#fieldpair) elements in the output report. The Display Index is zero-based, meaning a [Field](#field) with a Display Index of 0 will appear in the 1st position. Note that since [Field](#field) elements are outputted in a single column and [FieldPair](#fieldpair) elements are outputted in two columns, there isn't a one-to-one relationship between Display Indexes and columns. Because a Display Index must be unique, an element that defines this attribute is guaranteed to be displayed in that index, unless the index would place it beyond the size of the entire collection. In this case, the element will be displayed in the last position. Gaps in contiguously-defined Display Indexes are filled with elements in the order in which they are defined in the configuration, giving higher priority to [Field](#field) elements over [FieldPair](#fieldpair) elements.

#### SorEnum

| Enumeration | Description |
| -------- | ----------- |
| <a name="sorenum-left">LEFT</a> | Indicates that [Field](#field) associated with the [left_source](#left_source) is the system of record. |
| <a name="sorenum-right">RIGHT</a> | Indicates that [Field](#field) associated with the [right_source](#right_source) is the system of record. |
| <a name="sorenum-no_sor">NO_SOR</a> | Indicates that neither [Field](#field) is the system of record. |

### ComparisonConfig

| Key name | Value type | Required/<br>Optional/<br>Default | Description |
| -------- | ---------- | --------------------------------- | ----------- |
| <a name="comparisonconfig-sort_field_id">sort_field_id</a> | string | Required | [Field](#field) [id](#field-id) by which to sort the output. |
| <a name="comparisonconfig-reverse">reverse</a> | boolean | Required | Indicates whether to sort the output in reverse order of the specified [Field](#field). |
