const canvas = document.getElementById('matrix-canvas');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const chars = "010101X$#!@ABCDEFGHIJKLMOPQRSTUVW";
const fontSize = 15;
const columns = canvas.width / fontSize;
const rows = canvas.height / fontSize;

const verticalDrops = Array(Math.floor(columns)).fill(1);
const horizontalDrops = Array(Math.floor(rows)).fill(1);

function drawMatrix() {
    ctx.fillStyle = "rgba(0, 0, 0, 0.15)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const colors = ["#ff0044", "#0088ff", "#00ff88"]; // Red, Blue, Green

    // Vertical
    verticalDrops.forEach((y, i) => {
        ctx.fillStyle = colors[Math.floor(Math.random() * 3)];
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, i * fontSize, y * fontSize);
        if (y * fontSize > canvas.height && Math.random() > 0.975) verticalDrops[i] = 0;
        verticalDrops[i]++;
    });

    // Horizontal
    horizontalDrops.forEach((x, i) => {
        ctx.fillStyle = colors[Math.floor(Math.random() * 3)];
        const text = chars[Math.floor(Math.random() * chars.length)];
        ctx.fillText(text, x * fontSize, i * fontSize);
        if (x * fontSize > canvas.width && Math.random() > 0.975) horizontalDrops[i] = 0;
        horizontalDrops[i]++;
    });
}

setInterval(drawMatrix, 60);

// Tab Switcher
function showTab(name) {
    document.querySelectorAll('.tab-view').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    document.getElementById(name + '-section').classList.add('active');
    event.target.classList.add('active');
}

// Result Meter Animation
window.onload = () => {
    const risk = document.body.getAttribute('data-risk-value');
    const fill = document.getElementById('risk-fill');
    if(fill) setTimeout(() => fill.style.width = risk + "%", 300);

    const tips = [
        "Phishing links often use '.tk' or '.xyz' domains.",
        "Check if the company name in the URL is misspelled.",
        "Banks will never ask for your PIN via a link."
    ];
    document.getElementById('dynamic-tips').innerHTML = tips.map(t => `<p>• ${t}</p>`).join('');
};

function hideModal(id) { document.getElementById(id).classList.remove('active'); }