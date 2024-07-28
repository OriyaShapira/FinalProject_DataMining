from flask import Flask, request, render_template

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    # Collecting form data
    manufactor = request.form['manufactor']
    model = request.form['model']
    year = request.form['year']
    hand = request.form['hand']
    gear = request.form['gear']
    capacity_Engine = request.form['capacity_Engine']
    engineType = request.form['Engine_type']
    km = request.form['km']
    currentOwnership = request.form['Current']
    area = request.form['area']
    city = request.form['city']

    # Optional dta fields
    color = request.form.get('color', '')
    previousOwnership = request.form.get('Previous', '')
    testYear = request.form.get('test-year', '')
    testMonth = request.form.get('test-month', '')
    description = request.form.get('Description', '')

    # Rendering the form data into the ad format
    ad_content = f"""
        <h2>Your car details are:</h2>
        <p><strong>{manufactor} {model} model {year}</strong></p>
        <p>Hand: {hand}</p>
        <p>Gear: {gear}</p>
        <p>Engine Capacity: {capacity_Engine}</p>
        <p>Engine Type: {engineType}</p>
        <p>Kilometers: {km}</p>
        <p>Area: {area}</p>
        <p>City: {city}</p>
        <p>Current Ownership: {currentOwnership}</p>
    """

    if previousOwnership: ad_content += f"<p>Previous Owner: {previousOwnership}</p>"
    if color: ad_content += f"<p>Color: {color}</p>"
    if testYear and testMonth: ad_content += f"<p>Test: {testMonth}/{testYear}</p>"
    if description: ad_content += f"<p>Description: {description}</p>"

    return render_template('index.html', prediction_text=ad_content)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
