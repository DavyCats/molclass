from typing import List
from pydantic import BaseSettings, Field

from sources import *
from util import get_release_tag

class Settings(BaseSettings):
    debug: bool = Field(True, env="DEBUG")
    port: int = Field(8080, env="PORT")
    release_tag: str = Field(get_release_tag())

    sources: List[type] = [
        GenomeNexus,
        Alamut,
        COSMIC,
        ClinVar,
        Franklin,
        CKB,
        LOVD,
        OncoKB,
        cBioPortal,
        Varsome,
        HMF,
        Mutalyzer,
        SpliceAI,
        BoostDM,
        # is_hidden()=True sources should be at the end, to not leave gaps in source layout
        Clingen,
        Ensembl,
        # GnomAD,
        dbSNP,
        TP53,
    ]

    def __init__(self):
        super().__init__()
        self.sources = [source for source in self.sources if source.is_complete(source)]

settings = Settings()
