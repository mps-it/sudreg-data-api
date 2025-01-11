from base64 import b64encode

import requests


def basic_auth(username, password):
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    return f'Basic {token}'


class SudskiRegistarDataAPI:
    """
       A Python client for the Sudski Registar Data API.

       This client provides an interface to interact with the Sudski Registar Data API,
       which provides access to various legal and business-related data.

       Attributes:
        base_url (str): The base URL for the Sudski Registar Data API.
        base_url_api (str): The base API URL for the Sudski Registar Data API.
        client_id (str): Client ID for the Sudski Registar Data API.
        client_secret (str): Client secret for the Sudski Registar Data API.
        requests_per_minute (int): The number of requests allowed per minute.
        token (str): The access token for the Sudski Registar Data API.
        snapshot_id (str): Snapshot ID for the API requests.
        headers (dict): The headers to be used for the API requests.
   """

    def __init__(self, client_id, client_secret, production=False, public=True):
        """
            Initializes the SudskiRegistarAPI with client ID and client secret.

            Args:
                client_id (str): Client ID for the Sudski Registar Data API.
                client_secret (str): Client secret for the Sudski Registar Data API.
                production (bool): Whether to use the production Sudski Registar Data API.
                public (bool): Whether to use the public Sudski Registar Data API.
        """
        if production:
            self.base_url = "https://sudreg-data.gov.hr/api/"
        else:
            self.base_url = "https://sudreg-data-test.gov.hr/api/"

        if public:
            self.base_url_api = self.base_url + "javni/"
        else:
            self.base_url_api = self.base_url + "drzavna_tijela/"

        self.client_id = client_id
        self.client_secret = client_secret
        self.requests_per_minute = 6
        self.token = ""
        self.snapshot_id = None
        self.omit_nulls = None
        self.no_data_error = None

        if not self.token:
            self.get_token()

        self.headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json',
        }

    def get_token(self):
        """
            Sends a request to the Sudski Registar Data API to get an access token.

           Raises:
               Exception: Get OAuth 2.0 token was unsuccessful.
        """
        url = self.base_url + "oauth/token"
        headers = { 'Authorization' : basic_auth(self.client_id, self.client_secret) }
        payload = { "grant_type": "client_credentials" }

        response = requests.post(url, headers=headers, data=payload)
        if response.status_code == 200:
            self.token = response.json()["access_token"]
        else:
            raise Exception("Error getting token: " + response.text)

    def set_snapshot_id(self, snapshot_id):
        """
            Sets the snapshot ID for the API requests.

            Args:
                snapshot_id (int): Specifies the data set to be downloaded,
                    if not specified the latest set is returned.
        """
        self.snapshot_id = str(snapshot_id)

    def set_omit_nulls(self, omit_nulls):
        """
            Sets the snapshot ID for the API requests.

            Args:
                omit_nulls (bool, optional): Specifies whether empty (null) keys are omitted from the returned data,
                    if not specified null keys are omitted.
        """
        self.omit_nulls = int(omit_nulls)

    def set_no_data_error(self, no_data_error):
        """
            Sets the no data error parameter for the API requests.

            Args:
                no_data_error (bool, optional): Specifies whether a request that did not find the requested data returns
                    an error (1) or an empty object (0), if not specified an error is returned.
        """
        self.no_data_error = int(no_data_error)

    def main_parameters(self, expand_relations=None, history_columns=None):
        """
            Returns the main parameters for the API requests.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.
        """
        params = {}
        if self.snapshot_id is not None:
            params["snapshot_id"] = self.snapshot_id
        if expand_relations is not None:
            params["expand_relations"] = int(expand_relations)
        if history_columns is not None:
            params["history_columns"] = int(history_columns)
        if self.no_data_error is not None:
            params["no_data_error"] = self.no_data_error
        if self.omit_nulls is not None:
            params["omit_nulls"] = self.omit_nulls
        return params

    def paging_parameters(self, expand_relations=None, offset=None, limit=None):
        """
            Returns the paging parameters for the API requests.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.
        """
        params = self.main_parameters(expand_relations, None)
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        return params

    def get_bris_pravni_oblici(self, expand_relations=None, history_columns=None):
        """
            Codebook of BRIS legal forms.

            The Business Registers Interconnection System (BRIS) defines the legal form of the entities managed in it
            for all countries and registers that are members of BRIS. For example, the German GMBH is equivalent to the
            domestic DOO legal form. Not all legal forms are maintained in BRIS.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "bris_pravni_oblici"
        params = self.main_parameters(expand_relations, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_bris_registri(self, expand_relations=None, history_columns=None):
        """
            Codebook of BRIS registers.

            The Business Registers Interconnection System (BRIS) is a central EU platform that aggregates data from all
            business registers of the member states.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "bris_registri"
        params = self.main_parameters(expand_relations, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_counts(self):
        """
            List of total number of available active and historical rows for all methods/tables.

            For pagination purposes, the system records the total number of all available rows, and separately,
            the number of available active rows, for each method/table.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "counts"
        params = self.main_parameters(None, None)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_detalji_subjekta(self, expand_relations=None, tip_identifikatora=None, identifikator=None):
        """
            All data about the subject collected into one structured object.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                tip_identifikatora (str, required): Specifies the type of identifier used to identify the subject,
                    allowed values are oib and mbs.
                identifikator (str, required): Specifies the identifier of the subject.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "detalji_subjekta"
        params = self.main_parameters(expand_relations, None)
        if tip_identifikatora is not None:
            if tip_identifikatora in ["oib", "mbs"]:
                params["tip_identifikatora"] = tip_identifikatora
            else:
                raise ValueError("tip_identifikatora must be 'oib' or 'mbs'")
        else:
            raise ValueError("tip_identifikatora is required")
        if identifikator is not None:
            params["identifikator"] = identifikator
        else:
            raise ValueError("identifikator is required")
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_djelatnosti_podruznica(self, offset=None, limit=None):
        """
            Branch activity records.

            From 2020, the activities of branches no longer have to be entered. As with the subject's activities,
            these data were initially entered according to the NKD codebook, and later it was possible to enter free text.
            In case the data in the same line is entered in both ways, both values are valid.
            The natural primary key is (MBS, PODRUZNICA_RBR, DJELATNOST_RBR).
            Serial numbers are given by the DJELATNOST_RBR field.
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "djelatnosti_podruznica"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_drzave(self, history_columns=None):
        """
            Country code book.

            Args:
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "drzave"
        params = self.main_parameters(None, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_email_adrese(self, offset=None, limit=None):
        """
            Records of e-mail addresses of subjects.

            The court register does not validate the addresses applied for registration by subjects.
            The natural primary key is (MBS, EMAIL_ADRESA_RBR).
            Serial numbers are given by the field EMAIL_ADRESA_RBR.
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "email_adrese"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_email_adrese_podruznica(self, offset=None, limit=None):
        """
            Branch email address records.

            The court register does not validate the addresses applied for registration by subjects.
            The natural primary key is (MBS, PODRUZNICA_RBR, EMAIL_ADRESA_RBR).
            Serial numbers are given by the field EMAIL_ADRESA_RBR.
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "email_adrese_podruznica"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_evidencijske_djelatnosti(self, offset=None, limit=None):
        """
            List of registration activities of entities.

            Nominally, this data does not belong to the main register book and the subject is not required to enter any
            registered activity. For historical reasons, entry is allowed both according to the NKD code list and as a
            free entry. In the event that data is entered in the same row in both ways, both values are valid.
            The natural primary key is (MBS, DJELATNOST_RBR).
            The ordinal numbers are given by the DJELATNOST_RBR field.
            The table is subordinate to the SUBJEKTI table via a foreign key in the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "evidencijske_djelatnosti"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_gfi(self, offset=None, limit=None):
        """
            Records of submitted annual financial reports of entities.

            Entities are required to submit an annual financial report (GFI) every year (some legal forms are exempt
            from this obligation). The reports themselves are kept at FINA and are available through the website
            https://rgfi.fina.hr/IzvjestajiRGFI.web/main/home.jsp
            The data in this table is for record purposes only and is not kept historically.
            The natural primary key is (MBS, GFI_RBR).
            The ordinal numbers are given by the GFI_RBR field.
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "gfi"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_inozemni_registri(self, offset=None, limit=None):
        """
            Record of data on foreign registers of entities (for foreign branches).

            Foreign register data is maintained only for branches of foreign founders. It contains the name of the
            founder's register, the body with which it is located, the registration number in that register and other
            details - see the description of the INO_PODRUZNICA field in the subjects method.
            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "inozemni_registri"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_jezici(self, history_columns=None):
        """
            Language codebook.

            Args:
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "jezici"
        params = self.main_parameters(None, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_postupci(self, offset=None, limit=None):
        """
            Records of actions taken against subjects.

            The data indicates that the subject is in one of the procedures such as bankruptcy, liquidation, etc.
            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "postupci"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_tvrtke(self, offset=None, limit=None):
        """
            Company records (names) of entities.

            In registry terminology, the company represents the name of the entity (this depends on the legal form,
            so for example, institutions are referred to as the entity name instead of the company).
            The name tag represents the root of the name, for example, for ABC Limited Liability Company,
            the tag would be ABC.
            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "tvrtke"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_skracene_tvrtke(self, offset=None, limit=None):
        """
            Records of abbreviated company entities.

            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "skracene_tvrtke"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_prijevodi_tvrtki(self, offset=None, limit=None):
        """
            Records of translations of company entities.

            The natural primary key is (MBS, PRIJEVOD_TVRTKE_RBR).
            The ordinal numbers are given by the PRIJEVOD_TVRTKE_RBR field.
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "prijevodi_tvrtki"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_prijevodi_skracenih_tvrtki(self, offset=None, limit=None):
        """
            Records of translations of abbreviated company names.

            The natural primary key is (MBS, PRIJEVOD_SKRACENE_TVRTKE_RBR).
            The ordinal numbers are given by the PRIJEVOD_SKRACENE_TVRTKE_RBR field.
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "prijevodi_skracenih_tvrtki"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_sjedista(self, offset=None, limit=None):
        """
            Records of headquarters and addresses of entities.

            In older entries, the address is often not correctly listed by field, but is entered in its entirety in
            the street or foreign settlement field. Such data is corrected manually over time,
            but there will always be some.
            The code books of counties, municipalities, settlements, streets and house numbers are not included
            in the service because they are the property of the State Geodetic Administration (DGU) and
            the Ministry of Justice and Administration does not have the right to redistribute them.
            Third parties can obtain them directly from the DGU. The listed codes correspond to the codes in
            the DGU code books.
            The field NASELJE_VAN_SIFRARNIKA is used for addresses abroad, while for domestic addresses,
            the NAZIV_NASELJA and SIFRA_NASELJA are used. As a rule, the domestic and foreign settlement fields should
            not be used at the same time, but for a small number of subjects, both are entered for historical reasons.
            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table via a foreign key in the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "sjedista"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_pravni_oblici(self, expand_relations=None, offset=None, limit=None):
        """
            Records of legal forms of entities.

            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "pravni_oblici"
        params = self.paging_parameters(expand_relations, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_pretezite_djelatnosti(self, offset=None, limit=None):
        """
            Records of the main activities of entities.

            Activities determined by the Classification Notification issued by the Central Bureau of Statistics.
            Entered according to the NKD code list.
            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table via a foreign key in the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "pretezite_djelatnosti"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_predmeti_poslovanja(self, expand_relations=None, offset=None, limit=None):
        """
            Records of business activities of entities.

            From 2020, entities are required to register only a small part of activities whose registration is
            prescribed by some special laws (e.g. banking activities), while previously all activities that can
            now and do not have to be registered as record-keeping activities were registered. Initially, these
            activities were entered according to the NKD codebook, and later it was possible to enter them in
            free text because the codebook was too restrictive. In case the data in the same line is entered in
            both ways, both values are valid.
            The natural primary key is (MBS, ACTIVITY_RBR).
            Serial numbers are given by the ACTIVITY_RBR field.
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "predmeti_poslovanja"
        params = self.paging_parameters(expand_relations, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_temeljni_kapitali(self, offset=None, limit=None):
        """
            Records of the basic capital of entities.

            The natural primary key is (MBS, TEMELJNI_KAPITAL_RBR).
            Ordinal numbers are given by the field TEMELJNI_KAPITAL_RBR.
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.
            An entity can have more than one capital at the same time usually due to different currencies.
            Most entities have only one capital.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "temeljni_kapitali"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_nazivi_podruznica(self, offset=None, limit=None):
        """
            Records of names of branches of entities.

            The PROCEDURE field serves a similar purpose to the data in the procedures method. In the case of
            the main branch of a foreign entity, this data indicates the bankruptcy/liquidation procedure against
            the entity in the Republic of Croatia. Another important difference is that the domain here is narrower
            and can only take on the following values: 1 - No procedure, 2 - Bankruptcy, 3 - Liquidation.
            The reason is that the name of the branch does not change in pre-bankruptcy procedures as it does in
            bankruptcies and liquidations.
            The GLAVNA_PODRUZNICA field indicates that this is the main branch of a foreign entity and also allows
            historical tracking of this data (because the serial number of the main branch in the entities method
            has no history). For domestic entities, this field is always 0, while for foreign entities, at any
            given time, exactly one branch is marked with 1. In practice, there are only a few entities where
            the main branch has changed and is no longer the one with serial number 1.
            The natural primary key is (MBS, PODRUZNICA_RBR).
            There are no serial numbers other than the branch number.
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "nazivi_podruznica"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_skraceni_nazivi_podruznica(self, offset=None, limit=None):
        """
            Records of names of branches of entities.

            The natural primary key is (MBS, PODRUZNICA_RBR).
            There are no serial numbers other than the branch number.
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "skraceni_nazivi_podruznica"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_sjedista_podruznica(self, offset=None, limit=None):
        """
            Records of headquarters and addresses of branches of entities.

            Branches can only have domestic addresses, so there are no fields for the country or the entry of
            settlements by free entry.
            In the case of the main branch of a foreign entity, this information indicates the headquarters of
            the entity registered in the Republic of Croatia.
            Code books of counties, municipalities, settlements, streets and house numbers are not included in
            the service because they are the property of the State Geodetic Administration (DGU) and
            the Ministry of Justice, and the administration has no right to redistribute them.
            Third parties can obtain them directly from DGU. The specified codes correspond to the codes in
            the DGU code books.
            The natural primary key is (MBS, PODRUZNICA_RBR).
            Serial numbers other than the number of the branch office do not exist.
            The table is subordinate to the SUBJEKTI table through a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "sjedista_podruznica"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_objave_priopcenja(self, offset=None, limit=None):
        """
            Records of the manner in which entities publish their announcements.

            Indicates the channel through which entities publish their communications
            (e.g., website, newspaper, etc.).
            The natural primary key is (MBS).
            The table is subordinate to the SUBJEKTI table via a foreign key on the MBS field.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "objave_priopcenja"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_promjene(self, offset=None, limit=None):
        """
            List of recent changes to entities.

            The list contains the latest time and SCN changes for the subjects that have had changes.
            By comparing it with the list from the previously downloaded snapshot, it is possible to determine
            for which subjects there were changes between the snapshots being compared. The mechanism is described in
            more detail in the developer's guide.

            Args:
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "promjene"
        params = self.paging_parameters(None, offset, limit)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_subjekti(self, tvrtka_naziv=None, only_active=None, offset=None, limit=None):
        """
            Records of basic data on entities.

            Entities can be active or inactive, but this basic data is not recorded historically and always
            represents the current state.
            The personal identification number is an identifier maintained by the tax administration.
            Since it was introduced after the registry began operating, it is not a mandatory field and there
            are many deleted entities that were never assigned. Active entities generally have an OIB,
            but there are exceptions where the OIB is unknown or not assigned. Over time, the number of such
            entities decreases, but they will probably always exist.
            Courts are organized hierarchically in two levels (see the courts method), so there are two
            foreign keys to the SUDOVI table (fields SUD_ID_NADLEZAN, SUD_ID_SLUZBA).
            It is important to know that both keys can point to the same court if the case is located at a
            commercial court, and that the court from the SUD_ID_SLUZBA column is primarily competent,
            but both courts have the right to resolve all files within the competent court.
            The date of establishment is not known for some very old entities that were created before 1995,
            when the registry was established in its current form.
            The natural primary key is (MBS).

            Args:
                tvrtka_naziv (string, optional): Name/company of entities being retrieved.
                only_active (bool, optional): Specifies whether all data or only active data is returned,
                    if not specified only active data is returned.
                offset (int, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                limit (int, optional): Specifies the number of rows (page size) for paging,
                    if not specified, 1000 rows are returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "subjekti"
        params = self.paging_parameters(None, offset, limit)
        if tvrtka_naziv is not None:
            params["tvrtka_naziv"] = tvrtka_naziv
        if only_active is not None:
            params["only_active"] = only_active
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_snapshots(self):
        """
            List of recordings from the main court registry database.

            The method returns data on all snapshots of the registry master database that can be downloaded
            through the service.
            Data for open data services is refreshed every working day, which provides a consistent snapshot of
            the master database. In doing so, the snapshot from the previous day is NOT immediately deleted
            from the open data database. After each successful completion of the daily refresh, the newly
            copied snapshot is assigned a so-called snapshot_id identifier, and the exact moment at which
            the data was copied from the registry master database and until when the snapshot will be safely
            available through the service are recorded. Old snapshots are removed on a first-in-first-out basis
            only after the specified deadline has expired.
            Additional details about snapshots and how to use them can be found in the developer instructions.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "snapshots"
        params = {}
        if self.no_data_error is not None:
            params["no_data_error"] = self.no_data_error
        if self.omit_nulls is not None:
            params["omit_nulls"] = self.omit_nulls
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_nacionalna_klasifikacija_djelatnosti(self, history_columns=None):
        """
            National Classification of Activities.

            The codebook of the national classification of activities maintained by the Central Bureau of Statistics
            of the Republic of Croatia. It is based on the EU classification of activities.
            Over time, the bureau has issued several versions of the classification and a single code in different
            versions generally does not represent the same activity.
            From 1.1.2025. a new version of the codebook is being introduced in which NKD codes have five digits instead
            of four.

            Args:
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "nacionalna_klasifikacija_djelatnosti"
        params = self.main_parameters(None, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_statusi(self):
        """
            Row status codebook.

            Applies to the status field in all tables/methods.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "statusi"
        params = self.main_parameters(None, None)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_sudovi(self, expand_relations=None, history_columns=None):
        """
            Code of Courts.

            Commercial courts are organized hierarchically in two levels. In the past, all courts were equal,
            but in 2011, a new organization was introduced and some of the previous courts became permanent
            offices of the remaining courts, which are now their superiors. Permanent services are linked to
            their competent courts through the SUD_ID_NADLEZAN field.
            All address information refers to the seat of the court.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "sudovi"
        params = self.main_parameters(expand_relations, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_valute(self, expand_relations=None, history_columns=None):
        """
            Currency code book.

            Args:
                expand_relations (bool, optional): Specifies whether data from linked codebooks is added to the response
                    or whether only the ID of the foreign key is included, if not specified only IDs are returned.
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "valute"
        params = self.main_parameters(expand_relations, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_vrste_gfi_dokumenata(self):
        """
            Code list of types of GFI documents.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "vrste_gfi_dokumenata"
        params = self.main_parameters(None, None)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_vrste_postupaka(self):
        """
            Codebook of types of procedures.

            It refers to the actions of entities or subsidiaries (bankruptcies, liquidations, ...).

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "vrste_postupaka"
        params = self.main_parameters(None, None)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()

    def get_vrste_pravnih_oblika(self, history_columns=None):
        """
            Code book of types of legal forms.

            Args:
                history_columns (bool, optional): Specifies whether the STATUS, VRIJEDI_OD and VRIJEDI_DO columns
                    are included in historically maintained code lists - if not specified, the columns are not returned.

            Returns:
                dict: The response from the API as a dictionary.

           Raises:
               requests.HTTPError: If the API response was unsuccessful.
        """

        endpoint = "vrste_pravnih_oblika"
        params = self.main_parameters(None, history_columns)
        response = requests.get(self.base_url_api + endpoint, headers=self.headers, params=params)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
        return response.json()