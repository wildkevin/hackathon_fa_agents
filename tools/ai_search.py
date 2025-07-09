from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from semantic_kernel.functions import kernel_function



search_endpoint: str = "https://agentichack-search.search.windows.net"
search_api_key: str = "CREbJyNtMs5jEiHfViliY08ajSJOAfFCwn9XF0VJlIAzSeBbNNfv"
index_name: str = "tesco_report_agent"
credential = AzureKeyCredential(search_api_key)

class RagPlugin:
    """
    A rag plugin for RAG Agent.
    """

    @kernel_function(
        name="retrieve_doc",
        description="retrieve relative sector information for the company and the root cause of metrics changes from AI Search for RAG Agent"
    )
    def retrieve_doc(self,query):

        print(f"QQQQQQ{query}")

        search_client = SearchClient(endpoint=search_endpoint, credential=credential, index_name=index_name)
        results = search_client.search(query_type='simple',
                                       search_text=query,
                                       top=10,
                                       include_total_count=True)
        docs = "\n".join(result['page_chunk'] for result in results)
        # print(f"AAAAA:{docs}")
        return docs