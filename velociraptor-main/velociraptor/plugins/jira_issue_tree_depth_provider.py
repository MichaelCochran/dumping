from typing import Any, Optional
from velociraptor.interfaces.jira_interface import JiraInterface, JiraIssueRecord, JiraResults
from velociraptor.types.field import DataTypeEnum, Field
from velociraptor.types.i_jira_value_provider import IJiraValueProvider
from velociraptor.types.i_record_graph_collection_provider import IRecordNode

class JiraIssueTreeDepthProvider(IJiraValueProvider):

    TREE_DEPTH_FIELD = Field(data_id="__tree_depth", type=DataTypeEnum.NUMBER)

    def __init__(self, plugin_config: Optional[Any], jira_interface: JiraInterface):
        # Do nothing
        pass

    def get_required_data_ids(self) -> list[str]:
        return []

    def get_produced_data_ids(self) -> list[str]:
        return [self.TREE_DEPTH_FIELD.data_id]

    def _walk_tree(self, record_node: IRecordNode, tree_depth: int):
        record = record_node.get_record()
        if record is None:
            print(f"Warning: Issue {record_node.get_key()} is linked but was not fetched by JQL query")
            return
        elif not isinstance(record, JiraIssueRecord):
            raise Exception("Expecting JiraIssueRecord")

        record.set_custom_value(self.TREE_DEPTH_FIELD, tree_depth)

        for child_node in record_node.get_child_nodes():
            self._walk_tree(child_node, tree_depth + 1)

    def process_results(self, results: JiraResults):
        if results.issue_graph_collection is None:
            raise Exception("JiraIssueTreeDepthProvider requires a JiraIssueGraphProvider to be configured.")

        # Set default to None so that error nodes are distinguishable from nodes with zero points
        for record in results.issue_records:
            record.set_custom_value(self.TREE_DEPTH_FIELD, None)

        for record_graph in results.issue_graph_collection.get_record_graphs():
            # Tree guarantees safety to do a recursive depth-first search to sum up story points without
            # - Cycles (infinite loop)
            # - Double-counting story points where contributed to two parents who share same parent (diamond graph)
            if not record_graph.is_tree():
                continue

            for root_node in record_graph.get_root_nodes():
                self._walk_tree(root_node, 0)