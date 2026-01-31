import msal
import logging

def get_graph_token(client_id, client_secret, tenant_id):
    try:
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        scope = ["https://graph.microsoft.com/.default"]

        app = msal.ConfidentialClientApplication(
            client_id=client_id,
            authority=authority,
            client_credential=client_secret
        )

        token = app.acquire_token_for_client(scopes=scope)

        if "access_token" not in token:
            raise Exception(token)

        return token["access_token"]

    except Exception as e:
        logging.error(f"Graph token acquisition failed: {e}")
        raise
