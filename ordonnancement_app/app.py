from flask import Flask, render_template, request

app = Flask(__name__)

def schedule_multi_machine(method, jobs, n_machines):
    # Règles de priorité
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
    tft = 0
    tardy_jobs = 0
    flow_retard = 0

    for job in jobs:
        m = machines.index(min(machines))
        start = max(machines[m], job["arrival"])
        end = start + job["duration"]
        machines[m] = end

        completion = end
        flow_time = completion - job["arrival"]
        tft += flow_time

        if completion > job["due"]:
            tardy_jobs += 1
            flow_retard += flow_time

        gantt.append({
            "machine": m + 1,
            "job": job["name"],
            "start": start,
            "end": end,
            "duration": job["duration"]
        })

    cmax = max(machines)
    tt = tft / len(jobs)
    tar = tardy_jobs / len(jobs)
    tfr = flow_retard / tft if tft != 0 else 0

    return gantt, {
        "cmax": cmax,
        "tft": tft,
        "tt": round(tt, 2),
        "tar": round(tar, 2),
        "tfr": round(tfr, 2)
    }


@app.route("/", methods=["GET", "POST"])
def index():
    step = 1
    shop_type = method = None
    n_jobs = n_machines = None
    gantt = results = None

    if request.method == "POST":
        step = int(request.form["step"])

        if step >= 2:
            shop_type = request.form["shop_type"]

        if step >= 3:
            method = request.form["method"]
            n_jobs = int(request.form["n_jobs"])
            n_machines = int(request.form["n_machines"])

        if step == 4:
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

    return render_template(
        "index.html",
        step=step,
        shop_type=shop_type,
        method=method,
        n_jobs=n_jobs,
        n_machines=n_machines,
        gantt=gantt,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)