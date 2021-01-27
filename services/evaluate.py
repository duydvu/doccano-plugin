import json
import jsonlines
import numpy as np
from typing import List
from sklearn.metrics import classification_report

from .common import build_label_map, map_labels

doccano_client = None
labels = list(map(lambda x: x['text'], json.load(
    open('./category.labels.json', encoding='utf-8'))))


def handle_request(request, client):
    global doccano_client
    doccano_client = client

    project_id = extract_request_2(request)

    truth_documents = doccano_client.get_document_list(project_id, {
        'limit': [doccano_client.get_project_statistics(project_id)['total']],
        'offset': [0],
    })['results']
    for doc in truth_documents:
        doc['meta'] = json.loads(doc['meta'])

    predict_documents = list(jsonlines.open(f'tmp/{doccano_client.get_project_detail(project_id)["description"]}'))

    labels_map = build_label_map(doccano_client, project_id)

    map_labels(labels_map, truth_documents)

    y_true, y_pred = extract_prediction(truth_documents, predict_documents)
    return calculate_macro_f1_score(y_true, y_pred)


def extract_request_2(request):
    project_id = request.args.get('projectId')

    if 'detail' in doccano_client.get_project_detail(project_id):
        raise Exception('Project is not found.')

    return project_id


def extract_prediction(truth_documents, predict_documents):
    y_true = list(map(lambda doc: doc['labels'], truth_documents))
    ids = list(map(lambda doc: doc['meta']['id'], truth_documents))
    predict_document_dict = {}
    for doc in predict_documents:
        predict_document_dict[doc['meta']['id']] = doc
    y_pred = [predict_document_dict[i]['labels'] for i in ids]
    return y_true, y_pred


def calculate_macro_f1_score(true_labels: List[List[str]], pred_labels: List[List[str]]):
    y_true, y_pred = [], []
    for true_label, pred_label in zip(true_labels, pred_labels):
        y_true_bin = [0] * len(labels)
        y_pred_bin = [0] * len(labels)
        for i, label in enumerate(labels):
            if any([tl == label for tl in true_label]):
                y_true_bin[i] = 1
            if any([pl == label for pl in pred_label]):
                y_pred_bin[i] = 1
        y_true.append(y_true_bin)
        y_pred.append(y_pred_bin)

    report = classification_report(
        y_true, y_pred,
        output_dict=True,
        target_names=labels,
    )
    valid_f1_scores = []
    for label in labels:
        if report[label]['support'] > 0:
            valid_f1_scores.append(report[label]['f1-score'])
    return {
        'f1-score': round(np.mean(valid_f1_scores), 2),
        'categories': [{
            'category': label,
            'precision': round(report[label]['precision'], 2),
            'recall': round(report[label]['recall'], 2),
            'f1-score': round(report[label]['f1-score'], 2),
            'support': report[label]['support'],
        } for label in labels],
    }
