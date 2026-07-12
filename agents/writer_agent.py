from agents.prompts import WRITER_PROMPT


class WriterAgent:

    def __init__(self, model):
        self.model = model
        self.chain = WRITER_PROMPT | model

    def write_report(
        self,
        analysis_results,
        sources
    ):
        """
        Generate final research report.
        """

        response = self.chain.invoke(
            {
                "analysis_results": analysis_results,
                "sources": sources
            }
        )

        return response.content