# SudskiRegistarDataAPI

## It is not an official library, it is a community project.

##### A light weight Python library for the SudReg Web API

## Documentation

SudReg Web API's full documentation is online at [Sudski registar api - javni korisnici](https://sudreg-podaci.pravosudje.hr/docs/services/5adda5d214bb2910b8322a96/operations/bris_pravni_oblik_Get).

## Installation

```bash
pip install sudreg
```

## Quick Start

```python
from sudreg_data_api import SudskiRegistarDataAPI

api = SudskiRegistarDataAPI("Subscription-Key")

print(api.get_subjekt_detalji(tip_identifikatora="oib", identifikator="53056966535", expand_relations=True))

```

## Documentation

[Upute za razvojne inženjere - v3.0.0.pdf](https://sudreg-data.gov.hr/ords/r/srn_rep/116/files/static/v11/Upute%20za%20razvojne%20in%C5%BEenjere%20-%20v3.0.0.pdf)

Zadnja verzija - preporučena za novi razvoj
Open API specifikacija v3 servisa za javne korisnike: [open_api_javni_v3.json](https://sudreg-data.gov.hr/api/javni/dokumentacija/open_api)
Ogledna baza podataka v3 servisa za javne korisnike (Oracle dijalekt): [ogledna_baza_javni.sql](https://sudreg-data.gov.hr/api/javni/dokumentacija/reference_database_script)
ER model podataka v3 servisa za javne korisnike: [er_model_javni.pdf](https://sudreg-data.gov.hr/api/javni/dokumentacija/er_diagram)
Changelog za javne korisnike: [changelog.html](https://sudreg-data.gov.hr/api/javni/dokumentacija/changelog)
[SwaggerHub za javne korisnike](https://app.swaggerhub.com/apis/mpu.gov.hr/sudreg_javni/)