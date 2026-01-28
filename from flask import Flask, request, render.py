from flask import Flask, request, render_template_string

app = Flask(__name__)

# ===================== ORDONNANCEMENT =====================
def schedule_multi_machine(method, jobs, n_machines):

    if method == "FIFO":
        jobs.sort(key=lambda x: x["arrival"])
    elif method == "SPT":
        jobs.sort(key=lambda x: x["duration"])
    elif method == "LPT":
        jobs.sort(key=lambda x: x["duration"], reverse=True)
    elif method == "EDD":
        jobs.sort(key=lambda x: x["due"])
    elif method == "WDD":
        jobs.sort(key=lambda x: x["due"] / x["weight"])

    machines = [0] * n_machines
    gantt = []
    tft = tardy = retard = 0

    for job in jobs:
        m = machines.index(min(machines))
        start = max(machines[m], job["arrival"])
        end = start + job["duration"]
        machines[m] = end

        flow_time = end - job["arrival"]
        tft += flow_time

        if end > job["due"]:
            tardy += 1
            retard += flow_time

        gantt.append({
            "machine": m + 1,
            "job": job["name"],
            "start": start,
            "duration": job["duration"]
        })

    cmax = max(machines)

    return gantt, {
        "cmax": cmax,
        "tft": tft,
        "tt": round(tft / len(jobs), 2),
        "tar": round(tardy / len(jobs), 2),
        "tfr": round(retard / tft, 2) if tft else 0
    }

# ===================== PAGE UNIQUE =====================
HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Ordonnancement Multi-Machines</title>

<style>
body { font-family: Arial; padding: 20px; background: #f4f6fb; }
h1 { text-align: center; }
form { background: white; padding: 20px; border-radius: 12px; }
input, select { margin: 5px; padding: 6px; }
button { padding: 10px; background: gold; border: none; font-weight: bold; }

.gantt-row { display: flex; margin-top: 10px; }
.machine { width: 120px; font-weight: bold; }
.timeline {
    flex: 1;
    height: 40px;
    background: #ddd;
    border-radius: 10px;
    position: relative;
}
.task {
    position: absolute;
    height: 100%;
    background: gold;
    border-radius: 10px;
    text-align: center;
    line-height: 40px;
    font-weight: bold;
}
</style>
</head>

<body>

<h1>📅 Ordonnancement Multi-Machines</h1>

<form method="POST">
Méthode :
<select name="method">
    <option>FIFO</option>
    <option>SPT</option>
    <option>LPT</option>
    <option>EDD</option>
    <option>WDD</option>
</select>

Jobs : <input type="number" name="n_jobs" value="3" required>
Machines : <input type="number" name="n_machines" value="2" required>

<hr>

{% for i in range(3) %}
<b>Job {{ i+1 }}</b><br>
Arrivée <input name="arrival_{{i}}" value="0">
Durée <input name="duration_{{i}}" value="4">
Due <input name="due_{{i}}" value="6">
Poids <input name="weight_{{i}}" value="1"><br>
{% endfor %}

<br>
<button>Simuler</button>
</form>

{% if results %}
<h2>📊 Résultats</h2>
<ul>
<li>Cmax : {{ results.cmax }}</li>
<li>TFT : {{ results.tft }}</li>
<li>TT : {{ results.tt }}</li>
<li>TAR : {{ results.tar }}</li>
<li>TFR : {{ results.tfr }}</li>
</ul>

<h2>🧩 Diagramme de Gantt</h2>

{% for m in range(n_machines) %}
<div class="gantt-row">
    <div class="machine">Machine {{ m+1 }}</div>
    <div class="timeline">
        {% for g in gantt if g.machine == m+1 %}
        <div class="task"
             data-start="{{ g.start }}"
             data-duration="{{ g.duration }}"
             data-cmax="{{ results.cmax }}">
            {{ g.job }}
        </div>
        {% endfor %}
    </div>
</div>
{% endfor %}
{% endif %}

<script>
document.querySelectorAll(".task").forEach(task => {
    const start = task.dataset.start;
    const duration = task.dataset.duration;
    const cmax = task.dataset.cmax;

    task.style.left = (start / cmax * 100) + "%";
    task.style.width = (duration / cmax * 100) + "%";
});
</script>

</body>
</html>
"""

# ===================== ROUTE =====================
@app.route("/", methods=["GET", "POST"])
def index():
    gantt = results = None
    n_jobs = n_machines = 0

    if request.method == "POST":
        method = request.form["method"]
        n_jobs = int(request.form["n_jobs"])
        n_machines = int(request.form["n_machines"])

        jobs = []
        for i in range(n_jobs):
            jobs.append({
                "name": f"J{i+1}",
                "arrival": int(request.form[f"arrival_{i}"]),
                "duration": int(request.form[f"duration_{i}"]),
                "due": int(request.form[f"due_{i}"]),
                "weight": int(request.form[f"weight_{i}"])
            })

        gantt, results = schedule_multi_machine(method, jobs, n_machines)

    return render_template_string(
        HTML,
        gantt=gantt,
        results=results,
        n_jobs=n_jobs,
        n_machines=n_machines
    )

if __name__ == "__main__":
    app.run(debug=True)
