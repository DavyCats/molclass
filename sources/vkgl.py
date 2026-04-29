import urllib.parse

from jinja2 import BaseLoader, Environment

from .source_result import Source

SUMMARY_TABLE_TEMPLATE = """
<table class='table caption-top'>
    <tr>
        <th>Variant</th>
        <th>Consensus</th>
        <th>Support</th>
    </tr>
{% for variant, data in vkgl_summary.items() %}
    <tr>
        <td>{{ variant }}</td>
        <td>{{ data.consensus }}</td>
        <td>{{ data.support }}</td>
    </tr>
{% endfor %}
</table>
"""

class VKGL(Source):
    def set_entries(self):
        self.entries = {
            ("gene", "gene_cdot"): self.gene_cdot,
            ("gene", "cdot"): self.gene_cdot,
        }
        return self.entries

    async def gene_cdot(self):
        """
        Query the molgenis api.
        """
        gene = self.variant["gene"]
        cdot = self.variant["cdot"]
        enc_gene = urllib.parse.quote(gene)
        enc_cdot = urllib.parse.quote(cdot)
        query_url = f"https://vkgl.molgeniscloud.org/api/v2/vkgl_public_consensus?q=gene=='{enc_gene}';c_notation=='{enc_cdot}'"
        _, json = await self.async_get_json(query_url)
        if not json or len(json["items"]) < 1:
            self.log_warning(f"No rows found for '{cdot}'")
            self.found = False
            self.html_text = "Variant not found"
            return

        vkgl_summary_dict = {}
        for item in json["items"]:
            variant_data = {
                "consensus": item["classification"]["label"],
                "support": item.get("support", "")
            }
            vkgl_summary_dict[item["label"]] = variant_data

        template = Environment(loader=BaseLoader()).from_string(SUMMARY_TABLE_TEMPLATE)
        self.html_text = template.render(
            vkgl_summary=vkgl_summary_dict
        )

    def get_name(self):
        return "VKGL Consensus"