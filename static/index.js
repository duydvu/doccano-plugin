let lock = false;

function createSampleProject(e) {
    e.preventDefault();
    if (lock) {
        return;
    }
    lock = true;
    const projectId = document.getElementById('projectId').value;
    const start = parseInt(document.getElementById('start').value) - 1;
    const end = parseInt(document.getElementById('end').value);
    const sampleSize = parseInt(document.getElementById('sampleSize').value);
    const newProjectName = document.getElementById('newProjectName').value;
    const username = document.getElementById('username').value;

    document.getElementById('notify').innerHTML = 'Processing...';

    fetch('/api/sample', {
        method: 'POST',
        body: JSON.stringify({
            projectId,
            start,
            end,
            sampleSize,
            newProjectName,
            username,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            if ('error' in data) {
                throw new Error(data.error);
            }
            lock = false;
            document.getElementById('notify').innerHTML = `OK. Link <a href="${data['link']}">${data['link']}</a>`;
        })
        .catch((error) => {
            lock = false;
            document.getElementById('notify').innerHTML = error;
            console.log(error);
        })
}

document.getElementById('main-form').addEventListener('submit', createSampleProject, true);