let lock = false;
let transform = {
    "<>": "tr",
    "children": [
        { "<>": "td", "html": "${category}" },
        { "<>": "td", "html": "${precision}" },
        { "<>": "td", "html": "${recall}" },
        { "<>": "td", "html": "${f1-score}" },
        { "<>": "td", "html": "${support}" },
    ],
};
let header = `
    <th>Category</th>
    <th>Precision</th>
    <th>Recall</th>
    <th>F1-score</th>
    <th>Support</th>
`

function createSampleProject(e) {
    e.preventDefault();
    if (lock) {
        return;
    }
    lock = true;
    const projectId = document.getElementById('projectId').value;

    document.getElementById('notify').innerHTML = 'Processing...';

    fetch('/api/evaluate?' + new URLSearchParams({
        projectId,
    }), {
        method: 'GET',
    })
        .then((response) => response.json())
        .then((data) => {
            if ('error' in data) {
                throw new Error(data.error);
            }
            lock = false;
            document.getElementById('notify').innerHTML = `<br/>F1-score: ${data['f1-score']}`;
            console.log(data)
            document.getElementById('result').innerHTML = header + json2html.transform(data['categories'], transform);
        })
        .catch((error) => {
            lock = false;
            document.getElementById('notify').innerHTML = error;
            document.getElementById('result').innerHTML = '';
            console.log(error);
        })
}

document.getElementById('main-form').addEventListener('submit', createSampleProject, true);