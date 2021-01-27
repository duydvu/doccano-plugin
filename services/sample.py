import json
import random
import jsonlines

from .common import build_label_map, map_labels

doccano_client = None


def handle_request(request, client):
    global doccano_client
    doccano_client = client
    project_id, start, end, sample_size, new_project_name, username = extract_request(request)
    labels_map = build_label_map(doccano_client, project_id)
    indexes, documents = sample_documents(project_id, start, end, sample_size)
    file_name = f'{project_id}-{abs(hash(" ".join(map(str, indexes))))}.jsonl'
    file_path = f'tmp/{file_name}'

    response = doccano_client.create_project(
        name=f'{new_project_name}-{start}-{end}',
        description=file_name,
        collaborative_annotation=True,
    )
    new_project_id = response['id']
    create_labels(new_project_id)
    assign_user(new_project_id, username)

    map_labels(labels_map, documents)

    with jsonlines.open(file_path, mode='w') as writer:
        writer.write_all(documents)
    try:
        doccano_client.post_doc_upload(new_project_id, 'json', file_name, 'tmp')
    except json.JSONDecodeError:
        pass

    return new_project_id


def extract_request(request):
    body = request.get_json(force=True)
    project_id = body['projectId']
    start = body['start']
    end = body['end']
    sample_size = body['sampleSize']
    new_project_name = body['newProjectName']
    username = body['username']

    if start < 0:
        raise Exception('Start must be greater than 0.')

    if start >= end:
        raise Exception('Start must be less than or equal to End.')

    if 'detail' in doccano_client.get_project_detail(project_id):
        raise Exception('Project is not found.')

    total = doccano_client.get_project_statistics(project_id)['total']
    if end > total:
        raise Exception(
            f'End exceeds the total number of mention in this project. Maximum is {total}.')

    users = doccano_client.get_user_list()
    if not any([user['username'] == username for user in users]):
        raise Exception('User is not found.')

    return project_id, start, end, sample_size, new_project_name, username


def sample_documents(project_id, start, end, sample_size):
    indexes = sorted(random.sample(range(start, end), sample_size))
    documents = []
    for index in indexes:
        response = doccano_client.get_document_list(project_id, url_parameters={
            'offset': [index],
            'limit': [1],
        })
        response['results'][0]['meta'] = json.loads(response['results'][0]['meta'])
        documents.extend(response['results'])
    return indexes, documents


def create_labels(project_id):
    labels = json.load(open('./category.labels.json', encoding='utf-8'))
    for label in labels:
        doccano_client.create_label(
            project_id=project_id,
            text=label['text'],
            prefix_key=label['prefix_key'],
            suffix_key=label['suffix_key'],
            background_color=label['background_color'],
            text_color=label['text_color'],
        )


def assign_user(project_id, username):
    roles = doccano_client.get_rolemapping_list(project_id)
    for role in roles:
        if role['username'] == username:
            doccano_client.delete(f'v1/projects/{project_id}/roles/{role["id"]}')
            break
    users = doccano_client.get_user_list()
    for user in users:
        if user['username'] == username:
            doccano_client.post(f'v1/projects/{project_id}/roles', data={'role': 1, 'user': user['id']})
