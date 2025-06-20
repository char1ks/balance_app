document.getElementById('fetchButton').addEventListener('click', async () => {
    const response = await fetch('/');
    const text = await response.text();
    const responsesDiv = document.getElementById('responses');
    responsesDiv.innerHTML += `<div>${text}</div>`;
});
