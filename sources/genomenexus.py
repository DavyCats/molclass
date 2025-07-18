import urllib.parse

from util import reverse_complement
from .source_result import Source, SourceURL

class GenomeNexus(Source):
    def set_entries(self):
        self.entries = {
            ("chr", "pos", "ref", "alt"): self.chr_pos_ref_alt,
        }

    async def check_validity(self, query):
        enc_query = urllib.parse.quote(query)
        api_url = f"https://www.genomenexus.org/annotation/{enc_query}?fields=annotation_summary"
        resp, json = await self.async_get_json(api_url)
        return json.get("successfully_annotated", False)

    async def chr_pos_ref_alt(self):
        """
        Simply add a URL to the variant
        """
        chrom = self.variant["chr"]
        pos = self.variant["pos"]
        ref = self.variant["ref"]
        alt = self.variant["alt"]

        # Check if annotation exists for ref/alt, if not try the reverse complement
        if not await self.check_validity(f"{chrom}:g.{pos}{ref}>{alt}"):
            ref = reverse_complement(ref)
            alt = reverse_complement(alt)
            if not await self.check_validity(f"{chrom}:g.{pos}{ref}>{alt}"):
                self.html_text = (f"No annotation found for either {chrom}:g.{pos}{self.variant['ref']}>{self.variant['alt']} "
                                  f"or {chrom}:g.{pos}{ref}>{alt} (reverse complement).")
                self.found = False
                return

        url = f"https://www.genomenexus.org/variant/{chrom}:g.{pos}{ref}>{alt}"
        self.html_links["main"] = SourceURL(f"{chrom}:g.{pos}{ref}>{alt}", url)

    def get_name(self):
        return "Genome Nexus"