import os
import jsonlines
import pandas as pd
from doccano_api_client import DoccanoClient

from .common import build_label_map, map_labels, get_all_documents


doccano_client: DoccanoClient = None
download_dir = 'download'


def handle_request(request, client: DoccanoClient):
    global doccano_client
    doccano_client = client
    project_id = extract_request(request)
    truth_documents = get_all_documents(doccano_client, project_id)

    labels_map = build_label_map(doccano_client, project_id)
    map_labels(labels_map, truth_documents)

    for document in truth_documents:
        document['labels'] = ','.join(document['labels'])

    file_name = f'{project_id}.xlsx'
    file_path = os.path.join(download_dir, file_name)
    pd.DataFrame(truth_documents).to_excel(file_path, index=False, engine='xlsxwriter')
    return file_name


def extract_request(request):
    project_id = request.args.get('projectId')

    if 'detail' in doccano_client.get_project_detail(project_id):
        raise Exception('Project is not found.')

    return project_id
