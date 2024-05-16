from flask import Flask, request, redirect, url_for, flash, send_file, session, render_template
import io
import csv
import os
import uuid
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = '123456789'

# Directory to store uploaded files temporarily
UPLOAD_FOLDER = '/tmp/'  # Set this to a suitable directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to delete old temporary files
def cleanup_old_files(directory, max_age_in_seconds):
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age_in_seconds:
                os.remove(file_path)

# Your existing function create_port_csv
def create_port_csv(input_file, output_file, maas_ng_ip, maas_ng_fqdn, selected_hostnames=None):
    port_mappings = {
        "exporter_aes": {
            "src": [("TCP", "22"), ("ICMP", "ping"), ("TCP", "443"), ("SSL", "443")],
            "dst": [("UDP", "514"), ("TCP", "514"), ("UDP", "162")],
        },
        "exporter_gateway": {
            "src": [("UDP", "161"), ("TCP", "22"), ("ICMP", "ping")],
            "dst": [("UDP", "162")],
        },
        "exporter_ams": {
            "src": [("TCP", "22"), ("UDP", "161"), ("TCP", "8443"), ("ICMP", "ping"), ("SSL", "8443")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_sm": {
            "src": [("TCP", "22"), ("ICMP", "ping")],
            "dst": [("UDP", "162")],
        },
        "exporter_avayasbc": {
            "src": [("TCP", "22"), ("UDP", "161"), ("TCP", "443"), ("ICMP", "ping"), ("SSL", "443")],
            "dst": [("UDP", "162"), ("UDP", "514"), ("TCP", "514")],
        },
        "exporter_aaep": {
            "src": [("TCP", "22"), ("TCP", "5432"), ("UDP", "161"), ("TCP", "443"), ("ICMP", "ping"), ("SSL", "443")],
            "dst": [("UDP", "162"), ("UDP", "514"), ("TCP", "514")],
        },
        "exporter_mpp": {
            "src": [("TCP", "22"), ("ICMP", "ping")],
            "dst": [],
        },
        "exporter_windows": {
            "src": [("TCP", "9182"), ("ICMP", "ping")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_linux": {
            "src": [("TCP", "22"), ("ICMP", "ping")],
            "dst": [],
        },
        "exporter_ipo": {
            "src": [("TCP", "22"), ("TCP", "8443"), ("UDP", "161")],
            "dst": [("UDP", "162"), ("UDP", "514"), ("TCP", "514")],
        },
        "exporter_iq": {
            "src": [("TCP", "22"), ("TCP", "443"), ("ICMP", "ping")],
            "dst": [],
        },
        "exporter_weblm": {
            "src": [("TCP", "22"), ("TCP", "8443"), ("ICMP", "ping"), ("SSL", "8443")],
            "dst": [],
        },
        "exporter_aacc": {
            "src": [("TCP", "9182"), ("TCP", "443"), ("ICMP", "ping"), ("SSL", "443")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_wfodb": {
            "src": [("TCP", "1433"), ("TCP", "9182"), ("ICMP", "ping")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_verint": {
            "src": [("TCP", "9182"), ("ICMP", "ping"), ("TCP", "443"), ("ICMP", "ping"), ("SSL", "443")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_network": {
            "src": [("UDP", "161"), ("ICMP", "ping")],
            "dst": [("UDP", "162"), ("UDP", "514"), ("TCP", "514")],
        },
        "exporter_tcti": {
            "src": [("TCP", "8080"), ("ICMP", "ping")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_callback": {
            "src": [("TCP", "1433"), ("ICMP", "ping")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_nuancelm": {
            "src": [("TCP", "9182"), ("TCP", "27000"), ("ICMP", "ping")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_jmx": {
            "src": [("TCP", "7080"), ("ICMP", "ping")],
            "dst": [],
        },
        "exporter_breeze": {
            "src": [("TCP", "22"), ("ICMP", "ping"), ("SSL", "443")],
            "dst": [("UDP", "162"), ("UDP", "514"), ("TCP", "514")],
        },
        "exporter_acm": {
            "src": [("TCP", "22"), ("TCP", "5022"), ("TCP", "443"), ("UDP", "161"), ("ICMP", "ping"), ("SSL", "443")],
            "dst": [("UDP", "514"), ("TCP", "514"), ("UDP", "162")],
        },
        "exporter_vmware": {
            "src": [("TCP", "22"), ("ICMP", "PING"), ("TCP", "443")],
            "dst": [],
        },
        "exporter_kafka": {
            "src": [("TCP", "9092")],
            "dst": [],
        },
        "exporter_drac": {
            "src": [("TCP", "22"), ("ICMP", "PING"), ("UDP", "161")],
            "dst": [("UDP", "162"), ("UDP", "514"), ("TCP", "514")],
        },
        "exporter_pfsense": {
            "src": [("TCP", "22"), ("ICMP", "PING"), ("UDP", "161")],
            "dst": [("UDP", "162"), ("UDP", "514"), ("TCP", "514")],
        },
        "exporter_aic": {
            "src": [("TCP", "9183"), ("ICMP", "ping"), ("SSL", "443")],
            "dst": [("UDP", "514"), ("TCP", "514")],
        },
        "exporter_voiceportal": {
            "src": [("TCP", "5432"), ("ICMP", "ping"), ("TCP", "443"), ("TCP", "22")],
            "dst": [],
        },
        "exporter_aam": {
            "src": [("ICMP", "ping"), ("TCP", "443"), ("TCP", "22"), ("UDP", "161"), ("SSL", "443")],
            "dst": [("UDP", "514"), ("TCP", "514"), ("UDP", "162")],
        },
        "exporter_pc5": {
            "src": [("ICMP", "ping"), ("TCP", "22")],
            "dst": [],
        },
        "exporter_audiocodes": {
            "src": [("ICMP", "ping"), ("TCP", "22"), ("UDP", "161"), ("SSL", "443")],
            "dst": [("UDP", "514"), ("TCP", "514"), ("UDP", "162"), ("SSL", "443")],
        },
        "exporter_redis": {
            "src": [("TCP", "6379")],
            "dst": [],
        },
       }

    unique_entries = set()

    reader = csv.DictReader(input_file)
    writer = csv.writer(output_file)
    writer.writerow(["Source_FQDN", "Source_IP_Address", "Destination_FQDN", "Destination_IP_Address", "Port"])

    for row in reader:
        target_fqdn = row["FQDN"]
        fqdn = row["FQDN"]
        if selected_hostnames is not None and fqdn not in selected_hostnames:
            continue
            
        ip = row["IP Address"]
        exporter_name_os = row["Exporter_name_os"]
        exporter_name_app = row["Exporter_name_app"]

        exporters = [exporter_name_os, exporter_name_app]

        for exporter in exporters:
            if exporter in port_mappings:
                for protocol, port in port_mappings[exporter]["src"]:
                    entry = (maas_ng_fqdn, maas_ng_ip, target_fqdn, ip, f"{protocol}: {port}")
                    if entry not in unique_entries:
                        writer.writerow(entry)
                        unique_entries.add(entry)

                for protocol, port in port_mappings[exporter]["dst"]:
                    entry = (target_fqdn, ip, maas_ng_fqdn, maas_ng_ip, f"{protocol}: {port}")
                    if entry not in unique_entries:
                        writer.writerow(entry)
                        unique_entries.add(entry)

@app.route("/", methods=["GET", "POST"])
def upload_csv():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected")
            return redirect(request.url)

        maas_ng_fqdn = request.form.get("maas_ng_fqdn")
        if not maas_ng_fqdn:
            flash("MaaS-NG FQDN is required")
            return redirect(request.url)
        
        maas_ng_ip = request.form.get("maas_ng_ip")
        if not maas_ng_ip:
            flash("MaaS-NG IP address is required")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)

        if file:
            filename = secure_filename(str(uuid.uuid4()) + '.csv')
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            session['file_path'] = file_path
            return redirect(url_for("process", maas_ng_ip=maas_ng_ip))

    return render_template("index.html")

@app.route("/process")
def process():
    maas_ng_ip = request.args.get("maas_ng_ip")
    file_path = session.get("file_path")

    if not file_path or not os.path.exists(file_path):
        flash("File not found. Please upload again.")
        return redirect(url_for("upload_csv"))

    hostnames = []
    with open(file_path, mode='r', encoding='utf-8') as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            hostnames.append(row["FQDN"])

    return render_template("process.html", hostnames=hostnames, maas_ng_ip=maas_ng_ip)

@app.route("/generate_output_csv", methods=["POST"])
def generate_output_csv():
    selected_hostnames = request.form.getlist("selected_hostnames")
    maas_ng_fqdn = request.form["maas_ng_fqdn"]
    maas_ng_ip = request.form["maas_ng_ip"]
    file_path = session.get("file_path")

    if not file_path or not os.path.exists(file_path):
        flash("File not found. Please upload again.")
        return redirect(url_for("upload_csv"))

    with open(file_path, mode='r', encoding='utf-8') as input_file, io.StringIO() as output_file:
        create_port_csv(input_file, output_file, maas_ng_ip, maas_ng_fqdn, selected_hostnames)
        
        output_file.seek(0)
        output_filename = secure_filename(str(uuid.uuid4()) + '_output.csv')
        output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        with open(output_file_path, 'w', encoding='utf-8') as final_output_file:
            final_output_file.write(output_file.getvalue())

        return send_file(output_file_path, as_attachment=True, download_name='output.csv')

# Run the Flask app
if __name__ == "__main__":
    # Cleanup old files every time the server starts
    cleanup_old_files(app.config['UPLOAD_FOLDER'], max_age_in_seconds=3600)  # 1 hour
    app.run(debug=True)
